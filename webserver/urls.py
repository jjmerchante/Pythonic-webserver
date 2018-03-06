"""webserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from pyapp import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^notificate', views.add_notification, name='add_notification'),
    url(r'^feedback', views.feedback, name='feedback'),
    url(r'^analyze-repos-user', views.analyze_user_projects, name='analyze_user_projects'),
    url(r'^analyze-repo', views.analyze_project, name='analyze_project'),
    url(r'^repos-user', views.repos_user, name='repos_user'),
    url(r'^status', views.get_status, name='get_status'),
    url(r'^repository/(.+)/(.+)$', views.show_results_repo, name='show_results_repo'),
    url(r'^user/(.+)$', views.show_results_user, name='show_results_user'),
    url(r'^idioms$', views.info_idioms, name='info_idioms'),
]
