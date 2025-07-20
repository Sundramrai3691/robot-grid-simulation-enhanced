"""
Trail markers for robot path visualization
"""

import pygame
from config.constants import FADING_SPEED

class TrailMarker:
    def __init__(self, pos, color, size):
        self.pos = pos
        self.color = color
        self.alpha = color[3] if len(color) > 3 else 255
        self.size = size
        self.original_alpha = self.alpha
        
    def update(self):
        """Update the trail marker (fade over time)"""
        self.alpha = max(0, self.alpha - FADING_SPEED)
    
    def draw(self, win):
        """Draw the trail marker"""
        if self.alpha > 0:
            # Create a surface for transparency
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], self.alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            win.blit(s, (self.pos[0] - self.size, self.pos[1] - self.size))
    
    def is_faded(self):
        """Check if the trail marker has completely faded"""
        return self.alpha <= 0
    
    def get_center(self):
        """Get the center position of the trail marker"""
        return self.pos