from abc import ABC, abstractmethod

import pygame


class Game(ABC):
    def __init__(self, caption, width, height, frame_rate):
        self.frame_rate = frame_rate
        self.game_over = False
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.world = self._create_world()

    def run(self):
        while not self.game_over:
            self._update_world()

            self.clock.tick(self.frame_rate)

    @abstractmethod
    def _create_world(self):
        pass

    @abstractmethod
    def _update_world(self):
        pass
