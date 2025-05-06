# delete_account_data.py

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


def delete_account_data(account_api_id):
    """
    Delete all data associated with the InstagramAccount identified by account_api_id.
    Does NOT delete the account itself—only its child records.
    Raises ValueError if the account doesn't exist.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_api_id)
    except InstagramAccount.DoesNotExist:
        raise ValueError(f"No InstagramAccount found for id '{account_api_id}'")

    # delete all related rows
    Post.objects.filter(instagram_account=account).delete()
    Comment.objects.filter(instagram_account=account).delete()
    InstagramStory.objects.filter(instagram_account=account).delete()
    InstagramUser.objects.filter(instagram_account=account).delete()
    Country.objects.filter(instagram_account=account).delete()
    City.objects.filter(instagram_account=account).delete()
    Age.objects.filter(instagram_account=account).delete()

    return f"All data for account '{account_api_id}' has been deleted."
