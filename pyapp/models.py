from __future__ import unicode_literals

from django.db import models


class ProjectStatus(models.Model):
    """
    Status of the analyzed project. Kind of status:
        - Initializing (Just the beginning)
        - Downloading repository...
        - Preparing... (Between downloading and analyzing, short period)
        - Analyzing...
        - Analyzed
        - Repository unavailable
        - Error, try again
    """
    projectUrl = models.URLField()
    totalFiles = models.IntegerField(default=0)
    analyzedFiles = models.IntegerField(default=0)
    status = models.CharField(max_length=128, default="Initializing")

    def __str__(self):
        return "%d-> %s: %d/%d. %s" % (self.id, self.projectUrl, self.totalFiles,
                                  self.analyzedFiles, self.status)


class Repository(models.Model):
    url = models.URLField(max_length=256)
    lastAnalysis = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%d-> %s: %s" % (self.id, self.url, self.lastAnalysis)

class Result(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    idiomName = models.CharField(max_length=128)
    line = models.IntegerField()
    file = models.CharField(max_length=512)
    author = models.EmailField()
    method = models.CharField(max_length=128, default="")

    def __str__(self):
        return "%d-> %s: %s %s:%d %s %s" % (self.id, self.repository, self.idiomName, self.file,
                                    self.line, self.author, self.method)


class User(models.Model):
    username = models.CharField(max_length=128, primary_key=True)
    email = models.EmailField()

    def __str__(self):
        return "%s %s" % (self.username, self.email)


class UserAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return "Analysis %s from repo <%s>" % (self.user, self.repository)


class FeedbackContact(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField()
    message = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Feedback from %s (%s) msg: '%s'" % (self.name, self.email, self.message)


class EmailNotify(models.Model):
    url = models.CharField(max_length=256) 
    email = models.EmailField()

    def __str__(self):
        return "Notificate to %s, path %s" % (self.email, self.url)
