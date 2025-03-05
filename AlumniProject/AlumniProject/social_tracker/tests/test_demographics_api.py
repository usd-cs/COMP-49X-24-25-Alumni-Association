from django.test import TestCase
from unittest.mock import patch, Mock
from social_tracker.models import Country, City, Age
from social_tracker.views import update_demographics
from social_tracker.utils.get_instagram_data import (
    get_country_demographics,
    get_city_demographics,
    get_age_demographics,
)


class DemographicsTestCase(TestCase):

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_country_demographics(self, mock_get):
        """Test fetching and storing country demographics from Instagram API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "total_value": {
                        "breakdowns": [
                            {
                                "results": [
                                    {"dimension_values": ["US"], "value": 500},
                                    {"dimension_values": ["AR"], "value": 300},
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        get_country_demographics("fake_token", "fake_account")

        self.assertEqual(Country.objects.count(), 2)
        self.assertTrue(
            Country.objects.filter(name="US", num_interactions=500).exists()
        )
        self.assertTrue(
            Country.objects.filter(name="AR", num_interactions=300).exists()
        )

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_city_demographics(self, mock_get):
        """Test fetching and storing city demographics from Instagram API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "total_value": {
                        "breakdowns": [
                            {
                                "results": [
                                    {
                                        "dimension_values": ["San Diego, California"],
                                        "value": 400,
                                    },
                                    {
                                        "dimension_values": ["Madison, Wisconsin"],
                                        "value": 250,
                                    },
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        get_city_demographics("fake_token", "fake_account")

        self.assertEqual(City.objects.count(), 2)
        self.assertTrue(
            City.objects.filter(
                name="San Diego, California", num_interactions=400
            ).exists()
        )
        self.assertTrue(
            City.objects.filter(
                name="Madison, Wisconsin", num_interactions=250
            ).exists()
        )

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_age_demographics(self, mock_get):
        """Test fetching and storing age demographics from Instagram API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "total_value": {
                        "breakdowns": [
                            {
                                "results": [
                                    {"dimension_values": ["18-24"], "value": 600},
                                    {"dimension_values": ["25-34"], "value": 450},
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        get_age_demographics("fake_token", "fake_account")

        self.assertEqual(Age.objects.count(), 2)
        self.assertTrue(
            Age.objects.filter(age_range="18-24", num_interactions=600).exists()
        )
        self.assertTrue(
            Age.objects.filter(age_range="25-34", num_interactions=450).exists()
        )

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_country_demographics_api_error(self, mock_get):
        """Test API failure in country demographics function."""
        mock_get.side_effect = Exception("API Error")

        result = get_country_demographics("fake_token", "fake_account")

        self.assertEqual(result, "Error getting Instagram posts: API Error")
        self.assertEqual(Country.objects.count(), 0)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_city_demographics_api_error(self, mock_get):
        """Test API failure in city demographics function."""
        mock_get.side_effect = Exception("API Error")

        result = get_city_demographics("fake_token", "fake_account")

        self.assertEqual(result, "Error getting Instagram posts: API Error")
        self.assertEqual(City.objects.count(), 0)

    @patch("social_tracker.utils.get_instagram_data.requests.get")
    def test_get_age_demographics_api_error(self, mock_get):
        """Test API failure in age demographics function."""
        mock_get.side_effect = Exception("API Error")

        result = get_age_demographics("fake_token", "fake_account")

        self.assertEqual(result, "Error getting Instagram posts: API Error")
        self.assertEqual(Age.objects.count(), 0)
    
    @patch("social_tracker.views.get_country_demographics")
    @patch("social_tracker.views.get_city_demographics")
    @patch("social_tracker.views.get_age_demographics")
    @patch("social_tracker.models.AccessToken.objects.get")
    def test_update_demographics_called(self, mock_get_access_token, mock_get_age, mock_get_city, mock_get_country):
        mock_access_token = Mock()
        mock_access_token.token = "fake_token"
        mock_access_token.account_id = "fake_account"
        mock_get_access_token.return_value = mock_access_token

        update_demographics()

        mock_get_country.assert_called_once_with(mock_access_token.token, mock_access_token.account_id)
        mock_get_city.assert_called_once_with(mock_access_token.token, mock_access_token.account_id)
        mock_get_age.assert_called_once_with(mock_access_token.token, mock_access_token.account_id)
