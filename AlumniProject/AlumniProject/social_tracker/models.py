from django.db import models


class Post(models.Model):
    post_ID = models.AutoField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    post_link = models.CharField(max_length=100)
    num_likes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    num_shares = models.IntegerField(default=0)
    num_saves = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date_posted"]
        app_label = "social_tracker"