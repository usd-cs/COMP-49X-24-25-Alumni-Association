from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone

from social_tracker.models import (
    Comment,
    InstagramUser,
    Post,
    InstagramAccount,
)
from social_tracker.utils.get_instagram_data import (
    get_comment_data,
    get_comments_helper,
    get_instagram_posts,
)


class CommentDataTests(TestCase):
    def setUp(self):
        self.account = InstagramAccount.objects.create(
            account_API_ID="fake_account",
            username="TestAccount",
        )

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comment_data_single_comment(self, mock_get):
        mock_comment_id = 12345  # int PK
        mock_post_id = "999"

        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {"data": [{"id": mock_comment_id}]}),
            Mock(
                status_code=200,
                json=lambda: {
                    "id": mock_comment_id,
                    "from": {"id": 111, "username": "test_user"},
                    "like_count": 2,
                    "text": "This is a comment!",
                    "timestamp": "2023-01-01T12:00:00+0000",
                    "replies": {"data": []},
                    "username": "test_user",
                    "parent_id": "",
                },
            ),
        ]

        Post.objects.create(
            instagram_account=self.account,
            post_link="https://example.com/post",
            post_API_ID=mock_post_id,
            date_posted=timezone.now(),
        )

        get_comment_data("fake_token", mock_post_id, self.account.account_API_ID)

        self.assertTrue(Comment.objects.filter(id=mock_comment_id).exists())
        self.assertTrue(InstagramUser.objects.filter(id=111).exists())

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comments_helper_reply_ids(self, mock_get):
        comment_id = 333
        user_id = 111
        post_id = "222"

        Post.objects.create(
            instagram_account=self.account,
            post_link="https://example.com/post",
            post_API_ID=post_id,
            date_posted=timezone.now(),
        )

        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": comment_id,
                "from": {"id": user_id, "username": "reply_user"},
                "like_count": 1,
                "text": "reply comment",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": [{"id": 666}]},
                "username": "reply_user",
                "parent_id": "",
            },
        )

        comment_obj, reply_ids = get_comments_helper(
            "fake_token",
            comment_id,
            post_id,
            self.account,
        )

        self.assertIsNotNone(comment_obj)
        self.assertEqual(comment_obj.id, comment_id)
        self.assertEqual(reply_ids, [666])

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_updates_existing_post(self, mock_get):
        media_resp = Mock(
            status_code=200,
            json=lambda: {
                "data": [
                    {
                        "id": "1",
                        "timestamp": "2023-01-01T12:00:00+0000",
                        "permalink": "http://example.com/post1",
                    }
                ]
            },
        )

        insights_resp = Mock(
            status_code=200,
            json=lambda: {
                "data": [
                    {"name": "likes", "values": [{"value": 99}]},
                    {"name": "comments", "values": [{"value": 9}]},
                    {"name": "saved", "values": [{"value": 5}]},
                    {"name": "shares", "values": [{"value": 2}]},
                ]
            },
        )

        caption_resp = Mock(status_code=200, json=lambda: {"caption": ""})
        comments_resp = Mock(status_code=200, json=lambda: {"data": []})

        mock_get.side_effect = [
            media_resp,  # /me/media
            insights_resp,  # insights
            caption_resp,  # caption
            comments_resp,  # first comments page (empty)
        ]

        res = get_instagram_posts("fake_token", "fake_account", num_posts=1)
        post = Post.objects.get(post_link="http://example.com/post1")

        self.assertEqual(post.num_likes, 99)
        self.assertEqual(res, "Posts processed successfully.")

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comment_data_no_comments(self, mock_get):
        mock_post_id = "abcde"
        mock_get.return_value = Mock(status_code=200, json=lambda: {"data": []})

        Post.objects.create(
            instagram_account=self.account,
            post_link="https://example.com/post",
            post_API_ID=mock_post_id,
            date_posted=timezone.now(),
        )

        get_comment_data("fake_token", mock_post_id, self.account.account_API_ID)
        self.assertFalse(Comment.objects.exists())
        self.assertFalse(InstagramUser.objects.exists())

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comment_data_api_error(self, mock_get):
        mock_post_id = "abcde"
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {"error": {"message": "Invalid token"}},
        )

        Post.objects.create(
            instagram_account=self.account,
            post_link="https://example.com/post",
            post_API_ID=mock_post_id,
            date_posted=timezone.now(),
        )

        get_comment_data("fake_token", mock_post_id, self.account.account_API_ID)
        self.assertFalse(Comment.objects.exists())
        self.assertFalse(InstagramUser.objects.exists())
