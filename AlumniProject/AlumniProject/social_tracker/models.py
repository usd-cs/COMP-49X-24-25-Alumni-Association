from django.db import models


class InstagramAccount(models.Model):
    """
    Model representing one Instagram business/account.
    Deleting this will delete all related posts, comments, users, stories, etc.
    """

    account_API_ID = models.CharField(max_length=100, primary_key=True)
    username = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "social_tracker"


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

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,  # <-- allow null for now
        blank=True,
        related_name="posts",
    )
    post_ID = models.AutoField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    post_link = models.CharField(max_length=100)
    num_likes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    num_shares = models.IntegerField(default=0)
    num_saves = models.IntegerField(default=0)
    post_API_ID = models.CharField(max_length=100, default="", unique=True)
    caption = models.TextField(null=True)

    class Meta:
        ordering = ["-date_posted"]
        app_label = "social_tracker"


class InstagramUser(models.Model):
    """
    Model representing a user who makes comments.

    Attributes:
        id (IntegerField): The unique identifier for the user.
        username (CharField): The username of the user.
        num_comments (IntegerField): The total number of comments made by the user.
    """

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="instagram_users",
    )
    id = models.IntegerField(primary_key=True)
    username = models.TextField(default="")
    num_comments = models.IntegerField(default=0)
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["num_comments"]
        app_label = "social_tracker"


class Comment(models.Model):
    """
    Model representing a comment on a post.

    Attributes:
        id (IntegerField): The unique identifier for the comment.
        date_posted (DateTimeField): The time the comment was posted.
        num_likes (IntegerField): The number of likes the comment received.
        text (TextField): The content of the comment.
        post_API_ID (ForeignKey): A foreign key to the Post model, linking this comment to a post.
        user_ID (ForeignKey): A foreign key to the User model, linking the comment to a user.
        username (CharField): The username of the commenter.
        parent_ID (TextField): The ID of the parent comment if this is a reply, otherwise empty.
        replies (JSONField): A list of replies associated with this comment.
    """

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )
    id = models.IntegerField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    num_likes = models.IntegerField(default=0)
    text = models.TextField(default="")
    post_API_ID = models.ForeignKey(
        Post,
        to_field="post_API_ID",
        db_column="POST_API_ID",
        on_delete=models.CASCADE,
        null=True,
    )
    user_ID = models.ForeignKey(InstagramUser, on_delete=models.CASCADE, null=True)
    username = models.TextField(default="")
    parent_ID = models.TextField(default="", null=True)
    replies = models.JSONField(default=list)

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

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="countries",
    )
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

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cities",
    )
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

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="age_ranges",
    )
    age_range = models.TextField()
    num_interactions = models.IntegerField(default=0)

    class Meta:
        app_label = "social_tracker"


class InstagramStory(models.Model):
    """
    Model representing an Instagram story.

    Attributes:
        story_ID (AutoField): Unique identifier for the story.
        date_posted (DateTimeField): The date and time when the story was posted.
        story_link (CharField): A link to the story.
        num_views (IntegerField): The number of views the story has received.
        num_profile_clicks (IntegerField): The number of profile clicks from the story.
        num_replies (IntegerField): The number of replies to the story.
        num_swipes_up (IntegerField): The number of swipe-ups on the story.
        story_API_ID (CharField): A unique identifier for the story in an external API.
    """

    instagram_account = models.ForeignKey(
        InstagramAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stories",
    )
    story_ID = models.AutoField(primary_key=True)
    date_posted = models.DateTimeField(null=True)
    story_link = models.CharField(max_length=100)
    num_views = models.IntegerField(default=0)
    num_profile_clicks = models.IntegerField(default=0)
    num_replies = models.IntegerField(default=0)
    num_swipes_up = models.IntegerField(default=0)
    story_API_ID = models.CharField(max_length=100, default="", unique=True)

    class Meta:
        ordering = ["-date_posted"]
        app_label = "social_tracker"
