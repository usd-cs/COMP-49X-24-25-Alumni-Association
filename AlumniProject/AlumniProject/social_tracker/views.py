from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils.get_instagram_data import (
    get_instagram_posts,
    get_country_demographics,
    get_city_demographics,
    get_age_demographics,
    get_instagram_stories,
)
from .utils.country_code_resolver import load_country_dict, get_country_name
from .models import Country, City, Age
from .utils.write_database_to_csv import export_posts_to_csv
from django.views.decorators.csrf import csrf_exempt
from .models import Post
from .models import AccessToken
from .models import Comment
from .models import InstagramUser
from .models import InstagramStory
from django.db import models

import json
from social_tracker.utils.get_time_of_day_statistics import (
    get_avg_likes_by_time_block,
    get_avg_comments_by_time_block,
    get_avg_saves_by_time_block,
    get_avg_shares_by_time_block,
)


"""
    Handles user login functionality.

    If authentication is successful:
        - Logs in the user
        - Redirects to the "home" page with an HTTP 200 status code.

    If authentication fails:
        - Renders the login page with an error message
        - Returns an HTTP 401 status code.

    Args:
        request (HttpRequest):
        The HTTP request object containing metadata about the request.

    Returns:
        HttpResponse:
        A redirect to the "home" page on success or the login page on failure.
"""


def user_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = User.objects.get(email=email)
            # Django login expects username not email
        except User.DoesNotExist:
            user = None
        if user is not None:
            user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            request.session.save()
            response = redirect("home")
            response.status_code = 302
            return response
        else:
            response = render(request, "login.html", {"error": "Invalid credentials."})
            response.status_code = 401
            return response
    return render(request, "login.html")


"""
    Home page. Requires users to be logged in using @login_required

    Args:
        request (HttpRequest):
            The HTTP request object containing metadata about the request.

    Returns:
        HttpResponse:
            A redirect to home page on success or the login page on failure.
"""


@login_required
def home(request):
    return render(request, "index.html")


@login_required
def post_details(request, post_api_id):
    """
    Renders a detail page for a specific Instagram post, identified by its external post API ID.

    This view looks up the Post object in the database via its 'post_API_ID'. If the post
    does not exist, the view returns a template indicating that the post was not found.
    Otherwise, it passes the retrieved Post object to the 'post-details.html' template.

    :param request: The current HttpRequest object.
    :param post_api_id: A string representing the external Instagram ID for the post.
    :return: An HttpResponse rendering either the detail page (with the Post context)
             or an error message if no matching post is found.
    """
    try:
        post_obj = Post.objects.get(post_API_ID=post_api_id)
    except Post.DoesNotExist:
        return render(request, "post-details.html", {"error": "Post not found."})

    return render(request, "post-details.html", {"post": post_obj})


