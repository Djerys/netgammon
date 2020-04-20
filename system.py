import sys
from functools import lru_cache

import pygame
import ecys

import logic
import config
import color
import bgp_client
import graphic as g
import component as c


@ecys.requires(c.NetPvPButtonInput)
class NetworkSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def update(self):
        try:
            self._handle_received()
        except bgp_client.BGPTimeoutError:
            pass

    def _handle_received(self):
        if self.client.bgp_client.connected:
            message = self.client.bgp_client.receive()
            print(message)
            if not self.client.net_color:
                if message['command'] == 'COLOR':
                    self.client.net_color = message['arg']
                    self.client.restart_game()
            else:
                if message['command'] == 'QUIT':
                    self.client.bgp_client.disconnect()
                if self.client.net_color == self.client.game.color:
                    if message['command'] == 'DIES':
                        die1, die2 = message['args']
                        self.client.game.roll_dice(logic.Roll(die1, die2))
                elif self.client.net_color != self.client.game.color:
                    if message['command'] == 'MOVE':
                        from_point, to_point = message['args']
                        self.client.game.move(from_point, to_point)
                    elif message['command'] == 'ENDMOVE':
                        roll = logic.Roll()
                        self.client.game.roll_dice(roll)
                        self.client.bgp_client.send_dies(roll.die1, roll.die2)


@ecys.requires(c.Render, c.Die)
class DiesSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def update(self):
        if not self.client.game.history:
            if not self.client.paused:
                roll = logic.Roll()
                if self.client.bgp_client.connected:
                    if self.client.net_color == color.WHITE:
                        self.client.bgp_client.send_dies(roll.die1, roll.die2)
                    else:
                        return
                self.client.game.roll_dice(roll)
            else:
                return
        self._arrange_dies()

    def _arrange_dies(self):
        unused_dies = list(self.client.game.roll.dies)
        for entity in self.entities:
            render = entity.get_component(c.Render)
            die_entity = entity.get_component(c.Die)
            if self.client.game.color == die_entity.color:
                render.visible = True
                if die_entity.number == 1:
                    die1 = self.client.game.roll.die1
                    render.image = config.DIE_IMAGES[die_entity.color][die1]
                    self._make_useless_die_transparent(
                        die1, render, unused_dies
                    )
                elif die_entity.number == 2:
                    die2 = self.client.game.roll.die2
                    render.image = config.DIE_IMAGES[die_entity.color][die2]
                    self._make_useless_die_transparent(
                        die2, render, unused_dies
                    )
            else:
                render.visible = False

    def _make_useless_die_transparent(
            self,
            die,
            render,
            unused_dies,
            alpha=100
    ):
        unused_die = die in unused_dies
        if not unused_die or not self.client.game.possible_points:
            render.convert_image()
            render.image.set_alpha(alpha)
        elif unused_die:
            unused_dies.remove(die)


@ecys.requires(c.Render, logic.Piece)
class ArrangePiecesSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.game = client.game

    def update(self):
        self._make_invisible_outside_pieces()
        self._arrange_inside_pieces()
        self._arrange_bar_banners()

    def _make_invisible_outside_pieces(self):
        points = self.game.board.points
        outside_points = (points[0], points[25])
        for point in outside_points:
            for piece in point.pieces:
                piece_entity = _entity_with_component(self, piece, logic.Piece)
                render = piece_entity.get_component(c.Render)
                render.visible = False

    def _arrange_bar_banners(self):
        bar = [
            (self.game.board.bar(color.WHITE),
             self.game.board.bar_pieces(color.WHITE)),
            (self.game.board.bar(color.RED),
             self.game.board.bar_pieces(color.RED))
        ]
        for point, pieces in bar:
            banner_entity = _entity_with_component(
                self, point, logic.Point, c.AdditionalBanner
            )
            banner_render = banner_entity.get_component(c.Render)
            if pieces:
                banner_render.image = config.BANNER_IMAGES[len(pieces)]
                banner_render.visible = True
            else:
                banner_render.visible = False

    def _arrange_inside_pieces(self):
        for point in self.game.board.points[1:25]:
            for piece_number, piece in enumerate(point.pieces):
                piece_entity = _entity_with_component(self, piece, logic.Piece)
                piece_render = piece_entity.get_component(c.Render)
                coords = g.PIECE_COORDS[point.number, piece_number]
                piece_render.rect.x, piece_render.rect.y = coords
                if piece_number < config.VISIBLE_NUMBER:
                    piece_render.visible = True
                else:
                    piece_render.visible = False
            banner_entity = _entity_with_component(
                self, point, logic.Point, c.AdditionalBanner
            )
            banner_render = banner_entity.get_component(c.Render)
            invisible_pieces = point.pieces[config.VISIBLE_NUMBER:]
            if invisible_pieces:
                number = len(invisible_pieces)
                banner_render.image = config.BANNER_IMAGES[number]
                banner_render.visible = True
            else:
                banner_render.visible = False


