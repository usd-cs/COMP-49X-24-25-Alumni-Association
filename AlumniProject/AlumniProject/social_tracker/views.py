from django.http import JsonResponse
from .utils.get_instagram_data import get_instagram_posts
from .utils.write_database_to_csv import export_posts_to_csv
from django.views.decorators.csrf import csrf_exempt
from .models import AccessToken
import json

ACCESS_TOKEN = None


@csrf_exempt
def save_access_token(request):
    """
    Accepts POST requests containing an access token and saves it to
    the database. It ensures that only one access token exists and
    automatically replaces the old tokenwhen a new one is provided.

    Parameters:
    - request: HttpRequest object that contains the access token.

    Returns:
    - JsonResponse: A JSON response indicating success or failure
        - 200: If access token is saved successfully.
        - 400: If access token is missing or invalid.
        - 405: If the request is invalid.
    """
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request."}, status=405)

    try:
        data = json.loads(request.body)
        access_token_value = data.get("access_token")

        if not access_token_value:
            return JsonResponse(
                {"message": "Access token required."}, status=400
            )

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