@login_required
def instagram_link(request, post_id):
    """
    Return the Instagram link for the post with `post_id` in JSON.
    Expected response format:
      {"link": "<post_link>"}
    If the post is not found or an error occurs, returns:
      {"error": "<error_message>"}
    """
    try:
        post_obj = Post.objects.get(post_API_ID=post_id)
        return JsonResponse({"link": post_obj.post_link}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def post_comments(request, post_id):
    """
    Return all comments for the post `post_id` in JSON.
    Expecting an array of comment objects:
      [{timestamp, num_likes, replies, username, text}, ...]
    """
    try:
        # Query your DB for all comments where post_id matches
        comment_qs = Comment.objects.filter(post_API_ID=post_id)

        # Build a JSON-serializable list
        comment_list = []
        for c in comment_qs:
            comment_list.append(
                {
                    "timestamp": (
                        c.date_posted.strftime("%H:%M %m/%d/%Y")
                        if c.date_posted
                        else None
                    ),
                    "num_likes": c.num_likes,
                    "replies": c.replies,  # or len(c.replies) if you prefer
                    "username": c.username,
                    "text": c.text,
                }
            )

        # Return the list as JSON
        return JsonResponse(comment_list, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def save_access_token(request):
    """
    Accepts POST requests containing an access token and saves it to
    the database. It ensures that only one access token exists and
    automatically replaces the old tokenwhen a new one is provided.

    Parameters:
    - request: HttpRequest object that contains the access token.

    Returns:
    - JsonResponse: JSON response indicating success or failure
        - 200: If the access token is saved successfully.
        - 400: If the access token is missing or invalid.
        - 405: If the request is invalid.
    """
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request."}, status=405)
    try:
        data = json.loads(request.body)
        access_token_value = data.get("access_token")
        account_ID = data.get("account_ID")

        if not access_token_value:
            return JsonResponse({"message": "Access token required."}, status=400)

        # save new access token
        access_token = AccessToken(token=access_token_value, account_id=account_ID)
        # save function should delete old one automatically
        access_token.save()

        return JsonResponse({"message": "Access token saved successfully."})
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid token."}, status=400)


@login_required
def get_demographics(request):
    return render(request, "demographics.html")


@login_required
def token_landing(request):
    return render(request, "token.html")


def get_posts_view(request):
    """
    Fetches Instagram posts using the stored access token
    and uses it to call the Instagram API. The results of
    the API call are returned as a JSON response.

    Parameters:
    - request: HttpRequest object.

    Returns:
    - JsonResponse: A JSON response that is
    the result of the API call.
    """
    access_token = AccessToken.objects.get()
    result = get_instagram_posts(access_token.token)
    return JsonResponse({"message": result})


def update_demographics():
    """
    Calls all the helper functions that collect demographic info
    from Instagram and puts them into the database. This can
    be used by the frontend to call the functions

    Parameters:
    - None

    Returns:
    - None
    """
    access_token = AccessToken.objects.get()
    get_country_demographics(access_token.token, access_token.account_id)
    get_city_demographics(access_token.token, access_token.account_id)
    get_age_demographics(access_token.token, access_token.account_id)
    return


def demographics_view(request):
    """
    Retrieves demographic interaction data and returns it as a JSON response.

    This view fetches data from the Age, Country, and City models, aggregating
    the number of interactions based on different demographic categories.

    Returns:
        JsonResponse: A JSON response containing:
            - 'ageRanges': A dictionary mapping age ranges to interaction counts.
            - 'topCountries': A list of dictionaries with country names and interaction counts.
            - 'topCities': A list of dictionaries with city names and interaction counts.
            - 'success': A boolean indicating the request was successful.

    Args:
        request (HttpRequest): The HTTP request object.
    """
    update_demographics()
    age_data = Age.objects.all().values("age_range", "num_interactions")
    country_data = (
        Country.objects.all()
        .order_by("-num_interactions")[:5]
        .values("name", "num_interactions")
    )
    city_data = (
        City.objects.all()
        .order_by("-num_interactions")[:5]
        .values("name", "num_interactions")
    )
    country_dict = load_country_dict()
    response_data = {
        "ageRanges": {item["age_range"]: item["num_interactions"] for item in age_data},
        "topCountries": [
            {
                "country": get_country_name(country_dict, item["name"]),
                "count": item["num_interactions"],
            }
            for item in country_data
        ],
        "topCities": [
            {"city": item["name"], "count": item["num_interactions"]}
            for item in city_data
        ],
    }
    return JsonResponse({"success": True, "data": response_data})


def demographics_page(request):
    """
    Renders the demographics page.

    This view returns the HTML page where demographic data is displayed.
    It provides the interface for users to view age, country, and city demographics.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered demographics HTML page.
    """
    return render(request, "demographics.html")


def list_stored_posts(request):
    """
    Returns a JSON response containing all posts stored in the database.

    Parameters:
    - request: HttpRequest object.

    Returns:
    - JsonResponse: A JSON response that is
    the result of the API call.
    """
    try:
        posts = Post.objects.all()

        # Get filter parameters from request
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        min_likes = request.GET.get("min_likes")
        min_comments = request.GET.get("min_comments")
        min_shares = request.GET.get("min_shares")
        min_saves = request.GET.get("min_saves")

        # Apply date filters if provided
        if date_from:
            try:
                date_from = datetime.strptime(date_from, "%Y-%m-%d")
                posts = posts.filter(date_posted__gte=date_from)
            except ValueError:
                return JsonResponse(
                    {"success": False, "message": "Invalid date format for date_from"},
                    status=400,
                )

        if date_to:
            try:
                date_to = datetime.strptime(date_to, "%Y-%m-%d")
                posts = posts.filter(date_posted__lte=date_to)
            except ValueError:
                return JsonResponse(
                    {"success": False, "message": "Invalid date format for date_to"},
                    status=400,
                )

        # Apply engagement filters if provided
        if min_likes:
            try:
                min_likes = int(min_likes)
                posts = posts.filter(num_likes__gte=min_likes)
            except ValueError:
                return JsonResponse(
                    {"success": False, "message": "Invalid min_likes value"}, status=400
                )

        if min_comments:
            try:
                min_comments = int(min_comments)
                posts = posts.filter(num_comments__gte=min_comments)
            except ValueError:
                return JsonResponse(
                    {"success": False, "message": "Invalid min_comments value"},
                    status=400,
                )

        if min_shares:
            try:
                min_shares = int(min_shares)
                posts = posts.filter(num_shares__gte=min_shares)
            except ValueError:
                return JsonResponse(
                    {"success": False, "message": "Invalid min_shares value"},
                    status=400,
                )

        if min_saves:
            try:
                min_saves = int(min_saves)
                posts = posts.filter(num_saves__gte=min_saves)
            except ValueError:
                return JsonResponse(
                    {"success": False, "message": "Invalid min_saves value"}, status=400
                )
        # Get posts data
        for post in posts:
            post.caption = "---" if not post.caption else post.caption
        posts_data = [
            {
                "id": post.post_API_ID,
                "date_posted": post.date_posted.strftime("%m/%d/%Y"),
                "post_link": post.post_link,
                "likes": post.num_likes,
                "comments": post.num_comments,
                "shares": post.num_shares,
                "saves": post.num_saves,
                "caption": post.caption[:50],
            }
            for post in posts
        ]
        return JsonResponse(
            {
                "success": True,
                "data": posts_data,
                "message": "Posts retrieved successfully",
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "data": posts_data,
                "message": f"Error retrieving posts: {str(e)}",
            },
            status=500,
        )


def export_csv_view(request):
    """
    Exports Instagram post data to a CSV file.
    Calls a script to export post data stored in the database to a CSV file.

    Parameters:
    - request: HttpRequest object.

    Returns:
    - HttpResponse: Response that contains downloadable csv file
    """
    return export_posts_to_csv()


def get_days_of_week(request):
    """
    Aggregates post engagement metrics by day of the week.

    This view retrieves all posts from the database and groups them by the day of the week
    they were posted. Returns an average of all metrics per day.

    Returns:
        JsonResponse: A JSON response with the following structure:
            {
                "success": True,
                "data": {
                    "Monday": [num_posts, avg_likes, avg_comments, avg_shares, avg_saves],
                    "Tuesday": [...],
                    ...
                }
            }
    """
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    days_dict = {day: [0, 0, 0, 0, 0] for day in days}
    posts = Post.objects.all()
    for post in posts:
        try:
            days_dict[post.date_posted.strftime("%A")][0] += 1
            days_dict[post.date_posted.strftime("%A")][1] += post.num_likes
            days_dict[post.date_posted.strftime("%A")][2] += post.num_comments
            days_dict[post.date_posted.strftime("%A")][3] += post.num_shares
            days_dict[post.date_posted.strftime("%A")][4] += post.num_saves
        except Exception as e:
            print(e)
    for day in days_dict:
        for item in range(1, 5):
            days_dict[day][item] = (
                round(days_dict[day][item] / days_dict[day][0], 2)
                if days_dict[day][0] > 0
                else 0
            )
    return JsonResponse(
        {
            "success": True,
            "data": days_dict,
        }
    )


def get_days_of_week_data_helper(request):
    """
    Calls the existing get_days_of_week view and gets the data dictionary.
    """
    response = get_days_of_week(request)
    data = json.loads(response.content)
    return data.get("data", {})


@login_required
def account_info(request):
    """
    Handles the Account Info page and displays two charts with post engagement trends.
    Also renders the account information page, displaying users sorted by comment count.

    Based on the selected metrics from the dropdowns, this view pulls average engagement data
    by 2-hour time blocks and by day of the week. It prepares the labels and values for each chart
    and passes everything to the template so the charts can render using Chart.js.
    The page responds to optional GET parameters of 'metric' for the time block chart and
    'day_metric' for the day of week chart.
    """
    metric = request.GET.get("metric", "likes")
    day_metric = request.GET.get("day_metric", "likes")

    # Time block data
    if metric == "likes":
        _, block_data = get_avg_likes_by_time_block()
    elif metric == "comments":
        _, block_data = get_avg_comments_by_time_block()
    elif metric == "saves":
        _, block_data = get_avg_saves_by_time_block()
    elif metric == "shares":
        _, block_data = get_avg_shares_by_time_block()
    else:
        _, block_data = get_avg_likes_by_time_block()  # default

    time_labels = [row["block"] for row in block_data]
    time_values = [row[f"avg_{metric}"] for row in block_data]

    # Day of week data (from existing view)
    day_data = get_days_of_week_data_helper(request)
    day_labels = list(day_data.keys())
    day_index = ["likes", "comments", "shares", "saves"].index(day_metric) + 1
    day_values = [day_data[day][day_index] for day in day_labels]

    users = InstagramUser.objects.order_by("-num_comments")

    context = {
        "metric": metric,
        "labels": time_labels,
        "values": time_values,
        "label": f"Average {metric.capitalize()} per Time Block",
        "day_metric": day_metric,
        "labels_day": day_labels,
        "values_day": day_values,
        "day_label": f"Average {day_metric.capitalize()} per Day",
        "users": users,
    }
    return render(request, "account_info.html", context)


@login_required
def stories_info(request):
    """
    Renders the stories information page.
    The story data will be loaded asynchronously via JavaScript.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered stories information HTML page.
    """

    context = {
        'stories': [], # Start with an empty list
        'total_views': 0,
        'total_profile_clicks': 0,
        'total_swipes': 0
    }
    return render(request, "stories_info.html", context)


@login_required
def get_stories_view(request):
    """
    Fetches Instagram stories using the stored access token
    and returns the data as a JSON response.

    This view calls the `get_instagram_stories` utility function.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: Contains either:
            - {"success": True, "stories": [list_of_story_dicts]}
            - {"success": False, "message": "Error message"}
    """
    if request.method != 'GET':
        return JsonResponse({
            "success": False,
            "message": "Only GET requests are allowed"
        }, status=405) # Method Not Allowed

    try:
        access_token = AccessToken.objects.get()
        print(f"Using access token: {access_token.token[:10]}... (truncated)")
        
        # Call the updated utility function
        result = get_instagram_stories(access_token.token)
        
        # Check if the result is a list (success) or a string (error)
        if isinstance(result, list):
            print(f"Successfully fetched {len(result)} stories.")
            # Convert datetime objects to strings for JSON serialization
            for story in result:
                if isinstance(story.get('date_posted'), datetime):
                    story['date_posted'] = story['date_posted'].isoformat()

            return JsonResponse({
                "success": True,
                "stories": result
            })
        else:
            # Result is an error string
            print(f"API Error/Message: {result}")
            return JsonResponse({
                "success": False,
                "message": result 
            }, status=500) # Internal Server Error or specific error indication

    except AccessToken.DoesNotExist:
        print("Access token not found in database.")
        return JsonResponse({
            "success": False,
            "message": "No access token found. Please add an access token first."
        }, status=404) # Not Found
    except Exception as e:
        print(f"Error in get_stories_view: {str(e)}")
        # Log the full traceback for debugging if needed
        # import traceback
        # traceback.print_exc()
        return JsonResponse({
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}"
        }, status=500) # Internal Server Error
