"""
Spot (Node) class for the grid system
"""

import pygame
import time
from config.constants import *

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.priority = None  
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.original_color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.previous = None
        self.cost = 1
        self.is_traffic_stop = False
        self.light_state = "green"  # green, yellow, red

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def is_dynamic(self):
        return self.color == BLUE

    def reset(self):
        self.color = self.original_color
        self.cost = 1
        self.previous = None

    def make_start(self):
        self.color = ORANGE
        self.original_color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK
        self.original_color = BLACK

    def make_end(self):
        self.color = TURQUOISE
        self.original_color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def make_dynamic(self):
        self.color = BLUE

    def make_traffic_light(self):
        self.is_traffic_stop = True
        self.update_traffic_light()

    def update_traffic_light(self):
        current_time = time.time()
        cycle_pos = (current_time % TRAFFIC_LIGHT_CYCLE) / TRAFFIC_LIGHT_CYCLE

        if cycle_pos < 0.7:
            self.light_state = "green"
            self.color = GREEN
        elif cycle_pos < 0.8:
            self.light_state = "yellow"
            self.color = YELLOW
        else:
            self.light_state = "red"
            self.color = RED

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

        # Draw traffic light indicator if applicable
        if self.is_traffic_stop:
            radius = self.width // 4
            offset = self.width // 4
            if self.light_state == "green":
                pygame.draw.circle(win, GREEN,
                                   (self.x + offset, self.y + offset), radius)
            elif self.light_state == "yellow":
                pygame.draw.circle(win, YELLOW,
                                   (self.x + self.width // 2, self.y + offset), radius)
            else:
                pygame.draw.circle(win, RED,
                                   (self.x + self.width - offset, self.y + offset), radius)

    def update_neighbors(self, grid):
        self.neighbors = []
        dirs = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for d in dirs:
            r, c = self.row + d[0], self.col + d[1]
            if 0 <= r < self.total_rows and 0 <= c < self.total_rows:
                neighbor = grid[r][c]

                # Check if neighbor is a red traffic light
                if neighbor.is_traffic_stop and neighbor.light_state == "red":
                    continue  # Skip this neighbor if it's a red light

                if not neighbor.is_barrier():
                    self.neighbors.append(neighbor)