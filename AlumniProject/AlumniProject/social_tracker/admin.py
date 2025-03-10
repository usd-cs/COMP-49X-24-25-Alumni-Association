# Register your models here.
from django.contrib import admin
from .models import Post


# register post
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "post_ID",
        "date_posted",
        "post_link",
        "num_likes",
        "num_comments",
    )
