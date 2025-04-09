from django.test import TestCase, Client
from django.urls import reverse
from social_tracker.models import Post
from datetime import datetime
import json


class GetDaysOfWeekTests(TestCase):
    def setUp(self):
        """Set up test data before each test method"""
        self.client = Client()
        self.url = reverse("days_of_week")

        self.post1 = Post.objects.create(
            date_posted=datetime(2024, 4, 1),  # Monday
            post_link="https://instagram.com/p/mon",
            num_likes=100,
            num_comments=20,
            num_shares=5,
            num_saves=10,
            post_API_ID="111",
        )

        self.post2 = Post.objects.create(
            date_posted=datetime(2024, 4, 2),  # Tuesday
            post_link="https://instagram.com/p/tue",
            num_likes=60,
            num_comments=10,
            num_shares=3,
            num_saves=4,
            post_API_ID="222",
        )

        self.post3 = Post.objects.create(
            date_posted=datetime(2024, 4, 1),  # Monday again
            post_link="https://instagram.com/p/mon2",
            num_likes=50,
            num_comments=30,
            num_shares=10,
            num_saves=8,
            post_API_ID="333",
        )

    def test_response_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data["success"])

    def test_data_structure(self):
        """Test if the data dictionary includes all days and proper values"""
        response = self.client.get(self.url)
        data = json.loads(response.content)

        self.assertIn("data", data)
        self.assertEqual(set(data["data"].keys()), {
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        })

        monday_data = data["data"]["Monday"]
        self.assertEqual(len(monday_data), 5)

    def test_average_calculations(self):
        """Ensure averages are calculated correctly"""
        response = self.client.get(self.url)
        data = json.loads(response.content)

        monday_data = data["data"]["Monday"]
        self.assertEqual(monday_data[0], 2)  # count
        self.assertEqual(monday_data[1], 75.0)  # avg_likes
        self.assertEqual(monday_data[2], 25.0)  # avg_comments
        self.assertEqual(monday_data[3], 7.5)  # avg_shares
        self.assertEqual(monday_data[4], 9.0)  # avg_saves

    def test_empty_database(self):
        """Test response when no posts exist"""
        Post.objects.all().delete()
        response = self.client.get(self.url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        for day in data["data"].values():
            self.assertEqual(day, [0, 0, 0, 0, 0])

    def test_missing_date_posted(self):
        """Post with null date_posted are ignored"""
        Post.objects.create(
            date_posted=None,
            post_link="https://instagram.com/p/null",
            num_likes=100,
            num_comments=20,
            num_shares=5,
            num_saves=10,
            post_API_ID="444",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["Monday"][0], 2)

