"""
Rendering and drawing functions
"""

import pygame
import math
from config.constants import *
from config.settings import *
from core.grid import draw_grid

def draw(win, grid, rows, width, trails, robot_center, robot, barrier_mode=False):
    win.fill(WHITE)

    # Draw grid spots
    for row in grid:
        for spot in row:
            spot.draw(win)
            if hasattr(spot, 'priority') and spot.priority:
                font = pygame.font.SysFont('Arial', 16, bold=True)
                text = font.render(str(spot.priority), True, BLACK)
                text_rect = text.get_rect(center=(spot.x + spot.width // 2, spot.y + spot.width // 2))
                win.blit(text, text_rect)



    # Draw trail path
    for trail in trails:
        pygame.draw.circle(win, PURPLE, trail.get_center(), 3)



    # Draw robot and direction
    if robot_center:
        pos_x, pos_y = robot_center
        radius = grid[0][0].width // 3
        pygame.draw.circle(win, ORANGE, (pos_x, pos_y), radius)

        if len(trails) > 1:
            prev_pos = trails[-2].get_center()
            angle = math.atan2(pos_y - prev_pos[1], pos_x - prev_pos[0])
            arrow_length = radius * 1.5
            end_x = pos_x + arrow_length * math.cos(angle)
            end_y = pos_y + arrow_length * math.sin(angle)
            pygame.draw.line(win, BLACK, (pos_x, pos_y), (end_x, end_y), 2)

    # Draw grid lines and UI
    draw_grid(win, rows, width)
    draw_ui(win, robot)

    pygame.display.update()


def draw_ui(win, robot=None):
    """Draw the user interface sidebar"""
    pygame.draw.rect(win, SIDEBAR_BG, (WIDTH, 0, SIDEBAR_WIDTH, WIDTH))  # Right sidebar

    font_title = pygame.font.SysFont('Arial', 24, bold=True)
    font = pygame.font.SysFont('Arial', 18)

    # Title
    title = font_title.render("A* SIMULATOR", True, BLACK)
    win.blit(title, (WIDTH + 20, 20))

    instructions = [
        "Controls:",
        "• Left Click: Set Start/Target",
        "• B: Add Barriers (Toggle)",
        "• Hold T: Add Traffic Light",
        "• Right Click: Remove Cell",
        "• Space: Start Simulation",
        "• C: Clear Grid, R: Reset",
        "• O: Save Obstacles, P: Load Obstacles",
        "• S: Save Map, L: Load Map",
        "• 1-4: Speed (Current: {}x)".format(sim_speed),
        "• T: Toggle Traffic Tool"
    ]

    for i, text in enumerate(instructions):
        label = font.render(text, True, BLACK)
        win.blit(label, (WIDTH + 20, 70 + i * 30))
    