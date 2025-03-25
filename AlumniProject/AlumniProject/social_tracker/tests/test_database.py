from datetime import datetime

from django.test import TestCase
from social_tracker.models import Post, Comment, InstagramUser
from django.contrib.auth.models import User


"""
Test cases for the database. Django TestCase creates a mock temporary
mock database for the tests.Therefore, none of these test values are being put
into the actual db.sqlite3 file that will be used for our live database.
We are using the Django built in User model as well as the Post model
defined in models.py.
"""


class DatabaseTest(TestCase):
    def setUp(self):
        Post.objects.create(
            post_link="http://www.sandiego.edu/p1",
            date_posted=datetime.now(),
            num_likes=100,
            num_comments=8,
            num_shares=10,
            num_saves=1,
            post_API_ID="12345",
        )
        Post.objects.create(
            post_link="http://www.sandiego.edu/p2",
        )
        User.objects.create(email="user@sandiego.edu", username="John User")
        User.objects.create(email="user2@sandiego.edu", username="Frank User")

         # Create test InstagramUsers
        InstagramUser.objects.create(id=1, username="john_doe", num_comments=5)
        InstagramUser.objects.create(id=2, username="jane_doe", num_comments=10)

        # Create test comments
        Comment.objects.create(
            id=1,
            text="Great post!",
            date_posted=datetime.now(),
            post_API_ID=Post.objects.get(post_API_ID="12345"),
            user_ID=InstagramUser.objects.get(id=1),
            username="john_doe",
        )
        Comment.objects.create(
            id=2,
            text="Nice content!",
            date_posted=datetime.now(),
            post_API_ID=Post.objects.get(post_API_ID="12345"),
            user_ID=InstagramUser.objects.get(id=2),
            username="jane_doe",
        )

    def test_post_creation(self):
        post = Post.objects.get(post_link="http://www.sandiego.edu/p1")
        self.assertEqual(post.num_likes, 100)

    def test_default_values(self):
        post = Post.objects.get(post_link="http://www.sandiego.edu/p2")
        self.assertEqual(post.num_likes, 0)
        self.assertEqual(post.num_comments, 0)
        self.assertEqual(post.num_shares, 0)
        self.assertEqual(post.num_saves, 0)
        self.assertEqual(post.post_API_ID, "")

    def test_date_posted(self):
        post = Post.objects.get(post_link="http://www.sandiego.edu/p1")
        self.assertIsNotNone(post.date_posted)

    def test_no_date_posted(self):
        post = Post.objects.get(post_link="http://www.sandiego.edu/p2")
        self.assertIsNone(post.date_posted)

    def test_post_deletion(self):
        post = Post.objects.get(post_link="http://www.sandiego.edu/p2")
        pre_num = Post.objects.count()
        post.delete()
        post_num = Post.objects.count()
        self.assertEqual(pre_num, 2)
        self.assertEqual(post_num, 1)

    def test_user_creation(self):
        user = User.objects.get(email="user@sandiego.edu")
        self.assertEqual(user.username, "John User")

    def test_user_deletion(self):
        user = User.objects.get(email="user2@sandiego.edu")
        pre_num = User.objects.count()
        user.delete()
        post_num = User.objects.count()
        self.assertEqual(pre_num, 2)
        self.assertEqual(post_num, 1)

    def test_instagram_user_creation(self):
        user = InstagramUser.objects.get(id=1)
        self.assertEqual(user.username, "john_doe")
        self.assertEqual(user.num_comments, 5)

    def test_instagram_user_deletion(self):
        user = InstagramUser.objects.get(id=2)
        pre_num = InstagramUser.objects.count()
        user.delete()
        post_num = InstagramUser.objects.count()
        self.assertEqual(pre_num, 2)
        self.assertEqual(post_num, 1)

    def test_comment_creation(self):
        comment = Comment.objects.get(id=1)
        self.assertEqual(comment.text, "Great post!")
        self.assertEqual(comment.user_ID.username, "john_doe")
        self.assertEqual(comment.post_API_ID.post_link, "http://www.sandiego.edu/p1")

    def test_comment_deletion(self):
        comment = Comment.objects.get(id=2)
        pre_num = Comment.objects.count()
        comment.delete()
        post_num = Comment.objects.count()
        self.assertEqual(pre_num, 2)
        self.assertEqual(post_num, 1)

    def test_comment_no_post(self):
        comment = Comment.objects.create(
            id=3,
            text="No post comment",
            date_posted=datetime.now(),
            post_API_ID=None,
            user_ID=InstagramUser.objects.get(id=1),
            username="john_doe",
        )
        self.assertIsNone(comment.post_API_ID)

    def test_comment_no_user(self):
        comment = Comment.objects.create(
            id=4,
            text="Anonymous comment",
            date_posted=datetime.now(),
            post_API_ID=Post.objects.get(post_API_ID="12345"),
            user_ID=None,
            username="anonymous",
        )
        self.assertIsNone(comment.user_ID)
