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
from social_tracker.views import user_login
from social_tracker import views


urlpatterns = [
    path("", views.token_landing, name="token_landing"),
    path("posts/", views.home, name="home"),
    path("login", user_login, name="login"),
    path("admin/", admin.site.urls),
    path("get-posts/", views.get_posts_view, name="get-posts"),
    path("get-stories/", views.get_stories_view, name="get-stories"),
    path("api/posts/list/", views.list_stored_posts, name="list-posts"),
    path("api/demographics/", views.demographics_view, name="api-demographics"),
    path("demographics/", views.demographics_page, name="demographics_page"),
    path("export-csv/", views.export_csv_view, name="export-csv"),
    path("save-access-token/", views.save_access_token, name="save-access-token"),
    path("demographics/", views.get_demographics, name="demographics"),
    path("token/", views.token_landing, name="token_page"),
    path("account-info/", views.account_info, name="account-info"),
    path("stories-info/", views.stories_info, name="stories-info"),
    path("api/post-comments/<str:post_id>/", views.post_comments, name="post_comments"),
    path(
        "api/instagram-link/<str:post_id>/", views.instagram_link, name="instagram_link"
    ),
    path("api/days-of-week/", views.get_days_of_week, name="days_of_week"),
    path("post-details/<str:post_api_id>/", views.post_details, name="post_details"),
    #path("oauth-reciever", views.oauth_reciever, name="oauth-receiver"),
]
