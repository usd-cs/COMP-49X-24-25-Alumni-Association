import requests
from datetime import datetime
from social_tracker.models import Post, Country, City, Age, Comment, User
from django.utils.dateparse import parse_datetime

def get_instagram_posts(access_token, num_posts=100):
    """
    Gets recent Instagram posts using the provided access token
    and adds them to the database. This function makes a GET request
    to the Instagram API to retrieve recent post data and then another
    get request that gets the post attributes with the ID. Any post not
    already in in the database is added.

    Parameters:
    - access_token (str): A valid access token for the Instagram API.
    - num_posts (int): number of recent posts to process (default: 100).

    Returns:
    - str: Message indicating the result of the operation:
        - "Posts processed successfully." if posts are retrieved and processed.
        - "No posts found." if no posts are returned by the API.
        - Error message if the API call fails.

    Exceptions:
    - Handles requests.exceptions.RequestException for API-related errors.
    """
    url = "https://graph.instagram.com/me/media"
    params = {
        "fields": "id,media_url,timestamp,permalink",
        "access_token": access_token,
        "limit": num_posts,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # raise error if it is not a success code
        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            posts = data["data"][:num_posts]

            # get post data
            for post in posts:
                date = datetime.strptime(
                    post["timestamp"], "%Y-%m-%dT%H:%M:%S%z"
                ).replace(tzinfo=None)
                permalink = post.get("permalink", "N/A")
                api_id = str(post.get("id", ""))

                # check if link already exists and add to database if not duplicate post and post exists
                if api_id != "" and api_id is not None:
                    # make request for insights based on post ID
                    url = (
                        "https://graph.instagram.com/v19.0/" + str(api_id) + "/insights"
                    )
                    params = {
                        "metric": "likes,comments,saved,shares",
                        "period": "lifetime",
                        "access_token": access_token,
                    }
                    response = requests.get(url, params=params)
                    resp_json = response.json()
                    data = resp_json.get("data")
                    # data is only none if posts were from before the account became a business account.
                    if data != [] and data is not None:
                        # get post attributes
                        num_likes = data[0].get("values")[0].get("value")
                        num_comments = data[1].get("values")[0].get("value")
                        num_saved = data[2].get("values")[0].get("value")
                        num_shares = data[3].get("values")[0].get("value")
                        if num_comments > 0: get_comment_data(access_token, api_id)
                        if not Post.objects.filter(post_link=permalink).exists():
                            # post does not exist in database, create new post
                            Post.objects.create(
                                date_posted=date,
                                post_link=permalink,
                                num_likes=num_likes,
                                num_comments=num_comments,
                                num_shares=num_shares,
                                num_saves=num_saved,
                                post_API_ID=api_id,
                            )
                        else:
                            # modifies existing post instead of creating a new post.
                            existing_post = Post.objects.get(post_link=permalink)
                            existing_post.num_likes = num_likes
                            existing_post.num_comments = num_comments
                            existing_post.num_shares = num_shares
                            existing_post.num_saves = num_saved
                            existing_post.post_API_ID = api_id
                            existing_post.save()

                else:
                    print(f"Invalid post- not added: {permalink}")

            return "Posts processed successfully."
        else:
            return "No posts found."

    except requests.exceptions.RequestException as e:
        return f"Error getting Instagram posts: {e}"


def get_country_demographics(access_token, account_id):
    """
    Fetches and stores Instagram engagement demographics by country.

    This function queries the Instagram Graph API for engagement demographic
    data, specifically breaking down interactions by country. The retrieved
    data is then stored in the `Country` model.

    Args:
        access_token (str): The access token for authenticating API requests.
        account_id (str): The Instagram account ID for which to retrieve data.

    Returns:
        str: An error message if the API request fails, otherwise None.
    """
    url = "https://graph.instagram.com/v22.0/" + str(account_id) + "/insights"
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
        response.raise_for_status()  # raise error if it is not a success code
        data = response.json()
        if "total_value" in data["data"][0]:
            countries = data["data"][0]["total_value"]["breakdowns"][0]["results"]
            if len(countries) > 0:
                Country.objects.all().delete()
            for i in range(0, len(countries)):
                Country.objects.create(
                    name=countries[i]["dimension_values"][0],
                    num_interactions=countries[i]["value"],
                )
    except Exception as e:
        return f"Error getting Instagram posts: {e}"


def get_city_demographics(access_token, account_id):
    """
    Fetches and stores Instagram engagement demographics by city.

    This function queries the Instagram Graph API for engagement demographic
    data, specifically breaking down interactions by city. The retrieved
    data is then stored in the `City` model.

    Args:
        access_token (str): The access token for authenticating API requests.
        account_id (str): The Instagram account ID for which to retrieve data.

    Returns:
        str: An error message if the API request fails, otherwise None.
    """
    url = "https://graph.instagram.com/v22.0/" + str(account_id) + "/insights"
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
        response.raise_for_status()  # raise error if it is not a success code
        data = response.json()
        if "total_value" in data["data"][0]:
            cities = data["data"][0]["total_value"]["breakdowns"][0]["results"]
            if len(cities) > 0:
                City.objects.all().delete()
            for i in range(0, len(cities)):
                City.objects.create(
                    name=cities[i]["dimension_values"][0],
                    num_interactions=cities[i]["value"],
                )
    except Exception as e:
        return f"Error getting Instagram posts: {e}"


def get_age_demographics(access_token, account_id):
    """
    Fetches and stores Instagram engagement demographics by age group.

    This function queries the Instagram Graph API for engagement demographic
    data, specifically breaking down interactions by age group. The retrieved
    data is then stored in the `Age` model.

    Args:
        access_token (str): The access token for authenticating API requests.
        account_id (str): The Instagram account ID for which to retrieve data.

    Returns:
        str: An error message if the API request fails, otherwise None.
    """
    url = "https://graph.instagram.com/v22.0/" + str(account_id) + "/insights"
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
        response.raise_for_status()  # raise error if it is not a success code
        data = response.json()
        if "total_value" in data["data"][0]:
            ages = data["data"][0]["total_value"]["breakdowns"][0]["results"]
            if len(ages) > 0:
                Age.objects.all().delete()
            for i in range(0, len(ages)):
                Age.objects.create(
                    age_range=ages[i]["dimension_values"][0],
                    num_interactions=ages[i]["value"],
                )
    except Exception as e:
        return f"Error getting Instagram posts: {e}"



def get_comment_data(access_token, post_id):
    """
    Gets all comments and replies for a specific Instagram post and stores them in the database.

    Uses the Instagram Graph API to retrieve all top-level and nested replies for
    a given post. It saves each comment and updates or creates the associated
    user. It also handles setting the correct parent_id for replies by linking them to their
    corresponding parent comments after all data has been fetched.

    Args:
        access_token (str): The access token used to authenticate with the Instagram API.
        post_id (str): The ID of the Instagram post to fetch comments for.

    Returns:
        None
    """
    try:
        all_comment_ids = []
        url = f"https://graph.instagram.com/{post_id}/comments"
        params = {
            "access_token": access_token,
            "fields": "id",
            "limit": 50,
        }

        # get all comment IDs using pagination during the api call
        while True:
            print("cycling")
            response = requests.get(url, params=params)
            resp_json = response.json()

            if "error" in resp_json:
                print(f"Error fetching comments: {resp_json['error'].get('message')}")
                return

            for comment in resp_json.get("data", []):
                comment_id = comment.get("id")
                if comment_id:
                    all_comment_ids.append(comment_id)

            paging = resp_json.get("paging", {})
            next_url = paging.get("next")
            if next_url:
                url = next_url
                params = {}
            else:
                break

        # Get all attributes of and save each comment
        comment_map = {}
        for comment_id in all_comment_ids:
            comment_obj, reply_ids = get_comments_helper(access_token, comment_id, post_id)
            if comment_obj:
                comment_map[comment_obj.id] = (comment_obj, reply_ids)

        # Loop through each comment and assign parent_id to its replies
        for comment_id, (comment, reply_ids) in comment_map.items():
            for reply_id in reply_ids:
                if reply_id in comment_map:
                    reply, _ = comment_map[reply_id]
                    if not reply.parent_id:
                        reply.parent_id = comment_id
                        reply.save()

    except Exception as e:
        print(f"Unexpected error in get_comment_data: {e}")


def get_comments_helper(access_token, comment_id, post_id=None):
    """
    Gets attribute for an Instagram comment and stores it along with user and reply data.

    Pulls information about a comment from the Instagram API. This includes the
    user who posted it, the number of likes, the comment text, timestamp, and
    any replies. It then checks for duplicates and creates or updates the corresponding 
    Comment and User records in the database.

    If the comment is new, it increments the user’s total comment count. It also collects
    any reply IDs so they can be processed later.

    Args:
        access_token (str): The access token used to authenticate with the Instagram API.
        comment_id (str): The ID of the comment to fetch.
        post_id (str, optional): The ID of the post the comment belongs to.

    Returns:
        tuple: A tuple containing the saved Comment object and a list of its reply IDs.
               Returns (None, []) if something goes wrong.
    """
    try:
        url = f"https://graph.instagram.com/{comment_id}"
        params = {
            "fields": "id,from,like_count,text,timestamp,replies,username,parent_id",
            "access_token": access_token,
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            print(f"Skipping comment {comment_id} due to an error: {data['error'].get('message')}")
            return None, []

        # get user and comment attributes
        user_data = data.get("from", {})
        user_id = user_data.get("id")
        username = user_data.get("username")
        timestamp = data.get("timestamp")
        text = data.get("text")
        num_likes = data.get("like_count")
        reply_ids = [r.get("id") for r in data.get("replies", {}).get("data", []) if r.get("id")]
        parent_id = data.get("parent_id") or ""

        # Save or update user
        try:
            user_obj, _ = User.objects.get_or_create(id=user_id)
            user_obj.username = username
        except Exception as e:
            print(f"User save error: {e}")
            return None, []

        # Save or update comment
        try:
            comment_obj, created = Comment.objects.get_or_create(id=comment_id)

            comment_obj.timestamp = parse_datetime(timestamp)
            comment_obj.post_id = post_id
            comment_obj.num_likes = num_likes
            comment_obj.replies = reply_ids
            comment_obj.text = text
            comment_obj.username = username
            comment_obj.user_id = user_id

            if not comment_obj.parent_id:
                comment_obj.parent_id = parent_id

            comment_obj.save()

            # Only increment comment count if this is a new comment
            if created:
                user_obj.num_comments += 1
                user_obj.save()

            return comment_obj, reply_ids

        except Exception as e:
            print(f"Error saving comment {comment_id}: {e}")
            return None, []

    except Exception as e:
        print(f"Error fetching comment {comment_id}: {e}")
        return None, []
