from datetime import timedelta

import pytest

from busy_beaver.apps.retweeter.cli import poll_twitter
from busy_beaver.apps.retweeter.workflow import (
    LAST_TWEET_KEY,
    fetch_tweets_post_to_slack,
)
from busy_beaver.toolbox import utc_now_minus
from tests._utilities import FakeSlackClient

MODULE_TO_TEST = "busy_beaver.apps.retweeter.workflow"


@pytest.fixture
def patched_twitter(patcher):
    class FakeTwitter:
        def __init__(self, tweets):
            self.tweets = tweets

        def get_user_timeline(self, username):
            return self.tweets

    def _wrapper(tweets):
        fake_twitter = FakeTwitter(tweets)
        patcher(MODULE_TO_TEST, namespace="twitter", replacement=fake_twitter)

    return _wrapper


@pytest.fixture
def patched_slack(patcher):
    obj = FakeSlackClient()
    return patcher(MODULE_TO_TEST, namespace="SlackClient", replacement=obj)


# Technically it's an integration test (tests more than one function)
# but it's a unit test that should be around a class
# TODO make the retweeter module into a class
@pytest.mark.integration
def test_fetch_tweets_post_to_slack(
    mocker, factory, kv_store, patched_twitter, patched_slack
):
    """
    GIVEN: 3 tweets to post (2 within the window)
    WHEN: fetch_tweets_post_to_slack is called
    THEN: we post one tweet
    """
    # Arrange
    installation = factory.SlackInstallation(workspace_id="abc")
    kv_store.put_int(installation.id, LAST_TWEET_KEY, 0)
    tweets = [
        factory.Tweet(id=3, created_at=utc_now_minus(timedelta())),
        factory.Tweet(id=2, created_at=utc_now_minus(timedelta(days=1))),
        factory.Tweet(id=1, created_at=utc_now_minus(timedelta(days=1))),
    ]
    patched_twitter(tweets)

    # Act
    fetch_tweets_post_to_slack(installation, "test_channel", "test_username")

    # Assert
    slack_adapter_initalize_args = patched_slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert installation.bot_access_token in args

    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "test_username/statuses/1" in args[0]
    assert "test_channel" in kwargs["channel"]


##########
# Test CLI
##########
@pytest.mark.end2end
def test_poll_twitter(
    mocker, runner, factory, kv_store, patched_twitter, patched_slack
):
    """
    GIVEN: 3 tweets to post (2 within the window)
    WHEN: poll_twitter is called
    THEN: we post one tweet
    """
    # Arrange
    installation = factory.SlackInstallation(workspace_id="abc")
    bot_access_token = installation.bot_access_token
    kv_store.put_int(installation.id, LAST_TWEET_KEY, 0)
    tweets = [
        factory.Tweet(id=3, created_at=utc_now_minus(timedelta())),
        factory.Tweet(id=2, created_at=utc_now_minus(timedelta(days=1))),
        factory.Tweet(id=1, created_at=utc_now_minus(timedelta(days=1))),
    ]
    patched_twitter(tweets)

    # Act
    runner.invoke(
        poll_twitter,
        ["--channel_name", "test_channel", "--workspace", installation.workspace_id],
    )

    # Assert
    slack_adapter_initalize_args = patched_slack.mock.call_args_list[0]
    args, kwargs = slack_adapter_initalize_args
    assert bot_access_token in args

    post_message_args = patched_slack.mock.call_args_list[-1]
    args, kwargs = post_message_args
    assert "ChicagoPython/statuses/1" in args[0]
    assert "test_channel" in kwargs["channel"]
