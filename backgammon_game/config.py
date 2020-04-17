from backgammon_game import color, graphic

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

FRAME_RATE = 30

CAPTION = 'Backgammon'

BACKGROUND_IMAGE = 'backgammon_game/assets/image/background.png'

WHITE_PIECE_IMAGE = 'backgammon_game/assets/image/white_piece.png'
RED_PIECE_IMAGE = 'backgammon_game/assets/image/red_piece.png'

WHITE_FROM_IMAGE = 'backgammon_game/assets/image/white_from_point.png'
RED_FROM_IMAGE = 'backgammon_game/assets/image/red_from_point.png'

TO_IMAGE = 'backgammon_game/assets/image/to_point.png'

HISTORY_FILENAME = 'backgammon_game/backgammon_history.txt'

VISIBLE_NUMBER = 7

DIE_IMAGES = {
    color.WHITE: {
        1: 'backgammon_game/assets/image/white_dice_1.png',
        2: 'backgammon_game/assets/image/white_dice_2.png',
        3: 'backgammon_game/assets/image/white_dice_3.png',
        4: 'backgammon_game/assets/image/white_dice_4.png',
        5: 'backgammon_game/assets/image/white_dice_5.png',
        6: 'backgammon_game/assets/image/white_dice_6.png'
    },
    color.RED: {
        1: 'backgammon_game/assets/image/red_dice_1.png',
        2: 'backgammon_game/assets/image/red_dice_2.png',
        3: 'backgammon_game/assets/image/red_dice_3.png',
        4: 'backgammon_game/assets/image/red_dice_4.png',
        5: 'backgammon_game/assets/image/red_dice_5.png',
        6: 'backgammon_game/assets/image/red_dice_6.png'
    }
}

BANNER_IMAGES = {
    1: 'backgammon_game/assets/image/banner1.png',
    2: 'backgammon_game/assets/image/banner2.png',
    3: 'backgammon_game/assets/image/banner3.png',
    4: 'backgammon_game/assets/image/banner4.png',
    5: 'backgammon_game/assets/image/banner5.png',
    6: 'backgammon_game/assets/image/banner6.png',
    7: 'backgammon_game/assets/image/banner7.png',
    8: 'backgammon_game/assets/image/banner8.png',
}

MENU_BUTTON_IMAGES = {
    graphic.LOCAL: 'backgammon_game/assets/image/local_pvp.png',
    graphic.WIN: {
        color.RED: 'backgammon_game/assets/image/red_wins.png',
        color.WHITE: 'backgammon_game/assets/image/white_wins.png'
    },
    graphic.NET: 'backgammon_game/assets/image/net_pvp.png'
}
