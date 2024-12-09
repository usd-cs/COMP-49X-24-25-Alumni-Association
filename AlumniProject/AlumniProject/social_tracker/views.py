from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

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
