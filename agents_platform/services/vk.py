import json
import datetime
from agents_platform import settings
# from handler import vk_handler
from services import utils
from vkstreaming import Streaming

# vk_subscriptions = settings.vk_subscriptions
api = Streaming("streaming.vk.com", settings.VK_KEY)
last_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
data = []


@api.stream
def my_func(event):
    handle_result(event)
    return


@utils.postpone
def handle_result(event):
    print(json.dumps(event, indent=4, sort_keys=True, ensure_ascii=False))
    vk_subscriptions = utils.read_data('vk_subscriptions.json')
    if event['event_type'] == 'post':
        for tag in event['tags']:
            if tag in vk_subscriptions:
                global last_time
                if datetime.datetime.now() - last_time <= datetime.timedelta(seconds=5):
                    data.append(event)
                else:
                    last_time = datetime.datetime.now()
                    # call interface function with tweet and twitter_subscriptions[keyword]
                    from agents_platform.handler import vk_handler
                    vk_handler(data, vk_subscriptions['tag'])
                    for event in data:
                        print(event)
                    data = []