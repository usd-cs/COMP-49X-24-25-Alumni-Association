import requests
from datetime import datetime
from social_tracker.models import Post, Country, City, Age, Comment, User


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


def get_comments_helper(access_token, comment_id, post_id=None, parent_id=None):
    """
    Fetch details of a comment and its replies.
    - Saves replies under the parent comment's `replies` list.
    - Each reply is processed as its own comment.
    - Skips comments with errors but continues processing others.
    """
    try:
        url = f"https://graph.instagram.com/{comment_id}"
        params = {
            "fields": "id,from,like_count,text,timestamp,replies,username,parent_id",
            "access_token": access_token,
        }

        response = requests.get(url, params=params)
        resp_json = response.json()

        if "error" in resp_json:
            print(f"Skipping comment {comment_id} due to API error: {resp_json['error'].get('message')}")
            return

        user_data = resp_json.get("from", {})
        user_id = user_data.get("id")
        username = user_data.get("username")
        timestamp = resp_json.get("timestamp")
        text = resp_json.get("text")
        num_likes = resp_json.get("like_count")
        replies_data = resp_json.get("replies", {}).get("data", [])

        # Collect reply IDs for the parent comment
        replies_list = []
        for reply in replies_data:
            reply_id = reply.get("id")
            if reply_id:
                replies_list.append(reply_id)

        # Save the comment
        try:
            if not Comment.objects.filter(id=comment_id).exists():
                Comment.objects.create(
                    id=comment_id,
                    timestamp=timestamp,
                    post_id=post_id,  # Associate comment with the post
                    num_likes=num_likes,
                    replies=replies_list,  # Save reply IDs
                    text=text,
                    username=username,
                    user_id=user_id,
                    parent_id=parent_id,  # Assign parent_id if it's a reply
                )
            else:
                existing_comment = Comment.objects.get(id=comment_id)
                existing_comment.timestamp = timestamp
                existing_comment.num_likes = num_likes
                existing_comment.replies = replies_list  # Update replies
                existing_comment.text = text
                existing_comment.save()
        except Exception as e:
            print(f"Skipping comment {comment_id} due to database error: {e}")
            return

        # Process each reply as its own comment
        for reply in replies_data:
            reply_id = reply.get("id")
            if reply_id:
                get_comments_helper(access_token, reply_id, post_id, parent_id=comment_id)

    except Exception as e:
        print(f"Skipping comment {comment_id} due to unexpected error: {e}")
        return


def get_comment_data(access_token, post_id):
    """
    Fetch all top-level comments of a post and process their replies.
    - Each reply is stored under the `replies` field of its parent.
    - Replies are processed as independent comments with `parent_id` set.
    """
    try:
        url = f"https://graph.instagram.com/{post_id}"
        params = {
            "fields": "comments",
            "access_token": access_token,
        }

        response = requests.get(url, params=params)
        resp_json = response.json()

        if "error" in resp_json:
            print(f"Error fetching post {post_id}: {resp_json['error'].get('message')}")
            return

        comments_data = resp_json.get("comments", {}).get("data", [])

        for comment in comments_data:
            comment_id = comment.get("id")
            if comment_id:
                get_comments_helper(access_token, comment_id, post_id)  # No parent_id for top-level comments

    except Exception as e:
        print(f"Error fetching post {post_id}: {e}")
        return
