from datetime import datetime

from django.test import TestCase

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
    """Tests for the delete_account_data() utility."""

    def setUp(self):
        # Two accounts: one to delete, one to keep
        self.account = InstagramAccount.objects.create(
            account_API_ID="acct1",
            username="acct1",
        )
        self.other_account = InstagramAccount.objects.create(
            account_API_ID="acct2",
            username="acct2",
        )

        now = datetime.now()

        # Child records linked to acct1
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
            id=1,
            text="test comment",
            date_posted=now,
        )
        InstagramStory.objects.create(
            instagram_account=self.account,
            story_API_ID="s1",
            date_posted=now,
        )
        InstagramUser.objects.create(
            instagram_account=self.account,
            id=1,
            username="user1",
        )
        Country.objects.create(
            instagram_account=self.account,
            name="US",
            num_interactions=5,
        )
        City.objects.create(
            instagram_account=self.account,
            name="San Diego",
            num_interactions=3,
        )
        Age.objects.create(
            instagram_account=self.account,
            age_range="18‑24",
            num_interactions=10,
        )

        # One post for the other account (should remain)
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
        """Calling delete_account_data on a missing account should raise."""
        with self.assertRaises(ValueError) as cm:
            delete_account_data("does_not_exist")
        self.assertIn("does_not_exist", str(cm.exception))

    def test_delete_all_child_records(self):
        """All child records for the target account should be deleted."""
        msg = delete_account_data("acct1")
        self.assertEqual(msg, "All data for account 'acct1' has been deleted.")

        # Everything for acct1 should be gone
        self.assertEqual(Post.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(
            Comment.objects.filter(instagram_account=self.account).count(), 0
        )
        self.assertEqual(
            InstagramStory.objects.filter(instagram_account=self.account).count(), 0
        )
        self.assertEqual(
            InstagramUser.objects.filter(instagram_account=self.account).count(), 0
        )
        self.assertEqual(
            Country.objects.filter(instagram_account=self.account).count(), 0
        )
        self.assertEqual(City.objects.filter(instagram_account=self.account).count(), 0)
        self.assertEqual(Age.objects.filter(instagram_account=self.account).count(), 0)

        # Data for the other account must still exist
        self.assertEqual(
            Post.objects.filter(instagram_account=self.other_account).count(),
            1,
        )

    def test_return_message_includes_id(self):
        """Return message should reference the deleted account id."""
        result = delete_account_data("acct1")
        self.assertIn("acct1", result)
