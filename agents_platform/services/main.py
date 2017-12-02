import time
import logger
import tweepy
import settings
from agents_platform.services import twitter

twitter_listener = twitter.TwitterStream()
twitter_stream = tweepy.Stream(auth=twitter_listener.auth, listener=twitter_listener)

# logger = logging.getLogger(__name__)

twitter_subscriptions = settings.twitter_subscriptions


def run():
    subscribe_keyword_twitter('Kenneth', 4567)
    print("Check what the fuck is happening")


def start_twitter():
    pass


def unsubscribe_keyword_twitter(keyword, board):
    if keyword in twitter_subscriptions:
        if board in twitter_subscriptions[keyword]:
            twitter_subscriptions[keyword].remove(board)
            return True

    return False


def subscribe_keyword_twitter(keyword, board):
    if keyword in twitter_subscriptions:
        twitter_subscriptions[keyword].append(board)
    else:
        twitter_subscriptions[keyword] = [board]
    try:

        twitter_stream.filter(track=list(twitter_subscriptions.keys()))
    except tweepy.RateLimitError:
        print("Rate limit error")
        # time.sleep(15*60)
    except tweepy.TweepError as e:
        logger.error(__name__, "TweepError: {}".format(e))


if __name__ == '__main__':
    run()
