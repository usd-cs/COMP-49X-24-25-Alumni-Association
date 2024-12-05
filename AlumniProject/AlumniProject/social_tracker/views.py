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
    Saves the provided access token, ensuring only one exists.
    """
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request."}, status=405)

    try:
        data = json.loads(request.body)
        access_token_value = data.get("access_token")

        if not access_token_value:
            return JsonResponse({"message": "Access token required."}, status=400)

        #save new access token- save function should delete old one automatically in the model
        access_token = AccessToken(token=access_token_value)
        access_token.save()

        return JsonResponse({"message": "Access token saved successfully."})
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid token."}, status=400)


def get_posts_view(request):
    access_token = AccessToken.objects.get()
    result = get_instagram_posts(access_token.token)
    return JsonResponse({'message': result})

def export_csv_view(request):
    return export_posts_to_csv()