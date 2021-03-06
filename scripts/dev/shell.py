import os

from busy_beaver import create_app
from busy_beaver.common.wrappers import (
    GitHubClient,
    KeyValueStoreClient,
    MeetupClient,
    SlackClient,
    TwitterClient,
    YouTubeClient,
)
from busy_beaver.extensions import db, rq  # noqa
from busy_beaver.models import *  # noqa

# create flask application context
app = create_app()
ctx = app.app_context()
ctx.push()

# configure adapters
OAUTH_TOKEN = os.getenv("GITHUB_OAUTH_TOKEN")
github = GitHubClient(OAUTH_TOKEN)

SLACK_TOKEN = os.getenv("SLACK_BOTUSER_OAUTH_TOKEN")
slack = SlackClient(SLACK_TOKEN)

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
twitter = TwitterClient(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = YouTubeClient(api_key=YOUTUBE_API_KEY)

MEETUP_API_KEY = os.getenv("MEETUP_API_KEY")
MEETUP_GROUP_NAME = "_ChiPy_"
meetup = MeetupClient(MEETUP_API_KEY)

kv = KeyValueStoreClient()

# log to console
display_text = "Busy Beaver Development Shell"
num_char = len(display_text)
print("*" * num_char)
print(display_text)
print("*" * num_char)
