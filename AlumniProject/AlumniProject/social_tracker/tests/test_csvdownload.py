from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from social_tracker.models import Post
import csv
from io import StringIO


class CSVDownloadTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test posts using your existing test data style
        self.post1 = Post.objects.create(
            post_link="http://www.sandiego.edu/p1",
            date_posted=datetime.now(),
            num_likes=100,
            num_comments=8,
            num_shares=10,
            num_saves=1,
        )

        self.post2 = Post.objects.create(
            post_link="http://www.sandiego.edu/p2",
            date_posted=datetime.now(),
            num_likes=200,
            num_comments=15,
            num_shares=20,
            num_saves=5,
        )

    def test_download_csv_url_exists(self):
        """Test if the download URL is accessible"""
        response = self.client.get(reverse("social_tracker:download_csv"))
        self.assertEqual(response.status_code, 200)

    def test_download_csv_content_type(self):
        """Test if the response has correct content type"""
        response = self.client.get(reverse("social_tracker:download_csv"))
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="social_media_data.csv"',
        )

    def test_download_csv_content(self):
        """Test if CSV content is correct"""
        response = self.client.get(reverse("social_tracker:download_csv"))
        content = response.content.decode("utf-8")
        csvreader = csv.reader(StringIO(content))

        # Check headers
        headers = next(csvreader)
        expected_headers = [
            "Post ID",
            "Date Posted",
            "Post Link",
            "Likes",
            "Comments",
            "Shares",
            "Saves",
        ]
        self.assertEqual(headers, expected_headers)

        # Check data rows
        rows = list(csvreader)
        self.assertEqual(len(rows), 2)  # Should have 2 posts

        # Check first post data
        self.assertEqual(int(rows[0][0]), self.post1.post_ID)
        self.assertEqual(rows[0][2], self.post1.post_link)
        self.assertEqual(int(rows[0][3]), self.post1.num_likes)

    def test_empty_database(self):
        """Test downloading CSV with no data"""
        # Delete all posts
        Post.objects.all().delete()

        response = self.client.get(reverse("social_tracker:download_csv"))
        content = response.content.decode("utf-8")
        csvreader = csv.reader(StringIO(content))

        # Should still have headers
        headers = next(csvreader)
        self.assertTrue(headers)

        # But no data rows
        rows = list(csvreader)
        self.assertEqual(len(rows), 0)
