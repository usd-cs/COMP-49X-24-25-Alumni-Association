import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
from social_tracker.utils.get_instagram_data import get_instagram_posts
from social_tracker.models import Post
from django.utils import timezone

class GetInstagramPostsTest(unittest.TestCase):
    """
    TestCase for the get_instagram_posts function.
    
    This class contains unit tests to verify the behavior of the get_instagram_posts function,
    including successful retrieval and processing of posts, handling no posts found, and API call failures.
    """

    @patch('AlumniProject.social_tracker.utils.get_instagram_data.requests.get')
    def test_get_instagram_posts_success(self, mock_get):
        """
        Test successful retrieval and processing of Instagram posts.
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "1",
                    "timestamp": "2023-01-01T12:00:00+0000",
                    "permalink": "http://example.com/post1",
                    "like_count": 10,
                    "comments_count": 5
                },
                {
                    "id": "2",
                    "timestamp": "2023-01-02T12:00:00+0000",
                    "permalink": "http://example.com/post2",
                    "like_count": 20,
                    "comments_count": 10
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = get_instagram_posts("fake_access_token", num_posts=2)
        self.assertEqual(result, "Posts processed successfully.")
        self.assertEqual(Post.objects.count(), 2)

    @patch('AlumniProject.social_tracker.utils.get_instagram_data.requests.get')
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

    @patch('AlumniProject.social_tracker.utils.get_instagram_data.requests.get')
    def test_get_instagram_posts_api_failure(self, mock_get):
        """
        Test handling of API call failure.
        """
        mock_get.side_effect = requests.exceptions.RequestException("API call failed")

        result = get_instagram_posts("fake_access_token", num_posts=2)
        self.assertIn("Error getting Instagram posts", result)
        self.assertEqual(Post.objects.count(), 0)

if __name__ == '__main__':
    unittest.main()