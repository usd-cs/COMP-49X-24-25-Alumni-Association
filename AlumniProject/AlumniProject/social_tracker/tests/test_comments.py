from django.test import TestCase
from unittest.mock import patch, Mock
from django.utils import timezone
from social_tracker.models import Comment, User, Post
from social_tracker.utils.get_instagram_data import (
    get_comment_data,
    get_comments_helper,
    get_instagram_posts,
)


class CommentDataTests(TestCase):
    """
    Test case for the comment saving process, incolving the get_comment_data,
    get_comments_helper, and get_instagram_posts functions.

    This class contains unit tests to verify the behavior of the above
    functions including successful retrieval and processing of comments, handling
    reply ids, no comments found, updating an existing post, and errors.
    """

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comment_data_single_comment(self, mock_get):
        """
        Test case for a single comment found. Tests that the comment and
        user was created.
        """
        mock_comment_id = "12345"
        mock_post_id = "abcde"

        # First API call returns a single comment ID
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {"data": [{"id": mock_comment_id}]}),
            # Second call returns details for the comment
            Mock(
                status_code=200,
                json=lambda: {
                    "id": mock_comment_id,
                    "from": {"id": "user123", "username": "test_user"},
                    "like_count": 2,
                    "text": "This is a comment!",
                    "timestamp": "2023-01-01T12:00:00+0000",
                    "replies": {"data": []},
                    "username": "test_user",
                    "parent_id": "",
                },
            ),
        ]

        # Create a dummy post to satisfy post_id constraint
        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=mock_post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

        get_comment_data("fake_token", mock_post_id)

        self.assertTrue(Comment.objects.filter(id=mock_comment_id).exists())
        self.assertTrue(User.objects.filter(id="user123").exists())

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comments_helper_reply_ids(self, mock_get):
        """
        Test case for handling getting reply ids for a single comment. Tests
        that the id was successfully retrieved and saved under the comment object.
        """
        comment_id = "c1"
        user_id = "u1"
        post_id = "p1"

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
                "from": {"id": user_id, "username": "reply_user"},
                "like_count": 1,
                "text": "reply comment",
                "timestamp": "2023-01-01T12:00:00+0000",
                "replies": {"data": [{"id": "r1"}]},
                "username": "reply_user",
                "parent_id": "",
            },
        )

        comment_obj, reply_ids = get_comments_helper(
            "fake_token", comment_id, post_id=post_id
        )

        self.assertIsNotNone(comment_obj)
        self.assertEqual(comment_obj.id, comment_id)
        self.assertEqual(reply_ids, ["r1"])

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_updates_existing_post(self, mock_get):
        """
        Test handling updating an existing post when new comments are ound.
        """
        Post.objects.create(
            post_link="http://example.com/post1",
            post_API_ID="1",
            num_likes=1,
            num_comments=1,
            num_shares=1,
            num_saves=1,
            date_posted=timezone.now(),
        )

        mock_get.side_effect = [
            Mock(
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
            ),
            Mock(
                status_code=200,
                json=lambda: {
                    "data": [
                        {"name": "likes", "values": [{"value": 99}]},
                        {"name": "comments", "values": [{"value": 9}]},
                        {"name": "saved", "values": [{"value": 5}]},
                        {"name": "shares", "values": [{"value": 2}]},
                    ]
                },
            ),
        ]

        result = get_instagram_posts("fake_token", num_posts=1)

        post = Post.objects.get(post_link="http://example.com/post1")
        self.assertEqual(post.num_likes, 99)
        self.assertEqual(result, "Posts processed successfully.")

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comment_data_no_comments(self, mock_get):
        """
        Test handling comment data when no comments are found and ensures
        nothing is created.
        """
        mock_post_id = "abcde"

        mock_get.return_value = Mock(status_code=200, json=lambda: {"data": []})

        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=mock_post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

        get_comment_data("fake_token", mock_post_id)

        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_comment_data_api_error(self, mock_get):
        """
        Test handling comment data when there is an api error and ensures
        no comments or users are created,
        """
        mock_post_id = "abcde"

        mock_get.return_value = Mock(
            status_code=200, json=lambda: {"error": {"message": "Invalid token"}}
        )

        Post.objects.create(
            post_link="https://example.com/post",
            post_API_ID=mock_post_id,
            num_likes=0,
            num_comments=0,
            num_shares=0,
            num_saves=0,
            date_posted=timezone.now(),
        )

        get_comment_data("fake_token", mock_post_id)

        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)
