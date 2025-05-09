from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone

from social_tracker.models import InstagramUser, Comment, Post, InstagramAccount
from social_tracker.utils.get_instagram_data import get_comments_helper


class UserModelTests(TestCase):
    """Tests around InstagramUser creation / updates via get_comments_helper."""

    def setUp(self):
        self.account = InstagramAccount.objects.create(
            account_API_ID="fake_account",
            username="UnitTestAcct",
        )

    def _make_post(self, pid="222"):
        return Post.objects.create(
            instagram_account=self.account,
            post_link=f"https://example.com/{pid}",
            post_API_ID=pid,
            date_posted=timezone.now(),
        )

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_user_created_with_comment(self, mock_get):
        self._make_post("222")

        comment_id = 333
        user_id = 111

        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": comment_id,
                "from": {"id": user_id, "username": "test_user"},
                "like_count": 3,
                "text": "Test comment",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": []},
                "username": "test_user",
                "parent_id": "",
            },
        )

        comment_obj, _ = get_comments_helper(
            "fake_token",
            comment_id,
            "222",
            self.account,
        )
        self.assertIsNotNone(comment_obj)
        self.assertTrue(InstagramUser.objects.filter(id=user_id).exists())

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_user_not_duplicated_on_second_comment(self, mock_get):
        self._make_post("222")

        user_id = 111

        # first comment
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": 333,
                "from": {"id": user_id, "username": "test_user"},
                "like_count": 1,
                "text": "hi",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": []},
                "username": "test_user",
                "parent_id": "",
            },
        )
        get_comments_helper("fake", 333, "222", self.account)

        # second comment by same user
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": 444,
                "from": {"id": user_id, "username": "test_user"},
                "like_count": 2,
                "text": "hello again",
                "timestamp": "2023-01-02T12:00:00+0000",
                "replies": {"data": []},
                "username": "test_user",
                "parent_id": "",
            },
        )
        get_comments_helper("fake", 444, "222", self.account)

        user = InstagramUser.objects.get(id=user_id)
        self.assertEqual(user.num_comments, 2)
        self.assertEqual(InstagramUser.objects.count(), 1)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_user_missing_data(self, mock_get):
        self._make_post("222")

        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": 555,
                "like_count": 0,
                "text": "anon",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": []},
                "parent_id": "",
            },
        )
        obj, _ = get_comments_helper("fake", 555, "222", self.account)
        self.assertIsNone(obj)
        self.assertFalse(InstagramUser.objects.exists())
        self.assertFalse(Comment.objects.exists())

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_api_error(self, mock_get):
        self._make_post("222")

        mock_get.return_value = Mock(
            status_code=400,
            json=lambda: {"error": {"message": "Invalid token"}},
        )
        obj, _ = get_comments_helper("fake", 666, "222", self.account)
        self.assertIsNone(obj)
        self.assertFalse(InstagramUser.objects.exists())
        self.assertFalse(Comment.objects.exists())
