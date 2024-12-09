from django.http import HttpResponse
import csv
from .models import Post

def download_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="social_media_data.csv"'},
    )
    writer = csv.writer(response)
    
    writer.writerow([
        'Post ID', 
        'Date Posted', 
        'Post Link', 
        'Likes', 
        'Comments', 
        'Shares', 
        'Saves'
    ])
    
    # Add ordering to make results consistent
    posts = Post.objects.all().order_by('post_ID')
    for post in posts:
        writer.writerow([
            post.post_ID,
            post.date_posted,
            post.post_link,
            post.num_likes,
            post.num_comments,
            post.num_shares,
            post.num_saves
        ])
    
    return response
