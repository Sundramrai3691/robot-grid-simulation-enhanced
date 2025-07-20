import pygame
import math
from config.constants import *
from config.settings import *
from core.grid import draw_grid

def draw(win, grid, rows, width, trails, robot_center, robot):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)
            if hasattr(spot, 'target_priority') and spot.target_priority:
                font = pygame.font.SysFont('Arial', 16, bold=True)
                text = font.render(str(spot.target_priority), True, BLACK)
                text_rect = text.get_rect(center=(spot.x + spot.width // 2, spot.y + spot.width // 2))
                win.blit(text, text_rect)

    for trail in trails:
        if hasattr(trail, 'get_center'):
            pygame.draw.circle(win, PURPLE, trail.get_center(), 3)

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

    draw_grid(win, rows, width)
    draw_ui(win, robot)
    pygame.display.update()

def draw_ui(win, robot=None):
    pygame.draw.rect(win, SIDEBAR_BG, (WIDTH, 0, SIDEBAR_WIDTH, WIDTH))

    font_title = pygame.font.SysFont('Arial', 24, bold=True)
    font = pygame.font.SysFont('Arial', 18)

    title = font_title.render("A* SIMULATOR", True, BLACK)
    win.blit(title, (WIDTH + 20, 20))

    instructions = [
        "Controls:",
        "• Left Click: Set Start/Target",
        "• M: Target Mode",
        "• B: Barrier Mode",
        "• T: Traffic Light Mode", 
        "• Right Click: Remove Cell",
        "• Space: Start Simulation",
        "• C: Clear Grid",
        "• R: Reset",
        "• S: Save Map",
        "• L: Load Map",
        "• 1-4: Speed Control"
    ]

    for i, text in enumerate(instructions):
        label = font.render(text, True, BLACK)
        win.blit(label, (WIDTH + 20, 70 + i * 25))