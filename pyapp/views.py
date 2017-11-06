from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.template import loader
from  django.core.exceptions import ObjectDoesNotExist

from pyapp.models import ProjectStatus, Repository, Result, User, UserAnalysis, FeedbackContact, EmailNotify

import analyzer

import urllib2
import json
import time
import threading
import re

from django.core.mail import EmailMessage


def index(request):
    """
    Home page of the project
    HTML with some forms to analyze your projects
    """
    context = {}
    return render(request, 'index.html', context)


def feedback(request):
    """
    Get -> Feedback web page
    Post -> Store feedback
    """
    if request.method == 'GET':
        context = {}
        return render(request, 'feedback.html', context)
    elif request.method == 'POST':
        name = request.POST.get("name", "Anonymus")
        email = request.POST.get("email", "")
        message = request.POST.get("message", "")
        if len(message) == 0:
            return HttpResponse("You must to send a message")
        fc = FeedbackContact(name=name, email=email, message=message)
        fc.save()
        return HttpResponse("Thank you for your feedback")
    else:
        return HttpResponseBadRequest("Bad request")


"""  REPOSITORY ANALYSIS - REQUEST """

def analyze_project(request):
    """
    Begin the analysis for a url project.
    Returns the redirect web page to see the status and the results
    """
    if request.method == 'POST':
        repo_url = request.POST.get('url')
        onlymodified = request.POST.get('onlymodified', 0)
        #print onlymodified
        try:
            onlymodified = int(onlymodified)
        except:
            onlymodified = 0
        if not repo_url:
            return HttpResponseBadRequest("No url provided")
        if not _validUrlGH(repo_url):
            return HttpResponseBadRequest("Bad url provided, check again")
        repoName = repo_url.split('/')[-1][:-4]
        userName = repo_url.split('/')[-2]
        print repo_url
        analyze_thread = threading.Thread(target=analyzer.analyze,
                                          kwargs={
                                            'repo_url': repo_url,
                                            'onlymodified': bool(onlymodified)
                                            })
        analyze_thread.start()
        return JsonResponse({'redirect': '/repository/%s/%s' % (userName, repoName)})
    return HttpResponseBadRequest("No url provided")

def get_status(request):
    """
    Returns the status analysis of a project
    See models.py file for more references
    """
    if request.method == 'GET':
        repo_url = request.GET.get('url')
        if not repo_url:
            return HttpResponseBadRequest("No url provided")
        try:
            proj = ProjectStatus.objects.get(projectUrl=repo_url)
        except:
            return JsonResponse({})
        return JsonResponse({'status': proj.status,
                             'totalFiles': proj.totalFiles,
                             'analyzedFiles': proj.analyzedFiles})
    return HttpResponseBadRequest("Bad request method")

def show_results_repo(request, user_repo, name_repo):
    """
    Returns the results for a single GitHub repository
    """
    url_repo = "https://github.com/%s/%s.git" % (user_repo, name_repo)
    data = _getDataRepoFromDB(url_repo)
    if data:
        analysis = analyzer.analyze_data(data)
        data['analysis'] = analysis
        context = {'results': json.dumps(data)}
    else:
        context = {'results': None}
    context['repository'] = url_repo
    return render(request, 'repo_results.html', context)

"""  GITHUB USER ANALYSIS - REQUEST """

def repos_user(request):
    """ Returns all the projects accessibles by github API """
    username = request.GET.get('username-gh')
    if username is None:
        return HttpResponseBadRequest("Username not found in request")
    json_response = _getUserReposFromGH(username)
    if json_response == None:
        return HttpResponseNotFound("Username not found in GitHub")
    return JsonResponse(json_response, safe=False)

def analyze_user_projects(request):
    """
    Begin the analysis for an array the projects and a username
    Returns the redirect web page to see the progress and results
    """
    if request.method == 'POST':
        repositories_str = request.POST.get('repos', [])
        username = request.POST.get('username', None)
        #TODO: onlymodified user repos
        if not username:
            return HttpResponseBadRequest('username not found in the request')

        mail = _getGitHubEmail(username)
        #print mail
        if not mail:
            return HttpResponseNotFound("Couldn't find an email to identify your commits")
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = User(username=username, email=mail)
            user.save()
        if repositories_str:
            repositories = json.loads(repositories_str)
            threads = []
            for repo in repositories:
                repositoryEntry, created = Repository.objects.get_or_create(url=repo)
                UserAnalysis.objects.get_or_create(user=user, repository=repositoryEntry)
                analyze_thread = threading.Thread(target=analyzer.analyze,
                                                  kwargs={
                                                    'repo_url': repo,
                                                    'onlymodified': False
                                                    },
                                                  name=repo)
                analyze_thread.start()
                threads.append(analyze_thread)
            url_notif = request.META['HTTP_HOST'] + '/user/' + username
            control = threading.Thread(target=analyzer.control_threads, kwargs={'threads': threads, 'url':url_notif})
            control.start()
        return JsonResponse({'redirect': '/user/%s' % username})
    return HttpResponseBadRequest('only POST methods')

