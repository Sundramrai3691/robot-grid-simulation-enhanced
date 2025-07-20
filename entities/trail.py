"""
Trail effect system for robot movement visualization
"""

import pygame
from config.constants import *

class TrailMarker:
    def __init__(self, pos, color, width):
        self.pos = pos
        self.color = color
        self.width = width
        self.alpha = TRAIL_ALPHA
        self.lifetime = TRAIL_LENGTH

    def update(self):
        """Update trail marker (fade over time)"""
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - FADING_SPEED)
        self.color = (*self.color[:3], self.alpha)

    def draw(self, win):
        """Draw the trail marker"""
        if self.alpha > 0:
            s = pygame.Surface((self.width, self.width), pygame.SRCALPHA)
            pygame.draw.rect(s, self.color, (0, 0, self.width, self.width))
            win.blit(s, (self.pos[0], self.pos[1]))

    def get_center(self):
        """Return the center position of the trail for drawing circles"""
        return (self.pos[0] + self.width // 2, self.pos[1] + self.width // 2)
