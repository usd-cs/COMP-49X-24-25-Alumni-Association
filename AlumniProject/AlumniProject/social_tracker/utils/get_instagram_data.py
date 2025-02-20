import requests
from datetime import datetime
from social_tracker.models import Post


def get_instagram_posts(access_token, num_posts=100):
    """
    Gets recent Instagram posts using the provided access token
    and adds them to the database. This function makes a GET request
    to the Instagram API to retrieve recent post data. Any post not
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
        "fields": (
            "id, caption,media_url,media_type,"
            "timestamp,permalink,like_count,comments_count"
        ),
        "access_token": access_token,
        "limit": num_posts
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
                num_likes = post.get("like_count", 0)
                num_comments = post.get("comments_count", 0)

                # check if link already exists
                if not Post.objects.filter(post_link=permalink).exists():
                    # add to database if not duplicate post
                    Post.objects.create(
                        date_posted=date,
                        post_link=permalink,
                        num_likes=num_likes,
                        num_comments=num_comments,
                    )
                else:
                    print(f"Duplicate post, not added: {permalink}")

            return "Posts processed successfully."
        else:
            return "No posts found."

    except requests.exceptions.RequestException as e:
        return f"Error getting Instagram posts: {e}"