def show_results_user(request, username):
    """
    Returns the results for a Github account
    """
    data_repos = _getDataUserFromDB(username)
    info_gh = _getInfoUserFromGH(username)
    #repos_user_gh = _getUserReposFromGH(username)
    if data_repos:
        data_analyzed = analyzer.analyze_data_b(data_repos)
        context = {'results': json.dumps(data_repos),
                   'resultsRaw': data_repos,
                   'analysis': data_analyzed,
                   'info_gh': info_gh}
    else:
        context = {'results': None,
                   'resultsRaw': None,
                   'analysis': None,
                   'info_gh': info_gh}
    context['username'] = username
    #TODO: Analyze data user
    return render(request, 'user_results.html', context)


def add_notification(request):
    """
    Send a notification when the analysis ends
    """
    if request.method == 'POST':
        email = request.POST.get('email', None)
        path = request.POST.get('path', None)
        if not email:
            return HttpResponseNotFound("No email found in the request")
        if not path:
            return HttpResponseNotFound("No analysis found in the request")
        url_notif = request.META['HTTP_HOST'] + path
        notif = EmailNotify(email=email, url=url_notif)
        notif.save()
        return HttpResponse("You will receive a link with the results when the application finishes analyzing")
    return HttpResponseBadRequest('only POST methods')

def get_raw_results_user(request, user):
    if not user:
        return HttpResponseNotFound("You must specify a user")
    user_entries = User.objects.filter(username=user)
    print user_entries
    for entry in user_entries:
        print entry.email
        res = Result.objects.filter(author=entry.email)
        print res
    return HttpResponse(Result.objects.all())


""" COMPLEMENTARY FUNCTIONS """

def _filter_json_data(jsondata):
    filtered = []
    for repo in jsondata:
        filtered.append({
            'name' : repo["full_name"],
            'fork' : repo["fork"],
            'language' : repo["language"],
            'html_url' : repo["html_url"]
        })
    return filtered

def _getGitHubEmail(username):
    url = "https://api.github.com/users/%s/events/public" % username
    print url
    location = ['payload', 'commits', 'array', 'author', 'email']
    email = ''
    try:
        response = urllib2.urlopen(url)
        jsondata = json.load(response)
        for event in jsondata:
            commits = event.get('payload', {}).get('commits', [])
            if len(commits) == 1:
                email = commits[0].get('author', {}).get('email')
            else:
                for commit in commits:
                    email = commit.get('author', {}).get('email')
                    if email: break
            if email:
                return email
    except urllib2.HTTPError as error:
        return error

def _getDataRepoFromDB(url):
    """Returns the data from the DB or None"""
    try:
        repo = Repository.objects.get(url=url)
    except ObjectDoesNotExist:
        return None

    data = {'idioms': {}, 'repository': repo.url, 'lastAnalysis': repo.lastAnalysis.strftime('%s')}
    res = Result.objects.filter(repository=repo)
    for item in res:
        if item.idiomName not in data['idioms']:
            data['idioms'][item.idiomName] = []
        idiomData = data['idioms'][item.idiomName]
        if item.method:
            idiomData.append({'file_name': item.file, 'line': item.line,
                              'author': item.author, 'method': item.method})
        else:
            idiomData.append({'file_name': item.file, 'line': item.line,
                              'author': item.author})
    return data

def _getDataUserFromDB(username):
    """ Return de data from the DB or None """

    user_analysis = UserAnalysis.objects.filter(user__username=username)
    #print user_analysis
    reposData = []
    for entry in user_analysis:
        repo = entry.repository
        data = {'idioms': {}, 'repository': repo.url, 'lastAnalysis': repo.lastAnalysis.strftime('%s')}
        res = Result.objects.filter(repository=repo)
        for item in res:
            if item.idiomName not in data['idioms']:
                data['idioms'][item.idiomName] = []
            idiomData = data['idioms'][item.idiomName]
            if item.method:
                idiomData.append({'file_name': item.file, 'line': item.line,
                                  'author': item.author, 'method': item.method})
            else:
                idiomData.append({'file_name': item.file, 'line': item.line,
                                  'author': item.author})
        try:
            proj = ProjectStatus.objects.get(projectUrl=repo.url)
            data['status'] = proj.status
        except:
            data['status'] = 'Unknow'

        reposData.append(data)

    return reposData


def _getInfoUserFromGH(username):
    #TODO delete this KEY
    #url = "https://api.github.com/users/%s?access_token=" % username
    url = "https://api.github.com/users/%s" % username
    try:
        response = urllib2.urlopen(url)
        jsondata = json.load(response)
    except urllib2.HTTPError as error:
        print "Error getting username {0}: {1}".format(username, error)
        jsondata = {}
    photo = jsondata.get("avatar_url", None)
    followers = jsondata.get("followers", None)
    repositories = jsondata.get("public_repos", None)
    return {"photo": photo, "followers": followers, "repositories": repositories}


def _getUserReposFromGH(username):
    #TODO delete this KEY
    #url = "https://api.github.com/users/%s/repos?access_token=" % username
    url = "https://api.github.com/users/%s/repos" % username
    try:
        response = urllib2.urlopen(url)
        jsondata = json.load(response)
    except urllib2.HTTPError as error:
        print "Error getting username {0}: {1}".format(username, error)
        return None
    json_filter = _filter_json_data(jsondata)
    return json_filter


def _validUrlGH(url):
    sp = url.split('/')
    if len(sp) != 5:
        return False
    expr = "^https\:\/\/github\.com\/(.+)\/(.+)\.git$"
    if not re.match(expr, url):
        return False
    return True
