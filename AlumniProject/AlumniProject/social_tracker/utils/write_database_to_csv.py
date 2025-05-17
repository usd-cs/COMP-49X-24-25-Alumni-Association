import csv
import io
import zipfile
from django.http import HttpResponse
from django.utils.text import slugify

from social_tracker.models import (
    InstagramAccount, 
    Post, 
    InstagramUser, 
    Comment, 
    InstagramStory,
    Country, 
    City, 
    Age
)

def export_all_models_zip() -> HttpResponse:
    """
    Build instagram_data.zip containing one sub-folder per InstagramAccount.
    Each sub-folder has CSV files for that account's data:
        account.csv, posts.csv, instagramusers.csv, comments.csv,
        stories.csv, countries.csv, cities.csv, ages.csv

    Comments CSV uses post_link instead of the raw post_API_ID.
    """
    parent_buf = io.BytesIO()

    with zipfile.ZipFile(parent_buf, "w", zipfile.ZIP_DEFLATED) as parent_zip:
        # 1) loop over every saved account
        for account in InstagramAccount.objects.all():
            folder = f"{slugify(account.username)}" or str(account.account_API_ID)

            # helper to add any CSV text to the parent zip under this folder
            def _add_csv(filename: str, rows: list[list], header: list[str]):
                csv_io = io.StringIO()
                writer = csv.writer(csv_io)
                writer.writerow(header)
                writer.writerows(rows)
                parent_zip.writestr(f"{folder}/{filename}", csv_io.getvalue())

            # 2) account.csv  (single row)
            _add_csv(
                "account.csv",
                [[account.account_API_ID, account.username,
                  account.date_added.astimezone().isoformat()]],
                ["account_API_ID", "username", "date_added"]
            )

            # 3) posts.csv
            posts = Post.objects.filter(instagram_account=account)
            _add_csv(
                "posts.csv",
                [[p.post_ID, p.date_posted, p.post_link, p.num_likes,
                  p.num_comments, p.num_shares, p.num_saves,
                  p.post_API_ID, p.caption]
                 for p in posts],
                ["post_ID", "date_posted", "post_link", "num_likes",
                 "num_comments", "num_shares", "num_saves",
                 "post_API_ID", "caption"]
            )

            # 4) instagramusers.csv
            users = InstagramUser.objects.filter(instagram_account=account)
            _add_csv(
                "instagramusers.csv",
                [[u.id, u.username, u.name, u.num_comments] for u in users],
                ["id", "username", "name", "num_comments"]
            )

            # 5) comments.csv  (post_link instead of post_API_ID)
            comments = Comment.objects.filter(instagram_account=account)
            _add_csv(
                "comments.csv",
                [[c.id, c.date_posted, c.num_likes, c.text,
                  c.post_API_ID.post_link if c.post_API_ID else "",  # post_link
                  c.user_ID_id, c.username, c.parent_ID, c.replies]
                 for c in comments],
                ["id", "date_posted", "num_likes", "text",
                 "post_link", "user_ID", "username",
                 "parent_ID", "replies"]
            )

            # 6) stories.csv
            stories = InstagramStory.objects.filter(instagram_account=account)
            _add_csv(
                "stories.csv",
                [[s.story_ID, s.date_posted, s.story_link, s.num_views,
                  s.num_profile_clicks, s.num_replies, s.num_swipes_up,
                  s.story_API_ID]
                 for s in stories],
                ["story_ID", "date_posted", "story_link", "num_views",
                 "num_profile_clicks", "num_replies", "num_swipes_up",
                 "story_API_ID"]
            )

            # 7) countries.csv
            countries = Country.objects.filter(instagram_account=account)
            _add_csv(
                "countries.csv",
                [[ct.name, ct.num_interactions] for ct in countries],
                ["name", "num_interactions"]
            )

            # 8) cities.csv
            cities = City.objects.filter(instagram_account=account)
            _add_csv(
                "cities.csv",
                [[ci.name, ci.num_interactions] for ci in cities],
                ["name", "num_interactions"]
            )

            # 9) ages.csv
            ages = Age.objects.filter(instagram_account=account)
            _add_csv(
                "ages.csv",
                [[ag.age_range, ag.num_interactions] for ag in ages],
                ["age_range", "num_interactions"]
            )

    parent_buf.seek(0)
    response = HttpResponse(parent_buf.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="instagram_data.zip"'
    return response
