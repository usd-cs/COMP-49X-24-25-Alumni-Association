from django.db import models


class Post(models.Model):
    post_ID = models.AutoField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    post_link = models.CharField(max_length=100)
    num_likes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    num_shares = models.IntegerField(default=0)
    num_saves = models.IntegerField(default=0)
    post_API_ID = models.IntegerField(default=None)

    class Meta:
        ordering = ["-date_posted"]
        app_label = "social_tracker"


class AccessToken(models.Model):
    token = models.TextField()

    def save(self, *args, **kwargs):
        # there can only be one access token at once
        if AccessToken.objects.exists() and not self.pk:
            AccessToken.objects.all().delete()
        super().save(*args, **kwargs)

    class Meta:
        app_label = "social_tracker"
