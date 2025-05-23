import json
from unittest.mock import patch, MagicMock, call
from datetime import datetime

from django.test import TestCase
from social_tracker.models import InstagramAccount
from social_tracker.utils.get_instagram_data import get_instagram_stories


# Helper function to create mock API responses
def create_mock_response(status_code=200, json_data=None, text_data=""):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data if json_data is not None else {}
    mock_resp.text = text_data
    if status_code >= 400 and json_data is None:
        mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    elif status_code >= 400 and json_data is not None:
        if "error" not in json_data:
            json_data["error"] = {"message": "API Error", "code": status_code}
        mock_resp.json.return_value = json_data
    return mock_resp


class GetInstagramStoriesTests(TestCase):
    def setUp(self):
        # Create accounts the tests reference
        for acct in ("acct123", "acct456", "acct789", "acct000", "acct001", "acct002"):
            InstagramAccount.objects.create(account_API_ID=acct, username=acct)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_stories_success_one_story(self, mock_get):
        """Test successfully fetching one story with insights."""
        story_id = "11111"
        timestamp_str = "2024-04-24T10:00:00+0000"
        permalink = "http://example.com/story1"

        mock_stories_response = create_mock_response(
            status_code=200,
            json_data={
                "data": [
                    {"id": story_id, "timestamp": timestamp_str, "permalink": permalink}
                ]
            },
        )

        mock_insights_response = create_mock_response(
            status_code=200,
            json_data={
                "data": [
                    {"name": "reach", "values": [{"value": 150}]},
                    {"name": "navigation", "values": [{"value": 20}]},
                    {"name": "profile_visits", "values": [{"value": 5}]},
                ]
            },
        )

        mock_get.side_effect = [mock_stories_response, mock_insights_response]

        result = get_instagram_stories("fake_valid_token", "acct123")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        story_data = result[0]
        expected_date = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z").replace(
            tzinfo=None
        )

        self.assertEqual(story_data["story_API_ID"], story_id)
        self.assertEqual(story_data["story_link"], permalink)
        self.assertEqual(story_data["date_posted"], expected_date)
        self.assertEqual(story_data["num_views"], 150)
        self.assertEqual(story_data["num_profile_clicks"], 5)
        self.assertEqual(story_data["num_swipes_up"], 20)
        self.assertEqual(story_data["num_replies"], 0)

        expected_calls = [
            call(
                "https://graph.instagram.com/v19.0/me/stories",
                params={
                    "fields": "id,timestamp,permalink",
                    "access_token": "fake_valid_token",
                },
            ),
            call(
                f"https://graph.instagram.com/v19.0/{story_id}/insights",
                params={
                    "metric": "reach,navigation,profile_visits",
                    "period": "lifetime",
                    "access_token": "fake_valid_token",
                },
            ),
        ]
        mock_get.assert_has_calls(expected_calls)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_stories_no_active_stories(self, mock_get):
        """Test fetching when the API returns no active stories."""
        mock_get.return_value = create_mock_response(
            status_code=200, json_data={"data": []}
        )

        result = get_instagram_stories("fake_token", "acct456")

        self.assertIsInstance(result, list)
        self.assertEqual(result, [])
        mock_get.assert_called_once()

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_stories_api_error_on_stories_fetch(self, mock_get):
        """Test fetching when the /me/stories API call fails."""
        mock_get.return_value = create_mock_response(
            status_code=400,
            json_data={"error": {"message": "Invalid token", "code": 190}},
        )

        result = get_instagram_stories("invalid_token", "acct789")

        self.assertIsInstance(result, str)
        self.assertIn("API Error fetching stories (400)", result)
        self.assertIn("Invalid token", result)
        mock_get.assert_called_once()

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_stories_api_error_on_insights_fetch(self, mock_get):
        """Test fetching successfully but failing on the insights call."""
        story_id = "22222"
        timestamp_str = "2024-04-23T12:00:00+0000"
        permalink = "http://example.com/story2"

        mock_stories_response = create_mock_response(
            status_code=200,
            json_data={
                "data": [
                    {"id": story_id, "timestamp": timestamp_str, "permalink": permalink}
                ]
            },
        )
        mock_insights_response = create_mock_response(
            status_code=403,
            json_data={"error": {"message": "Permissions error", "code": 200}},
        )

        mock_get.side_effect = [mock_stories_response, mock_insights_response]

        result = get_instagram_stories("token_without_insights_perm", "acct000")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        story_data = result[0]
        expected_date = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z").replace(
            tzinfo=None
        )

        self.assertEqual(story_data["story_API_ID"], story_id)
        self.assertEqual(story_data["date_posted"], expected_date)
        self.assertEqual(story_data["num_views"], 0)
        self.assertEqual(story_data["num_profile_clicks"], 0)
        self.assertEqual(story_data["num_swipes_up"], 0)
        self.assertEqual(story_data["num_replies"], 0)

        self.assertEqual(mock_get.call_count, 2)

    def test_get_stories_missing_token(self):
        """Test calling the function with no access token."""
        result = get_instagram_stories(None, "acct001")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Access token is missing.")

        result_empty = get_instagram_stories("", "acct002")
        self.assertIsInstance(result_empty, str)
        self.assertEqual(result_empty, "Access token is missing.")
