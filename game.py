import sys

import pygame


class Game:
    def __init__(
            self,
            caption,
            width,
            height,
            background_image_filename,
            frame_rate
    ):
        self.background_image = pygame.image.load(background_image_filename)
        self.frame_rate = frame_rate
        self.game_over = False
        self.objects = []
        pygame.mixer.init(frequency=44100)
        pygame.font.init()
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.key_down_handlers = []
        self.key_up_handlers = []
        self.mouse_handlers = []

    def _update(self):
        for o in self.objects:
            o.update()

    def _draw(self):
        for o in self.objects:
            o.draw(self.surface)

    def _handle_events(self):
        mouse_events = {
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                for handler in self.key_down_handlers:
                    handler(event.key)

            elif event.type == pygame.KEYUP:
                for handler in self.key_up_handlers:
                    handler(event.key)

            elif event.type in mouse_events:
                for handler in self.mouse_handlers:
                    handler(event.type, event.pos)

    def run(self):
        while not self.game_over:
            self.surface.blit(self.background_image, (0, 0))

            self._handle_events()
            self._update()
            self._draw()

            pygame.display.update()
            self.clock.tick(self.frame_rate)
