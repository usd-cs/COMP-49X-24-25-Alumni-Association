"""
URL configuration for AlumniProject project.

The `urlpatterns` list routes URLs to views.
For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:
    path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:
    path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function:
    from django.urls import include, path
    2. Add a URL to urlpatterns:
    path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from social_tracker.views import user_login, home
from social_tracker import views

urlpatterns = [
    path("", home, name="home"),
    path("login", user_login, name="login"),
    path("admin/", admin.site.urls),
    path("get-posts/", views.get_posts_view, name="get-posts"),
    path("api/posts/list/", views.list_stored_posts, name="list-posts"),
    path('api/demographics/', views.demographics_view, name='api-demographics'),
    path("demographics/", views.demographics_page, name="demographics_page"),
    path("export-csv/", views.export_csv_view, name="export-csv"),
    path("save-access-token/", views.save_access_token, name="save-access-token"),
    path("demographics/", views.get_demographics, name="demographics"),
]
