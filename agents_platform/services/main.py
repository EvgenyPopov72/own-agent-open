import time
import logger
import tweepy
import settings
from agents_platform.services import twitter, vk

twitter_listener = twitter.TwitterStream()
twitter_stream = tweepy.Stream(auth=twitter_listener.auth, listener=twitter_listener)

# logger = logging.getLogger(__name__)

twitter_subscriptions = settings.twitter_subscriptions
vk_subscriptions = settings.vk_subscriptions


def run():
    # subscribe_keyword_twitter('Trump', 4567)
    subscribe_keyword_vk('Путин', 9000)
    print("Check what the fuck is happening")


def start_twitter():
    pass


def subscribe_keyword_vk(keyword, element):
    if keyword in vk_subscriptions:
        vk_subscriptions[keyword].append(element)
    else:
        vk_subscriptions[keyword] = [element]

    api = vk.api
    api.del_all_rules()
    for keyword in vk_subscriptions:
        api.add_rules(keyword, keyword)
    rules = api.get_rules()
    for rule in rules:
        print("{tag:15}:{value}".format(**rule))

    api.start()

    # @api.stream
    # def my_func(event):
    #     if event['type'] == 'post':
    #         for tag in event['tags']:
    #             if tag in vk_subscriptions:
    #                 # call vk interface method
    #                 print(event)
        # print("[{}]: {}".format(event['author']['id'], event['text']))




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
