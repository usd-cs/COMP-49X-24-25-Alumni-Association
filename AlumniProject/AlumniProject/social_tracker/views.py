from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils.get_instagram_data import get_instagram_posts
from .utils.write_database_to_csv import export_posts_to_csv
from django.views.decorators.csrf import csrf_exempt
from .models import Post
from .models import AccessToken
import json

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
            response = redirect("home")
            response.status_code = 200
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

        if not access_token_value:
            return JsonResponse({"message": "Access token required."}, status=400)

        # save new access token
        access_token = AccessToken(token=access_token_value)
        # save function should delete old one automatically
        access_token.save()

        return JsonResponse({"message": "Access token saved successfully."})
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid token."}, status=400)


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

        #Get filter parameters from request
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        min_likes = request.GET.get('min_likes')
        min_comments = request.GET.get('min_comments')
        min_shares = request.GET.get('min_shares')
        min_saves = request.GET.get('min_saves')
        
        #Apply date filters if provided
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                posts = posts.filter(date_posted__gte=date_from)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid date format for date_from'
                }, status=400)
            
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                posts = posts.filter(date_posted__lte=date_to)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid date format for date_to'
                }, status=400)
            
        #Apply engagement filters if provided
        if min_likes:
            try:
                min_likes = int(min_likes)
                posts = posts.filter(num_likes__gte=min_likes)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid min_likes value'
                }, status=400)
            
        if min_comments:
            try:
                min_comments = int(min_comments)
                posts = posts.filter(num_comments__gte=min_comments)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid min_comments value'
                }, status=400)
            
        if min_shares:
            try:
                min_shares = int(min_shares)
                posts = posts.filter(num_shares__gte=min_shares)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid min_shares value'
                }, status=400)
            
        if min_saves:
            try:
                min_saves = int(min_saves)
                posts = posts.filter(num_saves__gte=min_saves)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid min_saves value'
                }, status=400)
            
        #Get posts data
        posts_data = [
            {
                'id': post.post_ID,
                'date_posted': post.date_posted,
                'post_link': post.post_link,
                'likes': post.num_likes,
                'comments': post.num_comments,
                'shares': post.num_shares,
                'saves': post.num_saves
            }
            for post in posts
        ]
        return JsonResponse({
            'success': True,
            'data': posts_data,
            'message': 'Posts retrieved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'data': posts_data,
            'message': f'Error retrieving posts: {str(e)}'
        }, status=500)
    

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
