import requests
from datetime import datetime
from django.utils.dateparse import parse_datetime
import json

from social_tracker.models import (
    InstagramAccount,
    Post,
    Country,
    City,
    Age,
    Comment,
    InstagramUser,
)


import requests
from datetime import datetime
from django.utils import timezone
from social_tracker.models import InstagramAccount, Post

def get_instagram_posts(access_token, account_id, num_posts=100):
    """
    Gets recent Instagram posts for the given account and saves or updates them,
    always linking each Post to its InstagramAccount, avoiding duplicate inserts,
    and using timezone-aware datetimes.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_id)
    except InstagramAccount.DoesNotExist:
        return f"Account with id {account_id} does not exist."

    url = "https://graph.instagram.com/me/media"
    params = {
        "fields": "id,media_url,timestamp,permalink",
        "access_token": access_token,
        "limit": num_posts,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            return "No posts found."

        for post_info in data["data"][:num_posts]:
            raw_ts = post_info.get("timestamp")
            if not raw_ts:
                continue

            # parse timestamp and make it timezone-aware
            naive_dt = datetime.strptime(raw_ts, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
            date_posted = timezone.make_aware(naive_dt, timezone.get_current_timezone())

            permalink = post_info.get("permalink", "")
            api_id = str(post_info.get("id", ""))
            if not api_id:
                continue

            # fetch insights
            insights_url = f"https://graph.instagram.com/v19.0/{api_id}/insights"
            insights_params = {
                "metric": "likes,comments,saved,shares",
                "period": "lifetime",
                "access_token": access_token,
            }
            insights_data = requests.get(insights_url, params=insights_params).json().get("data", [])

            # fetch caption
            caption = ""
            try:
                cap_url = f"https://graph.instagram.com/v19.0/{api_id}"
                cap_resp = requests.get(cap_url, params={
                    "access_token": access_token,
                    "fields": "caption"
                })
                caption = cap_resp.json().get("caption") or ""
            except Exception:
                pass

            if insights_data:
                num_likes    = insights_data[0]["values"][0]["value"]
                num_comments = insights_data[1]["values"][0]["value"]
                num_saved    = insights_data[2]["values"][0]["value"]
                num_shares   = insights_data[3]["values"][0]["value"]

                # update_or_create to avoid unique constraint errors
                post_obj, created = Post.objects.update_or_create(
                    post_API_ID=api_id,
                    defaults={
                        "instagram_account": account,
                        "date_posted": date_posted,
                        "post_link": permalink,
                        "num_likes": num_likes,
                        "num_comments": num_comments,
                        "num_shares": num_shares,
                        "num_saves": num_saved,
                        "caption": caption,
                    },
                )

                if num_comments > 0:
                    get_comment_data(access_token, api_id, account_id)

        return "Posts processed successfully."

    except requests.exceptions.RequestException as e:
        return f"Error getting Instagram posts: {e}"



def get_country_demographics(access_token, account_id):
    """
    Fetches engagement breakdown by country for the given account
    and saves Country rows linked to that InstagramAccount.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_id)
    except InstagramAccount.DoesNotExist:
        return f"Account with id {account_id} does not exist."

    url = f"https://graph.instagram.com/v22.0/{account_id}/insights"
    params = {
        "metric": "engaged_audience_demographics",
        "metric_type": "total_value",
        "access_token": access_token,
        "period": "lifetime",
        "timeframe": "this_month",
        "breakdown": "country",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        breakdowns = data["data"][0].get("total_value", {}).get("breakdowns", [])
        countries = breakdowns[0].get("results", []) if breakdowns else []

        if countries:
            Country.objects.filter(instagram_account=account).delete()
            for c in countries:
                Country.objects.create(
                    instagram_account=account,
                    name=c["dimension_values"][0],
                    num_interactions=c["value"],
                )
    except Exception as e:
        return f"Error getting country demographics: {e}"


def get_city_demographics(access_token, account_id):
    """
    Fetches engagement breakdown by city for the given account
    and saves City rows linked to that InstagramAccount.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_id)
    except InstagramAccount.DoesNotExist:
        return f"Account with id {account_id} does not exist."

    url = f"https://graph.instagram.com/v22.0/{account_id}/insights"
    params = {
        "metric": "engaged_audience_demographics",
        "metric_type": "total_value",
        "access_token": access_token,
        "period": "lifetime",
        "timeframe": "this_month",
        "breakdown": "city",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        breakdowns = data["data"][0].get("total_value", {}).get("breakdowns", [])
        cities = breakdowns[0].get("results", []) if breakdowns else []

        if cities:
            City.objects.filter(instagram_account=account).delete()
            for c in cities:
                City.objects.create(
                    instagram_account=account,
                    name=c["dimension_values"][0],
                    num_interactions=c["value"],
                )
    except Exception as e:
        return f"Error getting city demographics: {e}"


def get_age_demographics(access_token, account_id):
    """
    Fetches engagement breakdown by age group for the given account
    and saves Age rows linked to that InstagramAccount.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_id)
    except InstagramAccount.DoesNotExist:
        return f"Account with id {account_id} does not exist."

    url = f"https://graph.instagram.com/v22.0/{account_id}/insights"
    params = {
        "metric": "engaged_audience_demographics",
        "metric_type": "total_value",
        "access_token": access_token,
        "period": "lifetime",
        "timeframe": "this_month",
        "breakdown": "age",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        breakdowns = data["data"][0].get("total_value", {}).get("breakdowns", [])
        ages = breakdowns[0].get("results", []) if breakdowns else []

        if ages:
            Age.objects.filter(instagram_account=account).delete()
            for a in ages:
                Age.objects.create(
                    instagram_account=account,
                    age_range=a["dimension_values"][0],
                    num_interactions=a["value"],
                )
    except Exception as e:
        return f"Error getting age demographics: {e}"


def get_comment_data(access_token, post_id, account_id):
    """
    Fetches all comments for a post and saves them,
    always linking Comment and InstagramUser to the given account.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_id)
    except InstagramAccount.DoesNotExist:
        print(f"Account with id {account_id} does not exist.")
        return

    all_comment_ids = []
    url = f"https://graph.instagram.com/{post_id}/comments"
    params = {
        "access_token": access_token,
        "fields": "id",
        "limit": 50,
    }

    # paginate to collect all comment IDs
    while True:
        resp = requests.get(url, params=params).json()
        if "error" in resp:
            print(f"Error fetching comments: {resp['error'].get('message')}")
            return

        for c in resp.get("data", []):
            cid = c.get("id")
            if cid:
                all_comment_ids.append(cid)

        nxt = resp.get("paging", {}).get("next")
        if not nxt:
            break
        url = nxt
        params = {}

    comment_map = {}
    for cid in all_comment_ids:
        obj, replies = get_comments_helper(access_token, cid, post_id, account)
        if obj:
            comment_map[obj.id] = (obj, replies)

    # assign parent_ID for replies
    for cid, (comment, replies) in comment_map.items():
        for rid in replies:
            if rid in comment_map:
                reply_obj, _ = comment_map[rid]
                if not reply_obj.parent_ID:
                    reply_obj.parent_ID = cid
                    reply_obj.save()


def get_comments_helper(access_token, comment_id, post_id, account):
    """
    Helper to fetch a single comment, save it and its user,
    always linking both to the given InstagramAccount.
    Returns (Comment instance, list_of_reply_ids).
    """
    try:
        url = f"https://graph.instagram.com/{comment_id}"
        params = {
            "fields": "id,from,like_count,text,timestamp,replies,username,parent_id",
            "access_token": access_token,
        }
        data = requests.get(url, params=params).json()
        if "error" in data:
            print(f"Skipping comment {comment_id}: {data['error'].get('message')}")
            return None, []

        user_data = data.get("from", {})
        uid = user_data.get("id")
        uname = user_data.get("username")
        if not uid or not uname:
            print(f"Skipping comment {comment_id} for missing user info")
            return None, []

        timestamp = data.get("timestamp")
        text = data.get("text", "")
        likes = data.get("like_count", 0)
        replies = [r.get("id") for r in data.get("replies", {}).get("data", []) if r.get("id")]
        parent_id = data.get("parent_id") or ""

        # save or update user
        user_obj, created = InstagramUser.objects.get_or_create(
            id=uid,
            defaults={"instagram_account": account}
        )
        user_obj.instagram_account = account
        user_obj.username = uname
        user_obj.save()

        # save or update comment
        comment_obj, created = Comment.objects.get_or_create(id=comment_id)
        comment_obj.instagram_account = account
        # ensure we get the right Post for this account
        comment_obj.post_API_ID = Post.objects.get(
            instagram_account=account,
            post_API_ID=post_id
        )
        comment_obj.date_posted = parse_datetime(timestamp)
        comment_obj.num_likes   = likes
        comment_obj.replies     = replies
        comment_obj.text        = text
        comment_obj.username    = uname
        comment_obj.user_ID     = user_obj
        if not comment_obj.parent_ID:
            comment_obj.parent_ID = parent_id
        comment_obj.save()

        if created:
            user_obj.num_comments += 1
            user_obj.save()

        return comment_obj, replies

    except Exception as e:
        print(f"Error processing comment {comment_id}: {e}")
        return None, []



def get_instagram_stories(access_token, account_id):
    """
    Fetches active Instagram stories for the given account,
    saves them to the database with the correct foreign key.
    """
    try:
        account = InstagramAccount.objects.get(account_API_ID=account_id)
    except InstagramAccount.DoesNotExist:
        return f"Account with id {account_id} does not exist."

    stories_url = "https://graph.instagram.com/v19.0/me/stories"
    stories_params = {"fields": "id,timestamp,permalink", "access_token": access_token}

    try:
        response = requests.get(stories_url, params=stories_params)
        data = response.json()

        if response.status_code != 200:
            error_msg = data.get("error", {}).get("message", "Unknown API error")
            return f"API Error fetching stories ({response.status_code}): {error_msg}"

        active_stories = []
        if "data" in data and data["data"]:
            for story in data["data"]:
                story_id = story.get("id")
                if not story_id:
                    continue

                # parse timestamp
                date_posted = None
                ts = story.get("timestamp")
                if ts:
                    try:
                        date_posted = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
                    except ValueError:
                        pass

                # default metrics
                metrics = {"num_views": 0, "num_profile_clicks": 0, "num_swipes_up": 0}

                # fetch insights
                try:
                    insights_url = f"https://graph.instagram.com/v19.0/{story_id}/insights"
                    insights_params = {
                        "metric": "reach,navigation,profile_visits",
                        "period": "lifetime",
                        "access_token": access_token,
                    }
                    resp_ins = requests.get(insights_url, params=insights_params).json().get("data", [])
                    for m in resp_ins:
                        name = m.get("name")
                        val = m.get("values", [{}])[0].get("value", 0)
                        if name == "reach":
                            metrics["num_views"] = val
                        elif name == "profile_visits":
                            metrics["num_profile_clicks"] = val
                        elif name == "navigation":
                            metrics["num_swipes_up"] = val
                except Exception:
                    pass

                active_stories.append({
                    "story_API_ID": story_id,
                    "date_posted": date_posted,
                    "story_link": story.get("permalink", ""),
                    "num_views": metrics["num_views"],
                    "num_profile_clicks": metrics["num_profile_clicks"],
                    "num_replies": 0,
                    "num_swipes_up": metrics["num_swipes_up"],
                })

            # delete old stories for this account and save new ones
            InstagramStory.objects.filter(instagram_account=account).delete()
            for s in active_stories:
                InstagramStory.objects.create(
                    instagram_account=account,
                    date_posted=s["date_posted"],
                    story_link=s["story_link"],
                    num_views=s["num_views"],
                    num_profile_clicks=s["num_profile_clicks"],
                    num_replies=s["num_replies"],
                    num_swipes_up=s["num_swipes_up"],
                    story_API_ID=s["story_API_ID"],
                )

        return active_stories

    except requests.exceptions.RequestException as e:
        return f"Error getting Instagram stories: {e}"
    except json.JSONDecodeError:
        return "Error decoding JSON response for stories."
    except Exception as e:
        return f"Error processing stories: {e}"