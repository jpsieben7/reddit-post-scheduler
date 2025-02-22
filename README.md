# reddit-post-scheduler

A versatile Python script for scheduling all sort of reddit posts.

# Features

- Create a reddit post of any type: link, text, title, image, or video
- Option to initialize the post with a comment under it
- Options to flair the post and flag it as spoiler and nsfw
- If you are a moderator, options to sticky, distinguish, and lock the post (and its comment), and to set the suggested
  sort or enable contest mode.
- Can also schedule comments to existing threads

# Setup

Go to your [app preferences](https://www.reddit.com/prefs/apps). Click the "Create app" or "Create another app" button.
Fill out the form like so:

- **name:** PostScheduler
- **App type:** Choose the **script** option
- **description:** A versatile Python script for scheduling all sort of reddit posts.
- **about url:** https://github.com/jpsieben7/reddit-post-scheduler
- **redirect url:** http://localhost:8080

Hit the "create app" button. Make note of the client ID and client secret.

Edit `credentials.json` to include your username, password, client ID, and client secret.

# Scheduling Posts

This app is designed to be scheduled to run daily at whatever time you like posting stuff. It will parse through the
post queue and post everything that corresponds with that days date.

Any posts that you would like to schedule should go in `postqueue.json`. The format is pretty straightforward and some
examples are already there.

```
{
  "posts": [
    {
      "sub": "subredditname",
      "title": "titletext",
      "text": "bodytext",
      "comment_text": "commenttext",
      "date": "8,11"
    },
    {
      "sub": "subredditname",
      "title": "titletext",
      "link": "linkurl",
      "comment_text": "commenttext",
      "date": "8,18"
    },
    {
      "sub": "subredditname",
      "title": "titletext",
      "image": "path/to/image",
      "comment_text": "commenttext",
      "date": "7,20"
    }
  ]
}
```

All that this file essentially needs is a list called `post` containing a dictionary for each post.

The following properties are required depending on the type of posts.

- `date` The date you want the post to go up on. Needs to be in "M,D" format. Required for all posts and comments.
- `sub` The subreddit to post to. Required for all posts.
- `title` The title of the post. Required for all posts.
- `text` The body text. Required for all text posts. (but not for a title-only post)
- `link` The url of the link. Required for all link posts.
- `image` The path to the image you want to upload. Required for all image posts, and will be used as the thumbnail if
  done on a video post.
- `video` The path to the video you want to upload. Required for all video posts.
- `parent` - The parent id of the comment or post you want to reply to. This is required if you're just making a
  comment, but not a post.
- `comment_text` - The text of the comment. This is required if you are making a comment, regardless of whether you are
  also making a post.

The following properties are optional strings. (some need moderator permissions)

- `flair_id` The uuid of the flair you want to use.
- `flair_text` The text of the flair you want to use.
- `collection_id` The uuid of the collection you want to post to.
- `sort` The suggested sort to apply.

The following properties are also optional, but take booleans, not strings. These all default to False, so only include
them if setting to True. Some need moderator permissions.

- `spoiler`
- `nsfw`
- `dont_notify` Disable inbox notifications
- `contest` Enable contest mode
- `lock`
- `distinguish`
- `sticky`
- `lock_comment`
- `distinguish_comment`
- `sticky_comment`
- `wait` If the ratelimit is reached, wait the required time (~10 mins) and try again.

# Setting this up with pythonanywhere

If you do not have a server, this can be set up for free on pythonanwhere. It meets their daily limits.

- Make an account at https://www.pythonanywhere.com
- Navigate to the "Files" page
- Click "Upload a File", and upload `postscheduler.py` and `postqueue.py`.
- Click on "Open Bash console here" and wait for the console to finish initializing.
- Type in `python3 -m pip install praw -U --user`.
- Navigate to the tasks page.
- Start a new daily task with the command `python3 postscheduler.py` set to run at the time that you want your stuff to
  post. (Note that the server time listed on the page may be different from your own time.)
