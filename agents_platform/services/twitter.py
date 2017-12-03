import time
import datetime
import logger
import tweepy
from services import utils
from agents_platform import settings


# twitter_subscriptions = settings.Storage.twitter_subscriptions


class TwitterStream(tweepy.StreamListener):

    def __init__(self):
        super(TwitterStream, self).__init__()
        self.auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(self.auth)
        self.last_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.data = []

    # def on_data(self, raw_data):
    #     state = super(TwitterStream, self).on_data(raw_data)
    #     if not state:
    #         return state
    #     re

    def on_status(self, tweet):
        self.handle_result(tweet)
        return True

    @utils.postpone
    def handle_result(self, tweet):
        twitter_subscriptions = utils.read_data('tw_subscriptions.json')
        for keyword in twitter_subscriptions:
            print(keyword)
            if keyword.lower() in tweet.text.lower():
                if datetime.datetime.now() - self.last_time <= datetime.timedelta(seconds=5):
                    self.data.append(tweet)
                    print("not yet time " + tweet.text)
                    return
                self.last_time = datetime.datetime.now()
                #call interface function with tweet and twitter_subscriptions[keyword]
                for tweet in self.data[:15]:
                    print(tweet.text)

    def on_error(self, status_code):
        if status_code == 420:
            return False


class TwitterAPI(object):
    RECENT, POPULAR, MIXED = 'recent', 'popular', 'mixed'

    def __init__(self):
        self.auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(self.auth)

    def fetch_trends(self, woeid=1, exclude=""):
        result = self.api.trends_place(id=woeid, exclude=exclude)
        return result[0]

    def search(self, query, max_tweets, count=100, lang='en', show_user=False, **kwargs):
        if 'retweet' not in kwargs or not kwargs['retweet']:
            query += " -filter:retweets"
        result_type = kwargs["result_type"] if "result_type" in kwargs else self.RECENT
        tweet_count = 0
        max_id = -1
        since_id = None
        while tweet_count < max_tweets:
            try:
                if max_id <= 0:
                    if not since_id:
                        new_tweets = self.api.search(q=query, count=count, lang=lang,
                                                     show_user=show_user,
                                                     result_type=result_type)

                    else:
                        new_tweets = self.api.search(q=query, count=count, lang=lang,
                                                     since_id=since_id,
                                                     show_user=show_user,
                                                     result_type=result_type)
                else:
                    if not since_id:
                        new_tweets = self.api.search(q=query, count=count,
                                                     max_id=str(max_id-1),
                                                     show_user=show_user,
                                                     result_type=result_type)
                    else:
                        new_tweets = self.api.search(q=query, count=count,
                                                     max_id=str(max_id - 1),
                                                     since_id=since_id,
                                                     show_user=show_user,
                                                     result_type=result_type)
                if not new_tweets:
                    logger.info(__name__, "No new tweets found")
                    break
                # since_id = new_tweets[-1].id
                max_id = new_tweets[-1].id
                tweet_count += len(new_tweets)
                if max_tweets - count <= tweet_count < max_tweets:
                    result_type = self.POPULAR
                return new_tweets
            except tweepy.RateLimitError:
                logger.warning(__name__, "Rate limit error")
                time.sleep(15 * 60)
            except tweepy.TweepError as e:
                logger.error(__name__, "TweepError: {}".format(e))
                break


