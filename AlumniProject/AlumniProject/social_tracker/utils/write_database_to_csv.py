import csv
from django.http import HttpResponse
from social_tracker.models import Post

def export_posts_to_csv():
    """
    Exports all post data from the Post model into a CSV file.
    """
    #creates HTTP response object that is CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="posts.csv"' #attachment content-disposition tells browser to download the file

    
    headers = ['post_ID', 'date_posted', 'post_link', 'num_likes', 'num_comments']

    writer = csv.writer(response)
    writer.writerow(headers) 

    #get all posts from database
    posts = Post.objects.all()

    #qrite each post into the CSV
    for post in posts:
        writer.writerow([
            post.post_ID,
            post.date_posted,
            post.post_link,
            post.num_likes,
            post.num_comments
        ])

    #returns the downloadable csv file
    return response