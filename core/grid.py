"""
Grid utilities and helper functions
"""

import pygame
from config.constants import *
from config.settings import *
from .spot import Spot

def make_grid(rows, width):
    """Create a grid of Spot objects"""
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Spot(i, j, gap, rows))
    return grid

def get_clicked_pos(pos, rows, width):
    """Get the grid position from mouse click coordinates"""
    gap = width // rows
    y, x = pos
    return y // gap, x // gap

def draw_grid(win, rows, width):
    """Draw the grid lines"""
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRAY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GRAY, (j * gap, 0), (j * gap, width))