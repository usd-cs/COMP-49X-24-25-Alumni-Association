from django.test import TestCase, Client
from django.urls import reverse
from social_tracker.models import Post
from datetime import datetime, timedelta
import json

class ListStoredPostsTests(TestCase):
    def setUp(self):
        """Set up test data before each test method"""
        self.client = Client()
        self.url = reverse('list-posts')  # Uses the URL name from urls.py
        
        # Create test posts with different dates and engagement metrics
        self.post1 = Post.objects.create(
            date_posted=datetime(2024, 1, 1),
            post_link="https://instagram.com/p/test1",
            num_likes=100,
            num_comments=20,
            num_shares=5,
            num_saves=10
        )
        
        self.post2 = Post.objects.create(
            date_posted=datetime(2024, 2, 1),
            post_link="https://instagram.com/p/test2",
            num_likes=50,
            num_comments=10,
            num_shares=2,
            num_saves=5
        )
        
        self.post3 = Post.objects.create(
            date_posted=datetime(2024, 3, 1),
            post_link="https://instagram.com/p/test3",
            num_likes=200,
            num_comments=30,
            num_shares=15,
            num_saves=20
        )

    def test_get_all_posts(self):
        """Test retrieving all posts without filters"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 3)
        
    def test_empty_database(self):
        """Test response when database is empty"""
        Post.objects.all().delete()
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 0)
        
    def test_date_filtering(self):
        """Test date range filtering"""
        # Test date_from
        response = self.client.get(f"{self.url}?date_from=2024-02-01")
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2) 
        
        # Test date_to
        response = self.client.get(f"{self.url}?date_to=2024-02-01")
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)  
        
        # Test date range
        response = self.client.get(f"{self.url}?date_from=2024-02-01&date_to=2024-02-28")
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)  
        
    def test_engagement_filtering(self):
        """Test filtering by engagement metrics"""
        # Test min_likes
        response = self.client.get(f"{self.url}?min_likes=100")
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)  
        
        # Test min_comments
        response = self.client.get(f"{self.url}?min_comments=20")
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)  
        
        # Test multiple engagement filters
        response = self.client.get(f"{self.url}?min_likes=100&min_comments=30")
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)  
        
    def test_invalid_inputs(self):
        """Test handling of invalid input parameters"""
        # Test invalid date format
        response = self.client.get(f"{self.url}?date_from=invalid-date")
        self.assertEqual(response.status_code, 400)
        
        # Test invalid number format
        response = self.client.get(f"{self.url}?min_likes=not-a-number")
        self.assertEqual(response.status_code, 400)
        
    def test_response_structure(self):
        """Test the structure of the response JSON"""
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        # Check required fields
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('message', data)
        
        # Check post structure
        if data['data']:
            post = data['data'][0]
            self.assertIn('id', post)
            self.assertIn('date_posted', post)
            self.assertIn('post_link', post)
            self.assertIn('likes', post)
            self.assertIn('comments', post)
            self.assertIn('shares', post)
            self.assertIn('saves', post)
            
    def test_combined_filters(self):
        """Test combining multiple filter types"""
        response = self.client.get(
            f"{self.url}?date_from=2024-02-01&min_likes=100&min_comments=20"
        )
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)  # Should only return post3
        
    def test_no_matching_results(self):
        """Test response when filters match no posts"""
        response = self.client.get(f"{self.url}?min_likes=1000")
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 0)