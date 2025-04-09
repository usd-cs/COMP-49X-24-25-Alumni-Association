from social_tracker.models import Post


def get_two_hour_block(post):
    """
    Returns the 2-hour time block when a post was made.

    Args:
        post (Post): A Post object with a valid date_posted field.

    Returns:
        str: A time block label like "12am-2am", or "Unknown" if missing.
    """
    if not post.date_posted:
        return "Unknown"

    hour = post.date_posted.hour
    blocks = [
        "12am-2am", "2am-4am", "4am-6am", "6am-8am",
        "8am-10am", "10am-12pm", "12pm-2pm", "2pm-4pm",
        "4pm-6pm", "6pm-8pm", "8pm-10pm", "10pm-12am"
    ]
    return blocks[hour // 2]


def sort_by_block_order(item):
    """
    Sorts result dictionaries by chronological 2-hour time block.

    Args:
        item (dict): A dictionary that contains a 'block' key.

    Returns:
        int: The index of the block in the expected order.
    """
    block_order = [
        "12am-2am", "2am-4am", "4am-6am", "6am-8am",
        "8am-10am", "10am-12pm", "12pm-2pm", "2pm-4pm",
        "4pm-6pm", "6pm-8pm", "8pm-10pm", "10pm-12am"
    ]
    block_index = {block: index for index, block in enumerate(block_order)}
    return block_index.get(item["block"], -1)


def get_avg_likes_by_time_block():
    """
    Calculates average likes per 2-hour time block.

    Returns:
        tuple: Total post count and a list of dicts with 'block' and 'avg_likes'.
    """
    like_totals = {}
    post_counts = {}
    total_posts = 0

    for post in Post.objects.all():
        block = get_two_hour_block(post)
        if block == "Unknown":
            continue

        total_posts += 1

        if block not in like_totals:
            like_totals[block] = 0
            post_counts[block] = 0

        like_totals[block] += post.num_likes
        post_counts[block] += 1

    results = []
    for block in like_totals:
        avg = like_totals[block] / post_counts[block]
        results.append({
            "block": block,
            "avg_likes": round(avg, 2),
        })

    results.sort(key=sort_by_block_order)
    return total_posts, results


def get_avg_comments_by_time_block():
    """
    Calculates average comments per 2-hour time block.

    Returns:
        tuple: Total post count and a list of dicts with 'block' and 'avg_comments'.
    """
    comment_totals = {}
    post_counts = {}
    total_posts = 0

    for post in Post.objects.all():
        block = get_two_hour_block(post)
        if block == "Unknown":
            continue

        total_posts += 1

        if block not in comment_totals:
            comment_totals[block] = 0
            post_counts[block] = 0

        comment_totals[block] += post.num_comments
        post_counts[block] += 1

    results = []
    for block in comment_totals:
        avg = comment_totals[block] / post_counts[block]
        results.append({
            "block": block,
            "avg_comments": round(avg, 2),
        })

    results.sort(key=sort_by_block_order)
    return total_posts, results


def get_avg_saves_by_time_block():
    """
    Calculates average saves per 2-hour time block.

    Returns:
        tuple: Total post count and a list of dicts with 'block' and 'avg_saves'.
    """
    save_totals = {}
    post_counts = {}
    total_posts = 0

    for post in Post.objects.all():
        block = get_two_hour_block(post)
        if block == "Unknown":
            continue

        total_posts += 1

        if block not in save_totals:
            save_totals[block] = 0
            post_counts[block] = 0

        save_totals[block] += post.num_saves
        post_counts[block] += 1

    results = []
    for block in save_totals:
        avg = save_totals[block] / post_counts[block]
        results.append({
            "block": block,
            "avg_saves": round(avg, 2),
        })

    results.sort(key=sort_by_block_order)
    return total_posts, results


def get_avg_shares_by_time_block():
    """
    Calculates average shares per 2-hour time block.

    Returns:
        tuple: Total post count and a list of dicts with 'block' and 'avg_shares'.
    """
    share_totals = {}
    post_counts = {}
    total_posts = 0

    for post in Post.objects.all():
        block = get_two_hour_block(post)
        if block == "Unknown":
            continue

        total_posts += 1

        if block not in share_totals:
            share_totals[block] = 0
            post_counts[block] = 0

        share_totals[block] += post.num_shares
        post_counts[block] += 1

    results = []
    for block in share_totals:
        avg = share_totals[block] / post_counts[block]
        results.append({
            "block": block,
            "avg_shares": round(avg, 2),
        })

    results.sort(key=sort_by_block_order)
    return total_posts, results
