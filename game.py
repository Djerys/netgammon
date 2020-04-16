from abc import ABC, abstractmethod

import pygame


class Game(ABC):
    def __init__(self, caption, width, height, frame_rate):
        self.frame_rate = frame_rate
        self.is_running = True
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

    def run(self):
        while self.is_running:
            self._update()
            self.clock.tick(self.frame_rate)

    @abstractmethod
    def _update(self):
        pass
