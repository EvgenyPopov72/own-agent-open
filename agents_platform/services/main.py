import time
import logger
import json
import tweepy
import settings
from services import utils
from agents_platform.services import twitter, vk

twitter_listener = twitter.TwitterStream()
twitter_stream = tweepy.Stream(auth=twitter_listener.auth, listener=twitter_listener)

# logger = logging.getLogger(__name__)

# twitter_subscriptions = json.load(open('agent_platform/tw_subscriptions.json'))
# vk_subscriptions = settings.vk_subscriptions


def run():
    # subscribe_keyword_twitter('Trump', 4567)
    subscribe_keyword_vk('Путин', 9000)
    # print("Check what the fuck is happening")


def start_twitter():
    pass


def subscribe_keyword_vk(keyword, element):

    vk_subscriptions = utils.read_data('vk_subscriptions.json')

    if keyword in vk_subscriptions:
        vk_subscriptions[keyword].append(element)
    else:
        vk_subscriptions[keyword] = [element]
    utils.write_data('vk_subscriptions.json', vk_subscriptions)

    api = vk.api
    api.del_all_rules()
    for keyword in vk_subscriptions:
        api.add_rules(keyword, keyword)
    rules = api.get_rules()
    for rule in rules:
        print("{tag:15}:{value}".format(**rule))

    api.start()


def unsubscribe_keyword_twitter(keyword, element):
    twitter_subscriptions = utils.read_data('tw_subscriptions.json')
    if keyword in twitter_subscriptions:
        if element in twitter_subscriptions[keyword]:
            twitter_subscriptions[keyword].remove(element)
            utils.write_data('tw_subscriptions.json', twitter_subscriptions)
            return True

    return False


def subscribe_keyword_twitter(keyword, element):
    twitter_subscriptions = utils.read_data('tw_subscriptions.json')
    if keyword in twitter_subscriptions:
        twitter_subscriptions[keyword].append(element)
    else:
        twitter_subscriptions[keyword] = [element]
    utils.write_data('tw_subscriptions.json', twitter_subscriptions)
    try:

        twitter_stream.filter(track=list(twitter_subscriptions.keys()),  stall_warnings=True)
    except tweepy.RateLimitError:
        print("Rate limit error")
        # last_time.sleep(15*60)
    except tweepy.TweepError as e:
        logger.error(__name__, "TweepError: {}".format(e))


if __name__ == '__main__':
    run()
