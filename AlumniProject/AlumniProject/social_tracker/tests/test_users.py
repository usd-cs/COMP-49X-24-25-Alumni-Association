from django.test import TestCase
from unittest.mock import patch, Mock
from django.utils import timezone
from social_tracker.models import InstagramUser, Comment, Post
from social_tracker.utils.get_instagram_data import get_comments_helper


class UserModelTests(TestCase):
    """
    Test case for the user saving process, incolving the get_comments_helper
    function.

    This class contains unit tests to verify the behavior of the above
    function including successful retrieval and processing of users, handling
    duplicates, missing data, and errors.
    """

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_user_created_with_comment(self, mock_get):
        """
        Testing successful user creation once a comment is found.
        """
        comment_id = "333"
        user_id = "111"
        post_id = "222"

        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

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

        comment_obj, reply_ids = get_comments_helper("fake_token", comment_id, post_id)

        self.assertIsNotNone(comment_obj)
        self.assertTrue(InstagramUser.objects.filter(id=user_id).exists())

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_user_not_duplicated_on_second_comment(self, mock_get):
        """
        Testing that a user is not duplicated once a second comment made by
        the same user is found.
        """
        comment_id_1 = "333"
        comment_id_2 = "444"
        user_id = "111"
        post_id = "222"

        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

        # Create first comment with user
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": comment_id_1,
                "from": {"id": user_id, "username": "test_user"},
                "like_count": 1,
                "text": "First comment",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": []},
                "username": "test_user",
                "parent_id": "",
            },
        )
        get_comments_helper("fake_token", comment_id_1, post_id)

        # Save state after first comment
        user = InstagramUser.objects.get(id=user_id)
        self.assertEqual(user.num_comments, 1)

        # Second comment by same user
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": comment_id_2,
                "from": {"id": user_id, "username": "test_user"},
                "like_count": 2,
                "text": "Second comment",
                "timestamp": "2023-01-02T12:00:00+0000",
                "replies": {"data": []},
                "username": "test_user",
                "parent_id": "",
            },
        )
        get_comments_helper("fake_token", comment_id_2, post_id)

        # Check that user still exists and comment count incremented once
        user.refresh_from_db()
        self.assertEqual(user.num_comments, 2)
        self.assertEqual(InstagramUser.objects.count(), 1)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_user_missing_data(self, mock_get):
        """
        Testing that a user is not created if there is missing information
        in the API response that corresponds to user info.
        """
        comment_id = "333"
        post_id = "222"

        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

        # API response missing "from" and username
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": comment_id,
                "like_count": 1,
                "text": "No user",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": []},
                # "from" field is omitted entirely
                "parent_id": "",
            },
        )

        comment_obj, reply_ids = get_comments_helper("fake_token", comment_id, post_id)

        self.assertIsNone(comment_obj)
        self.assertEqual(InstagramUser.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comments_helper_handles_api_error(self, mock_get):
        """
        Testing that the API handles errors when getting comment response data
        and does not create any comments or users if encountering an error.
        """
        comment_id = "333"
        post_id = "222"

        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

        mock_get.return_value = Mock(
            status_code=400, json=lambda: {"error": {"message": "Invalid token"}}
        )

        comment_obj, reply_ids = get_comments_helper("fake_token", comment_id, post_id)

        self.assertIsNone(comment_obj)
        self.assertEqual(InstagramUser.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
