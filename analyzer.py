import os
import sys
import re
import subprocess
from pythonic import completeAnalysis
from pyapp.models import ProjectStatus, Repository, Result, EmailNotify
from datetime import datetime
from  django.core.exceptions import ObjectDoesNotExist
import urllib2
import json
from django.db import transaction
import idiomsInfo
import time
from django.core.mail import EmailMultiAlternatives


def log(msg, level=0):
    """
    Print a message with differents levels of importance
    0: trace, 1: info, 2: warn, 3: error
    """
    color = ['\033[0m', '\033[94m', '\033[93m', '\033[91m']
    if level < 0  or level > 3: level = 0
    print color[level] + msg + '\033[0m'
    sys.stdout.flush()


def isPythonFile(filepath):
    """
    Is the path passed a Python file?
    """
    isPython = False
    (root, ext) = os.path.splitext(filepath)
    if ext == '.py':
        isPython = True
    elif ext == '':
        with open(filepath, 'r') as file:
            isPython = bool(re.search('#!.*python', file.readline()))
    return isPython


def getPyFilesIn(in_dir):
    filesList = []
    for root, dirs, files in os.walk(in_dir):
        if re.search('\/.git\/', root):
            continue
        for name in files:
            filepath = os.path.join(root, name)
            if not os.path.islink(filepath) and isPythonFile(filepath):
                filesList.append(filepath)
    return filesList


def downloadRepo(url, dir_dwnld):
    """
    Download the repository url to the dirRepo directory.
    The url must be in format https://github.com/user/repository.git
    If the repository is downloaded return True, otherwise, False
    """
    if not os.path.exists(dir_dwnld):
        try:
            os.mkdir(dir_dwnld)
        except OSError as e:
            raise Exception("Cannot clone into {0}: {1}".format(dir_dwnld, e))

    repoName = url.split('/')[-1][:-4]
    userName = url.split('/')[-2]
    clonedName = dir_dwnld + '/' + userName + "-" + repoName
    urlInfoRepo = "https://api.github.com/repos/%s/%s" % (userName, repoName)
    response = callGitHubAPI(urlInfoRepo)
    if response.get("private", True):
        return False
    if os.path.exists(clonedName):
        log("---WARNING---: {0}: repository already exists".format(clonedName), 2)
    else:
        ret = os.system('git clone --depth 1 {0} {1}'.format(url, clonedName))
        if ret == 0:
            log("{0}: Downloaded repository".format(clonedName), 1)
        else:
            log("Problems downloading the repository", 2)
            return False
    return True


def analyze(repo_url, onlymodified=False):
    """
    - Guiven a url for a GitHub repository analyze it and returns an object.
    - url must be in format https://github.com/user/repository.git
    - DELETe all the previuos results
    """
    clone_location = '/tmp/repositories'

    ProjectStatus.objects.filter(projectUrl=repo_url).delete()
    repoEntryDB = ProjectStatus(projectUrl=repo_url, status="Downloading repository...")
    repoEntryDB.save()
    if not downloadRepo(repo_url, clone_location):
        repoEntryDB.status = "Repository unavailable"
        repoEntryDB.save()
        return

    repoEntryDB.status = "Preparing..."
    repoEntryDB.save()
    repo_name = repo_url.split('/')[-1][:-4]
    user_name = repo_url.split('/')[-2]
    cloned_name = user_name + "-" + repo_name

    python_files = getPyFilesIn(clone_location + '/' + cloned_name)
    if onlymodified == 1:
        python_files = filter_files(python_files)
    total_files = len(python_files)
    files_done = 0
    ret_data = {
                "repository": repo_url,
                "idioms": {},
                "antiidioms": {}
              }

    repoEntryDB.status = "Analyzing..."
    repoEntryDB.totalFiles = total_files
    repoEntryDB.save()
    for file_name in python_files:
        print "ANALYZING %s" % file_name
        try:
            (results, resultsAnti) = completeAnalysis(file_name)
        except Exception as e:
            log("******" + str(e) + "******", 3)
            continue
        abbrFileName = file_name.split(clone_location + '/' + cloned_name)[1]
        for idiom in results:
            if not idiom.name in ret_data['idioms']:
                ret_data['idioms'][idiom.name] = []
            actualIdiom = ret_data['idioms'][idiom.name]
            for idiomItem in idiom.where:
                idiomItem['file_name'] = abbrFileName
                actualIdiom.append(idiomItem)

        for idiomanti in resultsAnti:
            if not idiomanti.name in ret_data['antiidioms']:
                ret_data['antiidioms'][idiomanti.name] = []
            actualIdiom = ret_data['antiidioms'][idiomanti.name]
            for idiomItem in idiomanti.where:
                idiomItem['file_name'] = abbrFileName
                actualIdiom.append(idiomItem)
        files_done += 1
        porcentage = (float(files_done)/total_files)*100
        repoEntryDB.analyzedFiles = files_done
        repoEntryDB.save()
        print "{0}% completed. {1}/{2} files.".format(porcentage, files_done, total_files)

    #analysisResults = analyze_idioms(ret_data)
    repoEntryDB.status = "Analyzed"
    repoEntryDB.save()

    saveAnalysis(ret_data)

    return ret_data

