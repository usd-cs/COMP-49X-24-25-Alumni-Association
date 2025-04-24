from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("token/", views.token_landing, name="token_page"),
    path("save-token/", views.save_access_token, name="save_token"),
    path("get-posts/", views.get_posts_view, name="get_posts"),
    path("list-posts/", views.list_stored_posts, name="list_posts"),
    path("export-csv/", views.export_csv_view, name="export_csv"),
    path("demographics/", views.demographics_page, name="demographics"),
    path("demographics-data/", views.demographics_view, name="demographics_data"),
    path("days-of-week/", views.get_days_of_week, name="days_of_week"),
    path("account-info/", views.account_info, name="account-info"),
    path("stories-info/", views.stories_info, name="stories-info"),
    path("get-stories/", views.get_stories_view, name="get_stories"),
    path("post/<str:post_api_id>/", views.post_details, name="post_details"),
    path("instagram-link/<str:post_id>/", views.instagram_link, name="instagram_link"),
    path("post-comments/<str:post_id>/", views.post_comments, name="post_comments"),
]
