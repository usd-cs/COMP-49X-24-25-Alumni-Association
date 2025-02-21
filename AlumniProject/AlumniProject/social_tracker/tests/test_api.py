import unittest
from unittest.mock import patch, Mock
import sys
import os
import requests
from social_tracker.utils.get_instagram_data import get_instagram_posts
from social_tracker.models import Post

# Add the project root to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


class GetInstagramPostsTest(unittest.TestCase):
    """
    TestCase for the get_instagram_posts function.

    This class contains unit tests to verify the behavior of the get_instagram_posts function,
    including successful retrieval and processing of posts, handling no posts found, and API call failures.
    """

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_success(self, mock_get):
        """
        Test successful retrieval and processing of Instagram posts.
        """
        # Mock first API call fetching post IDs, links, and timestamps
        mock_response_1 = Mock()
        mock_response_1.json.return_value = {
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
        mock_response_1.status_code = 200

        # Mock second API call that fetches post metrics
        mock_response_2 = Mock()
        mock_response_2.json.return_value = {
            "data": [
                {"name": "likes", "values": [{"value": 10}]},
                {"name": "comments", "values": [{"value": 5}]},
                {"name": "saved", "values": [{"value": 3}]},
                {"name": "shares", "values": [{"value": 1}]},
            ]
        }
        mock_response_2.status_code = 200

        # Ensure requests.get() returns different responses for the two different URLs we use
        def side_effect(url, params):
            if "insights" in url:
                return mock_response_2  # Second request for insights
            return mock_response_1  # First request for posts

        mock_get.side_effect = side_effect

        result = get_instagram_posts("fake_access_token", num_posts=2)
        self.assertEqual(result, "Posts processed successfully.")
        self.assertEqual(Post.objects.count(), 2)


    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_no_posts(self, mock_get):
        """
        Test handling of no posts found.
        """
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = get_instagram_posts("fake_access_token", num_posts=2)
        self.assertEqual(result, "No posts found.")
        self.assertEqual(Post.objects.count(), 0)


    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_instagram_posts_api_failure(self, mock_get):
        """
        Test handling of API call failure.
        """
        mock_get.side_effect = requests.exceptions.RequestException("API call failed")

        result = get_instagram_posts("fake_access_token", num_posts=2)
        self.assertIn("Error getting Instagram posts", result)
        self.assertEqual(Post.objects.count(), 0)



if __name__ == "__main__":
    unittest.main()