@transaction.atomic
def saveAnalysis(data):
    try:
        repoEntry = Repository.objects.get(url=data['repository'])
    except ObjectDoesNotExist:
        repoEntry = Repository(url=data['repository'])
    repoEntry.save() # update date and time

    # delete previous analysis and store the new one
    Result.objects.filter(repository=repoEntry).delete()
    for idiom in data["idioms"]:
        for item in data["idioms"][idiom]:
            res = Result(repository=repoEntry, idiomName=idiom, line=item['line'],
                         file=item['file_name'], author=item['author'], method=item.get('method', ''))
            res.save()


def analyze_data(data):
    """
    Make an analysis about de idioms and return some marks
    """
    beginner_list = idiomsInfo.new_beginner_list()
    intermediate_list = idiomsInfo.new_itermediate_list()
    advanced_list = idiomsInfo.new_advanced_list()

    for idiom in beginner_list:
        idiom["times"] = len(data['idioms'].get(idiom["name"], []))

    for idiom in intermediate_list:
        idiom["times"] = len(data['idioms'].get(idiom["name"], []))

    for idiom in advanced_list:
        idiom["times"] = len(data['idioms'].get(idiom["name"], []))

    return {'beginner': beginner_list,
            'intermediate': intermediate_list,
            'advanced': advanced_list}

def analyze_data_b(repositories_data):
    """
    Make an analysis about de idioms and return some marks
    """
    beginner_list = idiomsInfo.new_beginner_list()
    intermediate_list = idiomsInfo.new_itermediate_list()
    advanced_list = idiomsInfo.new_advanced_list()

    analysis_return = {
        "beginner": {
    		"total": 0,
    		"found": 0,
    		"know": [],
            "learn": []
    	}, "intermediate": {
    		"total": 0,
    		"found": 0,
    		"know": [],
            "learn": []
    	}, "advanced": {
    		"total": 0,
    		"found": 0,
    		"know": [],
            "learn": []
    	}}
    # count each idioms
    for repo_data in repositories_data:
        for idiom in beginner_list:
            idiom["times"] += len(repo_data['idioms'].get(idiom["name"], []))
        for idiom in intermediate_list:
            idiom["times"] += len(repo_data['idioms'].get(idiom["name"], []))
        for idiom in advanced_list:
            idiom["times"] += len(repo_data['idioms'].get(idiom["name"], []))
    # split in know and learn idioms
    analysis_return["beginner"]["know"] = [idiom for idiom in beginner_list if idiom["times"] > 0]
    analysis_return["beginner"]["learn"] = [idiom for idiom in beginner_list if idiom["times"] == 0]
    analysis_return["intermediate"]["know"] = [idiom for idiom in intermediate_list if idiom["times"] > 0]
    analysis_return["intermediate"]["learn"] = [idiom for idiom in intermediate_list if idiom["times"] == 0]
    analysis_return["advanced"]["know"] = [idiom for idiom in advanced_list if idiom["times"] > 0]
    analysis_return["advanced"]["learn"] = [idiom for idiom in advanced_list if idiom["times"] == 0]
    #count idioms of each category
    analysis_return["beginner"]["total"] = len(beginner_list)
    analysis_return["intermediate"]["total"] = len(intermediate_list)
    analysis_return["advanced"]["total"] = len(advanced_list)
    analysis_return["beginner"]["found"] = len(analysis_return["beginner"]["know"])
    analysis_return["intermediate"]["found"] = len(analysis_return["intermediate"]["know"])
    analysis_return["advanced"]["found"] = len(analysis_return["advanced"]["know"])

    return analysis_return

def filter_files(files):
    currentDir = os.getcwd()
    new_list = []
    for filepath in files:
        fileName = filepath.split('/')[-1]
        fileLocation = '/'.join(filepath.split('/')[:-1])
        os.chdir(fileLocation)

        command = 'git log --oneline'.split(' ')
        command.append(fileName)
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE);
        (data, error) = proc.communicate()
        if len(data.splitlines()) > 1:
            new_list.append(filepath)
        os.chdir(currentDir)
    return new_list



def callGitHubAPI(url):
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as error:
        print error
        return {}
    return json.load(response)


def control_threads(threads, url):
    print url
    while len(threads) > 0:
        for th in threads:
            if not th.isAlive():
                print th.name, "STOPPED"
                ps = ProjectStatus.objects.get(projectUrl=th.name)
                if ps.status != "Analyzed" and ps.status != "Repository unavailable":
                    ps.status = "Error, try again"
                    ps.save()
                threads.remove(th)
            else:
                print th.name, "RUNNING"
        time.sleep(15) #TODO: Increment

    notifs = EmailNotify.objects.filter(url=url)
    for n in notifs:
        print n.email

        subject, from_email, to = 'Pythonic analysis', 'pythonicproject1@gmail.com', n.email
        text_content = 'You can see the results of the analysis following this link: ' + url
        html_content = 'You can see the results of the analysis following this link: ' + url
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    notifs.delete()
