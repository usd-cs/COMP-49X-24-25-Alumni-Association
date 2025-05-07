import json
from unittest.mock import patch, Mock
import requests
from django.test import TestCase, override_settings
from social_tracker.models import Post, InstagramAccount
from social_tracker.utils.get_instagram_data import get_instagram_posts
from social_tracker.views import instagram_link


class GetInstagramPostsTest(TestCase):
    """Unit‑tests for get_instagram_posts().  Uses a fresh DB per test."""

    def setUp(self):
        # username is mandatory on InstagramAccount
        self.account = InstagramAccount.objects.create(
            account_API_ID="fake_account",
            username="FakeAccount",
        )

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_success(self, mock_get):
        # 1st call → media list
        posts_payload = {
            "data": [
                {
                    "id": "1",
                    "timestamp": "2023-01-01T12:00:00+0000",
                    "permalink": "http://example.com/post1",
                },
                {
                    "id": "2",
                    "timestamp": "2023-01-02T12:00:00+0000",
                    "permalink": "http://example.com/post2",
                },
            ]
        }
        # 2nd call (insights) → metrics
        insights_payload = {
            "data": [
                {"name": "likes", "values": [{"value": 10}]},
                {"name": "comments", "values": [{"value": 5}]},
                {"name": "saved", "values": [{"value": 3}]},
                {"name": "shares", "values": [{"value": 1}]},
            ]
        }

        mock_media = Mock(status_code=200)
        mock_media.json.return_value = posts_payload
        mock_insights = Mock(status_code=200)
        mock_insights.json.return_value = insights_payload

        def side_effect(url, params):
            return mock_insights if "insights" in url else mock_media

        mock_get.side_effect = side_effect

        res = get_instagram_posts(
            "fake_access_token",
            self.account.account_API_ID,
            num_posts=2,
        )
        self.assertEqual(res, "Posts processed successfully.")
        self.assertEqual(Post.objects.count(), 2)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_no_posts(self, mock_get):
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = {"data": []}
        mock_get.return_value = mock_resp

        res = get_instagram_posts(
            "fake_access_token",
            self.account.account_API_ID,
            num_posts=2,
        )
        self.assertEqual(res, "No posts found.")
        self.assertEqual(Post.objects.count(), 0)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("boom")
        res = get_instagram_posts(
            "fake_access_token",
            self.account.account_API_ID,
            num_posts=2,
        )
        self.assertIn("Error getting Instagram posts", res)
        self.assertEqual(Post.objects.count(), 0)


@override_settings(LOGIN_URL="/")  # bypass @login_required in view
class InstagramLinkTests(TestCase):
    """Unit‑tests for instagram_link view helper."""

    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create(
            post_API_ID="999000999000",
            post_link="https://instagram.com/p/testpost",
        )

    def _dummy_request(self):
        r = Mock()
        r.user = Mock(is_authenticated=True)
        return r

    def test_valid_post(self):
        resp = instagram_link(self._dummy_request(), "999000999000")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.content),
            {"link": self.post.post_link},
        )

    def test_invalid_post(self):
        resp = instagram_link(self._dummy_request(), "does_not_exist")
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", json.loads(resp.content))

    @patch("social_tracker.models.Post.objects.get")
    def test_db_error(self, mock_get):
        mock_get.side_effect = Exception("db‑err")
        resp = instagram_link(self._dummy_request(), "999000999000")
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", json.loads(resp.content))
