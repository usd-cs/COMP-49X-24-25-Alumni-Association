from django.db import models


class Post(models.Model):
    """
    Model representing a social media post.

    Attributes:
        post_ID (AutoField): Unique identifier for the post.
        date_posted (DateTimeField): The date and time when the post was made.
        post_link (CharField): A link to the post.
        num_likes (IntegerField): The number of likes the post has received.
        num_comments (IntegerField): The number of comments on the post.
        num_shares (IntegerField): The number of times the post has been shared.
        num_saves (IntegerField): The number of times the post has been saved.
        post_API_ID (CharField): A unique identifier for the post in an external API.
    """

    post_ID = models.AutoField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    post_link = models.CharField(max_length=100)
    num_likes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    num_shares = models.IntegerField(default=0)
    num_saves = models.IntegerField(default=0)
    post_API_ID = models.CharField(max_length=100, default="")

    class Meta:
        ordering = ["-date_posted"]
        app_label = "social_tracker"

class User(models.Model):
    user_ID = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100)
    num_comments = models.IntegerField(default=0)

    class Meta:
        ordering = ["num_comments"]
        app_label = "social_tracker"

class Comment(models.Model):
    comment_ID = models.IntegerField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    num_likes = models.IntegerField(default=0)
    text = models.TextField(default="")
    post_API_ID = models.ForeignKey(Post, to_field='post_API_ID', db_column='POST_API_ID', on_delete=models.CASCADE)
    user_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_ID = models.ForeignKey('self', null=True)

    class Meta:
        ordering = ["-date_posted"]
        app_label = "social_tracker"

class AccessToken(models.Model):
    """
    Model to store an access token for authentication.

    Attributes:
        token (TextField): The access token string.
        account_id (TextField): The account ID associated with the token.

    Methods:
        save: Ensures there is only one active access token at a time.
    """

    token = models.TextField()
    account_id = models.TextField(default="None")

    def save(self, *args, **kwargs):
        # There can only be one access token at a time
        if AccessToken.objects.exists() and not self.pk:
            AccessToken.objects.all().delete()
        super().save(*args, **kwargs)

    class Meta:
        app_label = "social_tracker"


class Country(models.Model):
    """
    Model representing a country and the number of interactions from that country.

    Attributes:
        name (TextField): The name of the country.
        num_interactions (IntegerField): The number of interactions from this country.
    """

    name = models.TextField()
    num_interactions = models.IntegerField(default=0)

    class Meta:
        app_label = "social_tracker"


class City(models.Model):
    """
    Model representing a city and the number of interactions from that city.

    Attributes:
        name (TextField): The name of the city.
        num_interactions (IntegerField): The number of interactions from this city.
    """

    name = models.TextField()
    num_interactions = models.IntegerField(default=0)

    class Meta:
        app_label = "social_tracker"


class Age(models.Model):
    """
    Model representing an age range and the number of interactions from that age group.

    Attributes:
        age_range (TextField): The age range
        num_interactions (IntegerField): The number of interactions from this age range.
    """

    age_range = models.TextField()
    num_interactions = models.IntegerField(default=0)

    class Meta:
        app_label = "social_tracker"


class Comment(models.Model):
    """
    Model representing a comment on a post.

    Attributes:
        id (TextField): The unique identifier for the comment.
        num_likes (IntegerField): The number of likes the comment received.
        username (TextField): The username of the commenter.
        user_id (TextField): The ID of the user who made the comment.
        replies (JSONField): A list of reply comment IDs associated with this comment.
        post_id (TextField): The ID of the Instagram post the comment is on.
        text (TextField): The content of the comment.
        timestamp (DateTimeField): The time the comment was posted.
        parent_id (TextField): The ID of the parent comment if this is a reply, otherwise empty.
    """

    id = models.TextField(primary_key=True)
    num_likes = models.IntegerField(default=0)
    username = models.TextField()
    user_id = models.TextField()
    replies = models.JSONField(default=list)
    post_id = models.TextField()
    text = models.TextField()
    timestamp = models.DateTimeField(null=True)
    parent_id = models.TextField(default="", null=True)

    class Meta:
        app_label = "social_tracker"


class User(models.Model):
    """
    Model representing a user who made one or more comments.

    Attributes:
        username (TextField): The username of the user.
        id (TextField): The unique identifier for the user (primary key).
        num_comments (IntegerField): The total number of comments made by the user.
    """

    username = models.TextField()
    id = models.TextField(primary_key=True)
    num_comments = models.IntegerField(default=0)

    class Meta:
        app_label = "social_tracker"