@ecys.requires(c.Render)
class RenderSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.surface = client.surface
        self.background_image = pygame.image.load(client.background_image)

    def update(self):
        self.surface.blit(self.background_image, (0, 0))
        for entity in self.entities:
            render = entity.get_component(c.Render)
            if render.visible:
                self.surface.blit(render.image, render.rect)
        pygame.display.update()


class InputSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.clicked_from = None

    def update(self):
        for event in pygame.event.get():
            self._handle_close_window(event)
            self._handle_from_point_press(event)
            self._handle_to_point_press(event)
            self._handle_end_move(event)
            self._handle_local_pvp_button_press(event)
            self._handle_net_pvp_button_press(event)
            self._handle_save_history(event)
            self._handle_pause_press(event)

    def _was_game_active_click(self, event):
        return (event.type == pygame.MOUSEBUTTONUP and
                event.button == pygame.BUTTON_LEFT and
                not self.client.game.game_over and
                not self.client.paused)

    def _was_no_game_active_click(self, event):
        return (event.type == pygame.MOUSEBUTTONUP and
                event.button == pygame.BUTTON_LEFT and
                (self.client.game.game_over or
                 self.client.paused))

    def _was_game_over_key_press(self, event):
        return (event.type == pygame.KEYUP and
                event.key == pygame.K_s and
                self.client.game.game_over)

    def _was_game_active_key_press(self, event):
        return (event.type == pygame.KEYUP and
                not self.client.game.game_over and
                not self.client.paused)

    def _was_no_game_active_key_press(self, event):
        return (event.type == pygame.KEYUP and
                (self.client.game.game_over or
                 self.client.paused))

    def _handle_close_window(self, event):
        if event.type == pygame.QUIT:
            if self.client.bgp_client.connected:
                if self.client.net_color:
                    self.client.bgp_client.send_quit()
                self.client.bgp_client.disconnect()
            pygame.quit()
            sys.exit()

    def _handle_from_point_press(self, event):
        if self._was_game_active_click(event):
            from_entities = self.world.entities_with(
                c.FromPointInput, c.Render, logic.Point
            )
            other = []
            clicked = False
            for entity in from_entities:
                input = entity.get_component(c.FromPointInput)
                render = entity.get_component(c.Render)
                point = entity.get_component(logic.Point)
                if (render.rect.collidepoint(event.pos) and
                        point in self.client.game.possible_points):
                    render.visible = True
                    self._make_to_points_invisible()
                    input.clicked = True
                    self.clicked_from = (input, render, point)
                    clicked = True
                else:
                    other.append((input, render))

            if clicked:
                for input, render in other:
                    input.clicked = False
                    render.visible = False

    def _handle_to_point_press(self, event):
        if self._was_game_active_click(event):
            entities = self.world.entities_with(c.ToPoint, c.Render, logic.Point)
            clicked = False
            renders = []
            for entity in entities:
                render = entity.get_component(c.Render)
                renders.append(render)
                if (render.rect.collidepoint(event.pos) and
                        render.visible and
                        self.clicked_from):
                    point = entity.get_component(logic.Point)
                    self.client.game.move(self.clicked_from[2], point)
                    if self.client.bgp_client.connected and self.client.net_color:
                        self.client.bgp_client.send_move(self.clicked_from[2], point)
                    self.clicked_from[0].clicked = False
                    self.clicked_from[1].visible = False
                    self.clicked_from = None
                    clicked = True

            if clicked:
                for render in renders:
                    render.visible = False

    def _make_to_points_invisible(self):
        to_entities = self.world.entities_with(c.ToPoint, c.Render)
        for entity in to_entities:
            render = entity.get_component(c.Render)
            render.visible = False

    def _handle_end_move(self, event):
        if self._was_game_active_key_press(event) and event.key == pygame.K_RETURN:
            can_finish = (not self.client.game.roll.dies or
                          not self.client.game.possible_points)
            if can_finish:
                if self.client.mode == mode.LOCAL_PVP:
                    self.client.game.roll_dice()
                elif self.client.mode == mode.NET_PVP:
                    self.client.bgp_client.send_endmove()

    def _handle_local_pvp_button_press(self, event):
        if self._was_no_game_active_click(event):
            local_render = self.client.local_pvp_button.get_component(c.Render)
            if local_render.rect.collidepoint(event.pos):
                if self.client.bgp_client.connected:
                    self.client.bgp_client.send_quit()
                    self.client.bgp_client.disconnect()
                self.client.restart_game()

    def _handle_net_pvp_button_press(self, event):
        if self._was_no_game_active_click(event):
            net_render = self.client.net_pvp_button.get_component(c.Render)
            if net_render.rect.collidepoint(event.pos):
                net_input = self.client.net_pvp_button.get_component(
                    c.NetPvPButtonInput
                )
                if not self.client.bgp_client.connected:
                    self.client.bgp_client.connect()
                net_input.clicked = True

    def _handle_save_history(self, event):
        win_render = self.client.win_button.get_component(c.Render)
        win_button_pressed = (self._was_no_game_active_click(event)
                              and win_render.rect.collidepoint(event.pos))
        if (win_button_pressed or
                (self._was_game_over_key_press(event)
                 and event.key == pygame.K_s)):
            self.client.save_history(config.HISTORY_FILENAME)

    def _handle_pause_press(self, event):
        if (self._was_game_active_key_press(event)
                and event.key == pygame.K_ESCAPE):
            self.client.paused = True
        elif (self._was_no_game_active_key_press(event)
              and event.key == pygame.K_ESCAPE):
            self.client.paused = False


class StateTrackingSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def update(self):
        win_render = self.client.win_button.get_component(c.Render)
        local_render = self.client.local_pvp_button.get_component(c.Render)
        net_render = self.client.net_pvp_button.get_component(c.Render)
        net_input = self.client.net_pvp_button.get_component(c.NetPvPButtonInput)
        if net_input.clicked:
            net_render.image = config.MENU_BUTTON_IMAGES[g.NET]['searching']
        if (not self.client.game.game_over and
                not self.client.paused):
            win_render.visible = False
            local_render.visible = False
            net_render.visible = False
        else:
            local_render.visible = True
            net_render.visible = True
            if self.client.game.game_over:
                game_color = self.client.game.color
                win_render.image = config.MENU_BUTTON_IMAGES[g.WIN][game_color]
                win_render.visible = True


class HintSystem(ecys.System):
    def __init__(self, client):
        super().__init__()
        self.game = client.game

    def update(self):
        point_entity = self._clicked_from_point()
        if not point_entity:
            return
        point = point_entity.get_component(logic.Point)
        try:
            possible_to_move = self.game.board.possible_moves(
                self.game.roll, point.number
            )
            self._make_visible_possibles(possible_to_move)
        except AssertionError:
            pass

    def _clicked_from_point(self):
        point_entity = None
        entities = self.world.entities_with(c.FromPointInput)
        for entity in entities:
            input = entity.get_component(c.FromPointInput)
            if input.clicked:
                point_entity = entity
        return point_entity

    def _make_visible_possibles(self, possible_points):
        entities = self.world.entities_with(c.ToPoint, c.Render, logic.Point)
        for entity in entities:
            number = entity.get_component(logic.Point).number
            if number in possible_points:
                render = entity.get_component(c.Render)
                render.visible = True


@lru_cache(maxsize=128)
def _entity_with_component(system, instance, *components):
    entities = system.world.entities_with(*components)
    for entity in entities:
        if instance == entity.get_component(components[0]):
            return entity
