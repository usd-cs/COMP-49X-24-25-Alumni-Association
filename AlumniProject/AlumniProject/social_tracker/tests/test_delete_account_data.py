from django.test import TestCase
from datetime import datetime
from social_tracker.models import (
    InstagramAccount,
    Post,
    Comment,
    InstagramUser,
    InstagramStory,
    Country,
    City,
    Age,
)
from social_tracker.utils.delete_account_data import delete_account_data


class DeleteAccountDataTests(TestCase):
    def setUp(self):
        # Create two accounts: one we'll delete data for, one we leave intact
        self.account = InstagramAccount.objects.create(
            account_API_ID="acct1",
            username="acct1",
        )
        self.other_account = InstagramAccount.objects.create(
            account_API_ID="acct2",
            username="acct2",
        )

        # Create child records for self.account
        now = datetime.now()
        Post.objects.create(
            instagram_account=self.account,
            date_posted=now,
            post_link="https://instagram.com/p/p1",
            num_likes=1,
            num_comments=1,
            num_shares=1,
            num_saves=1,
            post_API_ID="p1",
        )
        Comment.objects.create(
            instagram_account=self.account,
            comment_API_ID="c1",
            text="test comment",
            timestamp=now,
        )
        InstagramStory.objects.create(
            instagram_account=self.account,
            story_API_ID="s1",
            timestamp=now,
        )
        InstagramUser.objects.create(
            instagram_account=self.account,
            user_API_ID="u1",
            username="user1",
        )
        Country.objects.create(
            instagram_account=self.account,
            country="US",
            count=5,
        )
        City.objects.create(
            instagram_account=self.account,
            city="San Diego",
            count=3,
        )
        Age.objects.create(
            instagram_account=self.account,
            age_range="18-24",
            count=10,
        )

        # Create one post for the other account (to ensure it's not deleted)
        Post.objects.create(
            instagram_account=self.other_account,
            date_posted=now,
            post_link="https://instagram.com/p/other",
            num_likes=2,
            num_comments=2,
            num_shares=2,
            num_saves=2,
            post_API_ID="p2",
        )

    def test_nonexistent_account_raises(self):
        """Calling delete_account_data on a missing account should raise ValueError."""
        with self.assertRaises(ValueError) as cm:
            delete_account_data("does_not_exist")
        self.assertIn("does_not_exist", str(cm.exception))

    def test_delete_all_child_records(self):
        """All child records for the target account should be deleted."""
        msg = delete_account_data("acct1")
        self.assertEqual(
            msg,
            "All data for account 'acct1' has been deleted."
        )

        # Verify all related models for acct1 are empty
        self.assertEqual(Post.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(Comment.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(InstagramStory.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(InstagramUser.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(Country.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(City.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(Age.objects.filter(instagram_account=self.account).count(), 0)

        # Ensure other account's data remains untouched
        self.assertEqual(
            Post.objects.filter(instagram_account=self.other_account).count(),
            1
        )

    def test_return_message_includes_id(self):
        """The return message should include the account API ID."""
        result = delete_account_data("acct1")
        self.assertIn("acct1", result)
