import graphic
import color

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

FRAME_RATE = 30

CAPTION = 'Netgammon'

BACKGROUND_IMAGE = 'assets/image/background.png'

WHITE_PIECE_IMAGE = 'assets/image/white_piece.png'
RED_PIECE_IMAGE = 'assets/image/red_piece.png'

WHITE_FROM_IMAGE = 'assets/image/white_from_point.png'
RED_FROM_IMAGE = 'assets/image/red_from_point.png'

TO_IMAGE = 'assets/image/to_point.png'

HISTORY_FILENAME = 'backgammon_history.txt'

VISIBLE_NUMBER = 7

DIE_IMAGES = {
    color.WHITE: {
        1: 'assets/image/white_dice_1.png',
        2: 'assets/image/white_dice_2.png',
        3: 'assets/image/white_dice_3.png',
        4: 'assets/image/white_dice_4.png',
        5: 'assets/image/white_dice_5.png',
        6: 'assets/image/white_dice_6.png'
    },
    color.RED: {
        1: 'assets/image/red_dice_1.png',
        2: 'assets/image/red_dice_2.png',
        3: 'assets/image/red_dice_3.png',
        4: 'assets/image/red_dice_4.png',
        5: 'assets/image/red_dice_5.png',
        6: 'assets/image/red_dice_6.png'
    }
}

BANNER_IMAGES = {
    1: 'assets/image/banner1.png',
    2: 'assets/image/banner2.png',
    3: 'assets/image/banner3.png',
    4: 'assets/image/banner4.png',
    5: 'assets/image/banner5.png',
    6: 'assets/image/banner6.png',
    7: 'assets/image/banner7.png',
    8: 'assets/image/banner8.png',
}

MENU_BUTTON_IMAGES = {
    graphic.LOCAL: 'assets/image/local_pvp.png',
    graphic.STATE: {
        color.RED: 'assets/image/red_wins.png',
        color.WHITE: 'assets/image/white_wins.png',
        graphic.DISCONNECT: 'assets/image/disconnect.png',
        graphic.NETWORK_COLOR_WHITE: 'assets/image/color_white.png',
        graphic.NETWORK_COLOR_RED: 'assets/image/color_red.png'
    },
    graphic.NET: {
        'press': 'assets/image/net_pvp.png',
        'pressed': 'assets/image/searching.png'
    }
}

HOST = '192.168.0.100'
PORT = 34299
