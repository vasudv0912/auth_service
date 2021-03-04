"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views


urlpatterns = [

	path('register/', views.Register.as_view(), name='Register'),
	path('login/', views.GetToken.as_view(), name='GetToken'),
	path('book/add', views.AddBook.as_view(), name='AddBook'),
    path('book/issue', views.IssueBook.as_view(), name='IssueBook'),
    path('book/edit', views.EditBook.as_view(), name='EditBook'),
    path('book/release', views.ReturnBook.as_view(), name='ReleaseBook'),

]
