import socket

import pygame
import sys

import config
import color
import logic
import component as c
import graphic as g


class State:
    def __init__(self, client):
        self.client = client

    def pause(self):
        pass

    def save_history(self, filename):
        pass

    def start_local_game(self):
        pass

    def start_network_game(self):
        pass

    def handle_received(self):
        pass

    def move(self, from_point, to_point):
        pass

    def end_move(self):
        pass

    def close_window(self):
        pygame.quit()
        sys.exit()

    @property
    def possible_points(self):
        return []

    def set_state_image(self):
        state_button = self.client.state_button
        render = state_button.get_component(c.Render)
        render.visible = False

    def set_local_button_image(self):
        local_button = self.client.local_button
        render = local_button.get_component(c.Render)
        render.visible = False

    def set_network_button_image(self):
        network_button = self.client.network_button
        render = network_button.get_component(c.Render)
        render.visible = False


class LockState(State):
    """Lock state is a state when the game started for the first time.

    It's base class for all states when you cannot play.
    """
    def start_local_game(self):
        self.client.game.restart()
        self.client.game.roll_dice()
        self.client.state = LocalPlayingState(self.client)

    def start_network_game(self):
        if not self.client.bgp.closed:
            self.client.bgp.close()
        try:
            self.client.bgp.connect()
        except (socket.error, ConnectionError):
            self.client.state = DisconnectedState(self.client)
        else:
            self.client.state = SearchingOpponentState(self.client)

    @State.possible_points.getter
    def possible_points(self):
        return []

    def set_local_button_image(self):
        local_button = self.client.local_button
        render = local_button.get_component(c.Render)
        render.visible = True

    def set_network_button_image(self):
        network_button = self.client.network_button
        render = network_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.NET]['press']


class WinState(LockState):
    def set_state_image(self):
        state_button = self.client.state_button
        render = state_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.STATE][self.client.game.color]

    def save_history(self, filename):
        self.client.save_history(filename)


class PauseState(LockState):
    def __init__(self, client, from_state):
        super().__init__(client)
        self.from_state = from_state

    def pause(self):
        self.client.state = self.from_state

    def handle_received(self):
        self.from_state.handle_received()

    def close_window(self):
        self.from_state.close_window()


class SearchingOpponentState(LockState):
    def start_local_game(self):
        self.client.bgp.close()
        super().start_local_game()

    def start_network_game(self):
        pass

    def set_network_button_image(self):
        network_button = self.client.network_button
        render = network_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.NET]['pressed']

    def handle_received(self):
        try:
            message = self.client.bgp.receive()
            print(message)
            if message['command'] == 'COLOR':
                self.client.network_game_color = message['arg']
                self.client.game.restart()
                if self.client.network_game_color == color.WHITE:
                    roll = logic.Roll()
                    self.client.game.roll_dice(roll)
                    self.client.bgp.send_dies(roll.die1, roll.die2)
                self.client.state = NetworkPlayingState(self.client)
        except socket.timeout as e:
            raise e
        except (socket.error, ConnectionError):
            self.client.state = DisconnectedState(self.client)

    def close_window(self):
        self.client.bgp.close()
        super().close_window()


class DisconnectedState(LockState):
    def set_state_image(self):
        state_button = self.client.state_button
        render = state_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.STATE][g.DISCONNECT]


class PlayingState(State):
    """Base class for local and network playing states. Do not use."""
    def pause(self):
        self.client.state = PauseState(self.client, self)

    def move(self, from_point, to_point):
        self.client.game.move(from_point, to_point)
        self._check_win_state()

    def _check_win_state(self):
        if self.client.game.game_over:
            self.client.state = WinState(self.client)


class LocalPlayingState(PlayingState):
    def end_move(self):
        self.client.game.roll_dice()

    @State.possible_points.getter
    def possible_points(self):
        return self.client.game.possible_points


class NetworkPlayingState(PlayingState):
    def move(self, from_point, to_point):
        if isinstance(from_point, logic.Point):
            from_point = from_point.number
        if isinstance(to_point, logic.Point):
            to_point = to_point.number
        super().move(from_point, to_point)
        self.client.bgp.send_move(from_point, to_point)

    def end_move(self):
        self.client.bgp.send_end_move()

    def handle_received(self):
        try:
            message = self.client.bgp.receive()
            print(message)
            if message['command'] == 'QUIT':
                self.client.bgp.close()
                self.client.state = DisconnectedState(self.client)
            if self.client.network_game_color == self.client.game.color:
                if message['command'] == 'DIES':
                    die1, die2 = message['args']
                    self.client.game.roll_dice(logic.Roll(die1, die2))
            elif self.client.network_game_color != self.client.game.color:
                if message['command'] == 'MOVE':
                    from_point, to_point = message['args']
                    self.client.game.move(from_point, to_point)
                elif message['command'] == 'ENDMOVE':
                    roll = logic.Roll()
                    self.client.game.roll_dice(roll)
                    self.client.bgp.send_dies(roll.die1, roll.die2)
            self._check_win_state()
        except socket.timeout as e:
            raise e
        except (socket.error, ConnectionError):
            self.client.state = DisconnectedState(self.client)

    def close_window(self):
        self.client.bgp.send_quit()
        self.client.bgp.close()
        super().close_window()

    @State.possible_points.getter
    def possible_points(self):
        if self.client.network_game_color != self.client.game.color:
            return []
        return self.client.game.possible_points
