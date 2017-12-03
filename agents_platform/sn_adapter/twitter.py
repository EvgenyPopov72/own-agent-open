import tweepy

from settings import TW_ACCESS_TOKEN_SECRET, TW_CONSUMER_SECRET, TW_CONSUMER_KEY, TW_ACCESS_TOKEN


class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler(TW_CONSUMER_KEY, TW_CONSUMER_SECRET)
        auth.set_access_token(TW_ACCESS_TOKEN, TW_ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def get_msg_by_tags(self, tags, qt=10):
        return tweepy.Cursor(self.api.search, q=tags).items(qt)
