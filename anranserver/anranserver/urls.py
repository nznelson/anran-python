"""anranserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from server import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', views.login_user),
    url(r'^users/', views.signup_user),
    url(r'^games/$', views.game),
    url(r'^games/(?P<game_id>.+)/join$', views.join_game),
    url(r'^games/(?P<game_id>.+)/move$', views.make_move),
    url(r'^games/(?P<game_id>.+)$', views.game_single),
]
