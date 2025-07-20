import pygame
import math
from config.constants import *
from config.settings import *
from core.grid import draw_grid

def draw(win, grid, rows, width, trails, robot_center, robot, dynamic_obstacles=None, modes=None):
    """Main drawing function for the entire simulation"""
    win.fill(WHITE)

    # Draw grid spots
    for row in grid:
        for spot in row:
            spot.draw(win)
            
            # Draw target priority numbers
            if hasattr(spot, 'target_priority') and spot.target_priority:
                font = pygame.font.SysFont('Arial', 16, bold=True)
                text = font.render(str(spot.target_priority), True, BLACK)
                text_rect = text.get_rect(center=(spot.x + spot.width // 2, spot.y + spot.width // 2))
                win.blit(text, text_rect)

    # Draw dynamic obstacles with special highlighting
    if dynamic_obstacles:
        for obstacle in dynamic_obstacles:
            if obstacle.current:
                # Draw a pulsing border around dynamic obstacles
                border_width = 3
                pygame.draw.rect(win, BLUE, 
                               (obstacle.current.x - border_width, 
                                obstacle.current.y - border_width,
                                obstacle.current.width + 2*border_width,
                                obstacle.current.width + 2*border_width))
                
                # Draw obstacle name
                font = pygame.font.SysFont('Arial', 12, bold=True)
                text = font.render(obstacle.name, True, WHITE)
                text_rect = text.get_rect(center=(
                    obstacle.current.x + obstacle.current.width // 2,
                    obstacle.current.y + obstacle.current.width // 2
                ))
                win.blit(text, text_rect)

    # Draw robot trails
    for trail in trails:
        trail.draw(win)

    # Draw robot with direction indicator
    if robot_center:
        pos_x, pos_y = robot_center
        radius = grid[0][0].width // 3
        
        # Draw robot body
        pygame.draw.circle(win, ORANGE, (pos_x, pos_y), radius)
        pygame.draw.circle(win, BLACK, (pos_x, pos_y), radius, 2)  # Border
        
        # Draw direction arrow if robot has moved
        if len(trails) > 1:
            prev_pos = trails[-2].get_center() if hasattr(trails[-2], 'get_center') else trails[-2].pos
            angle = math.atan2(pos_y - prev_pos[1], pos_x - prev_pos[0])
            arrow_length = radius * 0.8
            end_x = pos_x + arrow_length * math.cos(angle)
            end_y = pos_y + arrow_length * math.sin(angle)
            pygame.draw.line(win, BLACK, (pos_x, pos_y), (end_x, end_y), 3)

    # Draw grid lines
    draw_grid(win, rows, width)
    
    # Draw UI sidebar
    draw_ui(win, robot, modes, dynamic_obstacles)
    
    pygame.display.update()

def draw_ui(win, robot=None, modes=None, dynamic_obstacles=None):
    """Draw the UI sidebar with controls and information"""
    # Clear sidebar area
    pygame.draw.rect(win, SIDEBAR_BG, (WIDTH, 0, SIDEBAR_WIDTH, WIDTH))
    
    font_title = pygame.font.SysFont('Arial', 20, bold=True)
    font_section = pygame.font.SysFont('Arial', 16, bold=True)
    font = pygame.font.SysFont('Arial', 14)
    font_small = pygame.font.SysFont('Arial', 12)

    y_offset = 20
    
    # Title
    title = font_title.render("A* ROBOT SIMULATOR", True, BLACK)
    win.blit(title, (WIDTH + 10, y_offset))
    y_offset += 35

    # Current mode indicator
    if modes:
        current_mode = "Normal"
        if modes.get('target_mode', False):
            current_mode = f"Target (Priority {modes.get('target_priority', 1)})"
        elif modes.get('barrier_mode', False):
            current_mode = "Barrier"
        elif modes.get('traffic_light_tool', False):
            current_mode = "Traffic Light"
        elif modes.get('dynamic_mode', False):
            current_mode = "Dynamic Obstacle"
        
        mode_text = font_section.render("Mode:", True, BLACK)
        win.blit(mode_text, (WIDTH + 10, y_offset))
        mode_value = font.render(current_mode, True, BLUE)
        win.blit(mode_value, (WIDTH + 60, y_offset))
        y_offset += 25

    # Controls section
    controls_title = font_section.render("Controls:", True, BLACK)
    win.blit(controls_title, (WIDTH + 10, y_offset))
    y_offset += 20

    controls = [
        "Left Click: Place object",
        "Right Click: Remove object",
        "M: Target Mode",
        "B: Barrier Mode", 
        "T: Traffic Light Mode",
        "D: Dynamic Obstacle Mode",
        "Space: Start/Stop Simulation",
        "C: Clear Grid",
        "R: Reset Robot",
        "S: Save Map",
        "L: Load Map",
        "1-4: Speed Control",
        "Q: Quit"
    ]

    for control in controls:
        text = font_small.render(control, True, BLACK)
        win.blit(text, (WIDTH + 10, y_offset))
        y_offset += 16

    # Robot status section
    if robot:
        y_offset += 10
        status_title = font_section.render("Robot Status:", True, BLACK)
        win.blit(status_title, (WIDTH + 10, y_offset))
        y_offset += 20

        # Battery status with color coding
        battery_pct = (robot.battery / robot.max_battery) * 100
        battery_color = GREEN if battery_pct > 50 else YELLOW if battery_pct > 20 else RED
        
        battery_text = font.render(f"Battery: {robot.battery:.1f}%", True, battery_color)
        win.blit(battery_text, (WIDTH + 10, y_offset))
        y_offset += 16

        # Draw battery bar
        bar_width = 100
        bar_height = 8
        bar_x = WIDTH + 10
        bar_y = y_offset
        
        pygame.draw.rect(win, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        fill_width = int(bar_width * (robot.battery / robot.max_battery))
        pygame.draw.rect(win, battery_color, (bar_x + 1, bar_y + 1, fill_width - 2, bar_height - 2))
        y_offset += 20

        # Other robot stats
        stats = [
            f"Steps Taken: {robot.steps_taken}",
            f"Distance: {robot.distance_traveled}",
            f"Replans: {robot.replan_count}",
            f"Speed: {robot.speed_multiplier}x",
            f"Targets: {len(robot.completed_targets)}/{len(robot.targets)}"
        ]

        for stat in stats:
            text = font_small.render(stat, True, BLACK)
            win.blit(text, (WIDTH + 10, y_offset))
            y_offset += 14

    # Dynamic obstacles section
    if dynamic_obstacles:
        y_offset += 15
        obstacles_title = font_section.render("Dynamic Obstacles:", True, BLACK)
        win.blit(obstacles_title, (WIDTH + 10, y_offset))
        y_offset += 20

        for i, obstacle in enumerate(dynamic_obstacles):
            obstacle_text = font_small.render(f"{obstacle.name} (Speed: {obstacle.speed})", True, BLUE)
            win.blit(obstacle_text, (WIDTH + 10, y_offset))
            y_offset += 14

    # Speed indicator
    y_offset = WIDTH - 60
    speed_text = font.render(f"Simulation Speed: {sim_speed}x", True, BLACK)
    win.blit(speed_text, (WIDTH + 10, y_offset))

def draw_path_preview(win, grid, path, color=PURPLE):
    """Draw a preview of the planned path"""
    if not path or len(path) < 2:
        return
    
    for i in range(len(path) - 1):
        current_spot = path[i]
        next_spot = path[i + 1]
        
        start_pos = (current_spot.x + current_spot.width // 2, 
                    current_spot.y + current_spot.width // 2)
        end_pos = (next_spot.x + next_spot.width // 2,
                  next_spot.y + next_spot.width // 2)
        
        pygame.draw.line(win, color, start_pos, end_pos, 3)

def draw_sensor_range(win, robot, grid):
    """Draw the robot's sensor range"""
    if not robot or not robot.current:
        return
    
    center_x = robot.current.x + robot.current.width // 2
    center_y = robot.current.y + robot.current.width // 2
    radius = robot.sensor_range * grid[0][0].width
    
    # Draw semi-transparent circle
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*GREEN, 50), (radius, radius), radius)
    win.blit(s, (center_x - radius, center_y - radius))
    
    # Draw border
    pygame.draw.circle(win, GREEN, (center_x, center_y), radius, 2)

def draw_mini_map(win, grid, robot):
    """Draw a miniaturized overview of the entire grid"""
    mini_size = 150
    mini_x = WIDTH + SIDEBAR_WIDTH - mini_size - 10
    mini_y = 10
    
    # Background
    pygame.draw.rect(win, WHITE, (mini_x, mini_y, mini_size, mini_size))
    pygame.draw.rect(win, BLACK, (mini_x, mini_y, mini_size, mini_size), 2)
    
    # Calculate scaling
    scale = mini_size / len(grid)
    
    # Draw grid elements
    for i, row in enumerate(grid):
        for j, spot in enumerate(row):
            pixel_x = mini_x + j * scale
            pixel_y = mini_y + i * scale
            
            color = WHITE
            if spot.is_barrier():
                color = BLACK
            elif spot.is_end():
                color = TURQUOISE
            elif spot.is_start():
                color = ORANGE
            elif hasattr(spot, 'is_traffic_stop') and spot.is_traffic_stop:
                color = spot.color
            
            if color != WHITE:
                pygame.draw.rect(win, color, (pixel_x, pixel_y, scale, scale))
    
    # Draw robot position
    if robot and robot.current:
        robot_x = mini_x + robot.current.col * scale
        robot_y = mini_y + robot.current.row * scale
        pygame.draw.circle(win, RED, (int(robot_x + scale/2), int(robot_y + scale/2)), 2)