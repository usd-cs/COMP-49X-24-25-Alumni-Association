# test_api.py

from django.test import TestCase
from social_tracker.models import Post
from django.utils import timezone

class PostModelTest(TestCase):

    def setUp(self):
        self.post = Post.objects.create(
            date_posted=timezone.now(),
            post_link="http://example.com",
            num_likes=10,
            num_comments=5,
            num_shares=2,
            num_saves=3
        )

    def test_post_creation(self):
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.post_link, "http://example.com")
        self.assertEqual(self.post.num_likes, 10)
        self.assertEqual(self.post.num_comments, 5)
        self.assertEqual(self.post.num_shares, 2)
        self.assertEqual(self.post.num_saves, 3)

    def test_default_values(self):
        post = Post.objects.create(post_link="http://example.com")
        self.assertEqual(post.num_likes, 0)
        self.assertEqual(post.num_comments, 0)
        self.assertEqual(post.num_shares, 0)
        self.assertEqual(post.num_saves, 0)

    def test_ordering(self):
        post1 = Post.objects.create(date_posted=timezone.now(), post_link="http://example1.com")
        post2 = Post.objects.create(date_posted=timezone.now() + timezone.timedelta(days=1), post_link="http://example2.com")
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], post1)