from layout import layouts
from own_adapter.board import Board
from own_adapter.agent import get_agent


def vk_handler(data, board):
    board = board[0]
    news_agent = get_agent()
    bd = Board.get_board_by_id("/boards/" + board, news_agent.get_platform_access(), need_name=True)

    elements = bd.get_elements()
    for el in elements:
        board.remove_element(el.get_url())

    for el in layouts[min(10, len(data))].values():
        board.add_element(el[0], el[1], el[2], el[3], "")

    elements = bd.get_elements()
    idx = 0
    for post in data[:len(elements)]:
        elements.get(idx).put_link(post['event_url'])
        idx += 1


def tw_handler(data, board):
    board = board[0]
    news_agent = get_agent()
    bd = Board.get_board_by_id("/boards/" + board, news_agent.get_platform_access(), need_name=True)

    elements = bd.get_elements()
    for el in elements:
        board.remove_element(el.get_url())

    for el in layouts[min(10, len(data))].values():
        board.add_element(el[0], el[1], el[2], el[3], "")

    elements = bd.get_elements()
    idx = 0
    links = list(map(lambda x: "https://twitter.com/%s/status/%s" % (x.author.name, x.id_str), data))
    for link in links[:len(elements)]:
        elements.get(idx).put_link(link)
        idx += 1
