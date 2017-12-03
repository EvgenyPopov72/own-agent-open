import json
import datetime
from agents_platform import settings
from vkstreaming import Streaming

vk_subscriptions = settings.vk_subscriptions
api = Streaming("streaming.vk.com", settings.VK_KEY)
last_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
data = []


@api.stream
def my_func(event):
    print(json.dumps(event, indent=4, sort_keys=True, ensure_ascii=False))
    if event['event_type'] == 'post':
        for tag in event['tags']:
            if tag in vk_subscriptions:
                global last_time
                if datetime.datetime.now() - last_time <= datetime.timedelta(minutes=5):
                    data.append(event)
                else:
                    last_time = datetime.datetime.now()
                    # call interface function with tweet and twitter_subscriptions[keyword]
                    for event in data:
                        print(event)