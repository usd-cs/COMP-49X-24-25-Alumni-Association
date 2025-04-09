from django.test import TestCase
from datetime import datetime, timezone

from social_tracker.models import Post
from social_tracker.utils.get_time_of_day_statistics import (
    get_two_hour_block,
    sort_by_block_order,
    get_avg_likes_by_time_block,
    get_avg_comments_by_time_block,
    get_avg_saves_by_time_block,
    get_avg_shares_by_time_block,
)


class TimeBlockTests(TestCase):
    """
    Unit tests for 2-hour block statistics on Instagram posts.
    """

    def setUp(self):
        """
        Set up test data with 3 posts across 2 different time blocks.
        """
        self.posts = [
            Post.objects.create(
                date_posted=datetime(2023, 1, 1, 1, 0, tzinfo=timezone.utc),  # 12am–2am
                num_likes=10,
                num_comments=2,
                num_saves=5,
                num_shares=1,
            ),
            Post.objects.create(
                date_posted=datetime(
                    2023, 1, 1, 13, 0, tzinfo=timezone.utc
                ),  # 12pm–2pm
                num_likes=30,
                num_comments=6,
                num_saves=2,
                num_shares=3,
            ),
            Post.objects.create(
                date_posted=datetime(
                    2023, 1, 1, 13, 30, tzinfo=timezone.utc
                ),  # 12pm–2pm
                num_likes=50,
                num_comments=8,
                num_saves=4,
                num_shares=5,
            ),
        ]

    def test_get_two_hour_block(self):
        """
        Test whether get_two_hour_block returns the correct block label.
        """
        block = get_two_hour_block(self.posts[0])
        self.assertEqual(block, "12am-2am")

        block = get_two_hour_block(self.posts[1])
        self.assertEqual(block, "12pm-2pm")

    def test_sort_by_block_order(self):
        """
        Test whether blocks are sorted correctly using sort_by_block_order.
        """
        unsorted = [{"block": "12pm-2pm"}, {"block": "12am-2am"}]
        sorted_blocks = sorted(unsorted, key=sort_by_block_order)
        self.assertEqual(sorted_blocks[0]["block"], "12am-2am")

    def test_avg_likes_by_time_block(self):
        """
        Test average number of likes calculated for each 2-hour block.
        """
        total, result = get_avg_likes_by_time_block()
        likes_dict = {entry["block"]: entry["avg_likes"] for entry in result}
        self.assertEqual(total, 3)
        self.assertEqual(likes_dict["12am-2am"], 10.0)
        self.assertEqual(likes_dict["12pm-2pm"], 40.0)

    def test_avg_comments_by_time_block(self):
        """
        Test average number of comments calculated for each 2-hour block.
        """
        total, result = get_avg_comments_by_time_block()
        comments_dict = {entry["block"]: entry["avg_comments"] for entry in result}
        self.assertEqual(total, 3)
        self.assertEqual(comments_dict["12am-2am"], 2.0)
        self.assertEqual(comments_dict["12pm-2pm"], 7.0)

    def test_avg_saves_by_time_block(self):
        """
        Test average number of saves calculated for each 2-hour block.
        """
        total, result = get_avg_saves_by_time_block()
        saves_dict = {entry["block"]: entry["avg_saves"] for entry in result}
        self.assertEqual(total, 3)
        self.assertEqual(saves_dict["12am-2am"], 5.0)
        self.assertEqual(saves_dict["12pm-2pm"], 3.0)

    def test_avg_shares_by_time_block(self):
        """
        Test average number of shares calculated for each 2-hour block.
        """
        total, result = get_avg_shares_by_time_block()
        shares_dict = {entry["block"]: entry["avg_shares"] for entry in result}
        self.assertEqual(total, 3)
        self.assertEqual(shares_dict["12am-2am"], 1.0)
        self.assertEqual(shares_dict["12pm-2pm"], 4.0)
