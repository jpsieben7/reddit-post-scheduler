#!/usr/bin/python3
# post flair comment sticky
import datetime
import time

import praw
from praw.exceptions import APIException
from praw.models.reddit.mixins import ReplyableMixin
from praw.reddit import Submission, Comment

import postqueuemanager
from postpayload import PostPayload
from postqueuemanager import PostQueueManager

# Credentials
reddit = praw.Reddit(**postqueuemanager.read_json_from_file("credentials.json"))

# Set to true to prevent the script from posting/commenting, but do everything else
DEBUG = False
f = open("postscheduler.log", "a+")


def log(msg):
    print(msg)
    f.write(msg)


###############################################################################
###############################################################################
###############################################################################

class RateLimitException(Exception):
    minutes_to_wait: int

    def __init__(self, minutes_to_wait):
        self.minutes_to_wait = minutes_to_wait


def get_current_day_month_string() -> str:
    return str(datetime.datetime.now().month) + "," + str(datetime.datetime.now().day)


def write_error_posting_to_log(e: Exception):
    log("\n\nError posting submission -- " + str(e))


def add_attributes_to_post(submission: Submission, pp: PostPayload):
    try:
        if pp.distinguish:
            submission.mod.distinguish()
            log("\nDistinguished")
        if pp.sticky:
            submission.mod.sticky()
            log("\nStickied")
        if pp.lock:
            submission.mod.lock()
            log("\nLocked")
        if pp.contest:
            submission.mod.contest_mode()
            log("\nEnabled Contest Mode")
        if pp.sort is not None:
            submission.mod.suggested_sort(pp.sort)
            log("\nSet suggested sort to " + pp.sort)
    except Exception as e:
        log("\n\nError attributing submission. (Are you a moderator?) -- " + str(e))


def submit_post(pp: PostPayload) -> Submission:
    submission = None
    try:
        if pp.image is None and pp.video is None:
            submission = reddit.subreddit(pp.sub).submit(pp.title, selftext=pp.text, url=pp.link,
                                                         flair_id=pp.flair_id,
                                                         flair_text=pp.flair_text, send_replies=not pp.dont_notify,
                                                         nsfw=pp.nsfw, spoiler=pp.spoiler,
                                                         collection_id=pp.collection_id)
        else:
            if pp.video is None:
                submission = reddit.subreddit(pp.sub).submit_image(pp.title, image_path=pp.image,
                                                                   flair_id=pp.flair_id,
                                                                   flair_text=pp.flair_text,
                                                                   send_replies=not pp.dont_notify,
                                                                   nsfw=pp.nsfw, spoiler=pp.spoiler,
                                                                   collection_id=pp.collection_id)
            else:
                submission = reddit.subreddit(pp.sub).submit_video(pp.title, video_path=pp.video,
                                                                   thumbnail_path=pp.image,
                                                                   flair_id=pp.flair_id, flair_text=pp.flair_text,
                                                                   send_replies=not pp.dont_notify, nsfw=pp.nsfw,
                                                                   spoiler=pp.spoiler,
                                                                   collection_id=pp.collection_id)

        log("\n\nPosted --  " + to_link(submission.permalink))
    except APIException as e:
        if e.field == "ratelimit":
            if pp.wait:
                msg = e.message.lower()
                index = msg.find("minute")
                minutes = int(msg[index - 2]) + 1 if index != -1 else 1
                log("\n\nRate limit reached. Need to wait " + str(minutes) + " minutes before retrying.")
                raise RateLimitException(minutes)
            else:
                write_error_posting_to_log(e)
                raise e
    except Exception as e:
        log("\n\nError posting submission -- " + str(e))
        raise e

    return submission


def get_comment_or_parent_as_replyable(pp: PostPayload) -> ReplyableMixin:
    submission = reddit.comment(id=pp.parent)
    try:
        submission.body
    except Exception as e:
        submission = reddit.submission(id=pp.parent)
    return submission


def reply_to_comment_or_submission(comment_or_submission, pp: PostPayload):
    try:
        comment = comment_or_submission.reply(pp.comment_text)
        log("\n\tCommented --  " + to_link(comment.permalink))
    except Exception as e:
        log("\n\tError posting comment -- " + str(e))
        raise e


def add_attributes_to_comment(comment: Comment, pp: PostPayload):
    try:
        if pp.sticky_comment:
            comment.mod.distinguish(how='yes', sticky=True)
            log("\n\tDistinguished and Stickied")
        elif pp.distinguish_comment:
            comment.mod.distinguish(how='yes')
            log("\n\tDistinguished")
        if pp.lock_comment:
            comment.mod.lock()
            log("\n\tLocked")
    except Exception as e:
        log("\n\tError attributing comment. (Are you a moderator?) -- " + str(e))
    return


def submit_post_payload(pp: PostPayload):
    replyable: ReplyableMixin

    if DEBUG:
        print("DEBUG: Skipping submission steps")
        return

    if pp.parent is None:
        submission = submit_post(pp)
        add_attributes_to_post(submission, pp)
        replyable = submission
    else:
        replyable = get_comment_or_parent_as_replyable(pp)

    if pp.comment_text is None:
        return

    comment = reply_to_comment_or_submission(replyable, pp)
    add_attributes_to_comment(comment, pp)


def is_date(target_time):
    current_time = get_current_day_month_string()
    return target_time == current_time


def to_link(permalink):
    return "https://reddit.com" + permalink


def post_posts_in_queue():
    log(f"\n---------------------\nStarted. Current date string: {get_current_day_month_string()}\n")

    post_queue_manager = PostQueueManager()
    posts = post_queue_manager.posts

    if DEBUG:
        print(f"DEBUG: Posts size: {len(posts)}")
        print(f"DEBUG: Current posts: {post_queue_manager.get_posts_as_pretty_printed_json()}")

    for post in posts:
        payload = PostPayload.from_overrides(post)

        current_date = get_current_day_month_string()

        if payload.date != current_date:
            msg = f"\nToday is {current_date} --  post is scheduled for {payload.date}\n"
            log(msg)
            continue

        if payload.link is not None:
            payload.text = None

        try:
            submit_post_payload(payload)
        except RateLimitException as e:
            time.sleep(e.minutes_to_wait * 60)
            try:
                submit_post_payload(payload)
            except Exception as e:
                write_error_posting_to_log(e)
                continue

        log(f"\nSubmitted post: {payload}\n")
        log(f"\nRemoving post from queue: {post}\n")
        post_queue_manager.remove_post(post)

    if not DEBUG:
        post_queue_manager.write_posts_to_file()
    else:
        print(f"DEBUG: Would have written to file:\n{post_queue_manager.get_posts_as_pretty_printed_json()}\n")

    log("\n\nFinished\n---------------------\n")
    f.close()


# Main
if __name__ == "__main__":
    post_posts_in_queue()
