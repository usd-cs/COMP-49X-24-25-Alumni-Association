from django.http import JsonResponse
from .utils.get_instagram_data import get_instagram_posts
from .utils.write_database_to_csv import export_posts_to_csv
from django.views.decorators.csrf import csrf_exempt
import json

ACCESS_TOKEN = None

@csrf_exempt
def save_access_token(request):
    """
    Saves the provided access token.
    """
    global ACCESS_TOKEN
    if request.method != "POST":
        #bad request
        return JsonResponse({"message": "Invalid request."}, status=405)

    try:
        data = json.loads(request.body)
        ACCESS_TOKEN = data.get("access_token")
        if ACCESS_TOKEN:
            #success message
            return JsonResponse({"message": "Access token saved successfully."})
        #blank text box
        return JsonResponse({"message": "Access token required."}, status=400)
    except json.JSONDecodeError:
        #invalid token
        return JsonResponse({"message": "Invalid token."}, status=400)


def get_posts_view(request):
    result = get_instagram_posts(ACCESS_TOKEN)
    return JsonResponse({'message': result})

def export_csv_view(request):
    return export_posts_to_csv()