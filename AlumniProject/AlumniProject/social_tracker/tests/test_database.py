from datetime import datetime

from django.test import TestCase
from social_tracker.models import Post
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
