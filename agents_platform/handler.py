from layout import layouts
from own_adapter.board import Board
from social_own_agent import get_agent


def vk_handler(data, board):
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
        elements.get(idx).put_link(data.get(idx))
        idx += 1


def tw_handler(links):
    pass