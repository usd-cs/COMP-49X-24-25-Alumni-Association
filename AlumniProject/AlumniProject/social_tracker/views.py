from django.http import JsonResponse
from .utils.get_instagram_data import get_instagram_posts
from .utils.write_database_to_csv import export_posts_to_csv
def get_posts_view(request):
    ACCESS_TOKEN = "IGQWRNVkJNS0UycG5obmY5ekxUV1VwRkVWVVV3R0dwN29CNkc2ZA3VDa1F5cFBWR2QycU9fRVFjaDVhYTAwdXBRcUlWY1pCZA3lBSGJ4a3JPVklHZAy1QWmVocGM5bnNoVVBEYzRydEJIVGdFN2ZA6NHA3Q3dyRTAzc1EZD"
    result = get_instagram_posts(ACCESS_TOKEN)
    return JsonResponse({'message': result})

def export_csv_view(request):
    return export_posts_to_csv()