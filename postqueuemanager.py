###############################################################################
# Notes:
# every item is assumed None/False if left out (except "wait" which defaults to true)
# everything is a string and should be entered in quotes except the following,
# which should just be the word True without quotes:
#   spoiler, nsfw, lock, contest, dont_notify, distinguish, sticky, lock_comment, distinguish_comment, sticky_comment
# date is "M,D"
# text should be "" for an empty title-only post
# image and video are path strings
# a video post can use image to set a thumbnail
# link is a url string
# parent is the ID of the comment or post you want to reply to (if not making a post)
# A lot of features will not work if you aren't a moderator

# link post:		date, sub, title, link
# text post:		date, sub, title, text
# title post:	date, sub, title
# image post:	date, sub, title, image
# video post:	date, sub, title, video, [image (for thumbnails)]
# comment:		date, parent, comment_text
#
# Every post (but not comment) can have flairs, collections, and suggested sorts
#   set using flair_id, flair_text, collection_id, and sort.
# They can also have the following booleans set to True (without quotes):
#   spoiler, nsfw, lock, contest, dont_notify, distinguish, sticky, wait
#
# wait doesn't change the post but will tell the scheduler to wait for any ratelimit to finish
#   and retry a post before continuing. True by default
#
# Every post can use the comment_text property to leave a comment under the post.
# If comment_text is used, then the following booleans can be set:
#   lock_comment, distinguish_comment, and sticky_comment
#
# All posts should be inside curly braces, followed by the word (in quotes) "posts" and a colon,
# then enclosed in square brackets. So like:
# { "posts": [ <Posts go here, grouped by curly brackets and separated by commas> ] }
# Each post should be inside curly braces and separated by commas.
# Each property should be designated with `"propertyname": value` and be seperated by commas.

# Examples
#
# Post example:
# {
#   "sub": "pics",
#   "title": "Monday Meme Megathread",
#   "text": "**Please post all of your memes in this thread.**\n\rMemes found anywhere else will be removed.",
#   "flair_text": "megathread",
#   "sticky": True,
#   "distinguish": True,
#   "dont_notify": True,
#   "comment": "[Here's a fun meme to start things off](https://i.imgur.com/97i2mJS.jpg)",
#   "date": "9,30"
# }

"""
Example postqueue.json for reference:

{
  "posts": [
    {
        "sub": "subreddit_name",
        "title": "title_text",
        "link": "link_url",
        "comment_text": "comment_text",
        "date": "8,18"
    },
    {
        "sub": "subreddit_name",
        "title": "title_text",
        "image": "path/to/image",
        "comment_text": "comment_text",
        "date": "7,20"
    }
  ]
}
"""

import json
from typing import List, Dict

posts_file_path = "./postqueue.json"


def read_json_from_file(path: str) -> Dict:
    with open(path, "r+") as f:
        return json.loads(f.read())


class PostQueueManager:
    posts: List[Dict]

    def __init__(self):
        self.posts = read_json_from_file(posts_file_path)["posts"]

    def remove_post(self, post_to_remove: Dict):
        self.posts.remove(post_to_remove)

    def get_posts_as_pretty_printed_json(self) -> str:
        posts_out = {"posts": self.posts}
        return json.dumps(posts_out, indent=4)

    def write_posts_to_file(self):
        with open(posts_file_path, "w+") as f:
            f.write(self.get_posts_as_pretty_printed_json())


###############################################################################
