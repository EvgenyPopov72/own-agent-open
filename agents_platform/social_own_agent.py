import json
import re
import threading
import time
import traceback

import websocket

import logger
from layout import layouts
from own_adapter.agent import Agent
from own_adapter.board import Board
from own_adapter.element import Element
from services import main, vk
from own_adapter.agent import get_agent
from settings import AGENT_LOGIN, AGENT_PASSWORD
from sn_adapter.twitter import Twitter

CURRENT_LOGGER = 'aeronaut\'s logger'
twitter_api = None


def __show_tweets(element, links):
    logger.debug(CURRENT_LOGGER, "show tweets")

    message = "show tweets"
    element.get_board().put_message(message)

    for tw in links:
        element.put_link(tw)


def __run_on_element(element, links):
    """Running on a target element"""
    try:
        __show_tweets(element, links)
    except Exception as ex:
        logger.exception(CURRENT_LOGGER, 'Error: could not process an element. Element id: {}. Exception message: {}.\n'
                                         '{}'.format(element.get_id(), str(ex), traceback.format_exc()))


def __run_on_board(board):
    """Runs the agent on elements of a board"""
    elements = board.get_elements()
    for element in elements:
        __run_on_element(element)


def periodical_update():
    """Does periodical work with a predefined last_time interval"""
    time_interval = 86400

    while True:
        time.sleep(time_interval)

        agent = get_agent()
        boards = agent.get_boards()
        for board in boards:
            __run_on_board(board)
        logger.info(CURRENT_LOGGER, 'Daily news update is done.')


# def get_agent():
#     """Returns the current agent"""
#     login = AGENT_LOGIN
#     password = AGENT_PASSWORD
#
#     platform_access = PlatformAccess(login, password)
#     agent = Agent(platform_access)
#
#     return agent


def on_websocket_message(ws, message):
    """Processes websocket messages"""
    message_dict = json.loads(message)
    content_type = message_dict['contentType']
    message_type = content_type.replace('application/vnd.uberblik.', '')

    logger.debug(CURRENT_LOGGER, message)

    if message_type == 'liveUpdateElementCaptionEdited+json':
        element_caption = message_dict['newCaption']
        if re.match(pattern='(@twitter:.+)|(@tw:.+)', string=element_caption):
            tags = element_caption.split(":")[-1].split()

            twitter_api = Twitter()
            twitts = twitter_api.get_msg_by_tags(" ".join(tags))
            links = map(lambda x: "https://twitter.com/%s/status/%s" % (x.author.name, x.id_str), twitts)

            logger.debug(CURRENT_LOGGER, "twitter keywords: %s" % tags)
            element_id = message_dict['path']
            news_agent = get_agent()
            board_id = '/'.join(element_id.split('/')[:-2])
            board = Board.get_board_by_id(board_id, news_agent.get_platform_access(), need_name=False)
            element = Element.get_element_by_id(element_id, news_agent.get_platform_access(), board)

            # subscribe_keyword_vk(tags, board_id.split('/')[-1] + '_' + element_id)

    elif message_type == 'liveUpdateActivitiesUpdated+json':
        logger.debug(CURRENT_LOGGER, "liveUpdateActivitiesUpdated")

        element_id = message_dict['path']
        news_agent = get_agent()
        board_id = '/boards/' + element_id.split('/')[-1]
        board = Board.get_board_by_id(board_id, news_agent.get_platform_access(), need_name=False)
        # element = Element.get_element_by_id(element_id, news_agent.get_platform_access(), board)
        msg = board.get_last_message()
        logger.debug(CURRENT_LOGGER, msg)

        if re.match(pattern='(/subscribe .+)', string=msg):
            elements = msg.split()
            tag = msg.split()[-1].lstrip("#")
            sn_account = tuple(map(lambda x: x.strip("@"), msg.split()[1:-1]))
            board = board_id.split('/')[-1]

            try:
                if 'tw' in sn_account:
                    if main.twitter_stream:
                        main.twitter_stream.running = False
                    main.subscribe_keyword_twitter(keyword=tag, element=board)
                if 'vk' in sn_account:
                    if vk.api:
                        vk.api.stop()
                    main.subscribe_keyword_vk(keyword=tag, element=board)
            except Exception as e:
                logger.error(CURRENT_LOGGER, e)

        elif re.match(pattern='(/unsubscribe .+)', string=msg):
            pass


def on_websocket_error(ws, error):
    """Logs websocket errors"""
    logger.error(CURRENT_LOGGER, error)


def on_websocket_open(ws):
    """Logs websocket openings"""
    logger.info(CURRENT_LOGGER, 'Websocket is open')


def on_websocket_close(ws):
    """Logs websocket closings"""
    logger.info(CURRENT_LOGGER, 'Websocket is closed')


def open_websocket():
    """Opens a websocket to receive messages from the boards about events"""
    agent = get_agent()
    # getting the service url without protocol name
    platform_url_no_protocol = agent.get_platform_access().get_platform_url().split('://')[1]
    access_token = agent.get_platform_access().get_access_token()
    url = 'ws://{}/opensocket?token={}'.format(platform_url_no_protocol, access_token)

    ws = websocket.WebSocketApp(url,
                                on_message=on_websocket_message,
                                on_error=on_websocket_error,
                                on_open=on_websocket_open,
                                on_close=on_websocket_close)
    ws.run_forever()


def run():
    websocket_thread = None
    updater_thread = None

    while True:
        # opening a websocket for catching server messages
        if websocket_thread is None or not websocket_thread.is_alive():
            try:
                websocket_thread = threading.Thread(target=open_websocket)
                websocket_thread.start()
            except Exception as e:
                logger.exception(CURRENT_LOGGER, 'Could not open a websocket. Exception message: {}'.format(str(e)))

        # periodical updates
        if updater_thread is None or not updater_thread.is_alive():
            try:
                updater_thread = threading.Thread(target=periodical_update)
                updater_thread.start()
            except Exception as e:
                logger.exception(CURRENT_LOGGER, 'Could not start updater. Exception message: {}'.format(str(e)))

        # wait until next check
        time.sleep(10)


if __name__ == '__main__':
    run()
