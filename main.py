import pygame
import os
from config.settings import *
from config.constants import *
from core.grid import make_grid, get_clicked_pos
from core.robot import Robot
from ui.renderer import draw
from ui.input_handler import get_text_input
from utils.file_manager import save_map, load_map, save_obstacles, load_obstacles

def main(win, width):
    global sim_speed, traffic_light_tool
    
    # Create maps directory if it doesn't exist
    if not os.path.exists("maps"):
        os.makedirs("maps")
    
    pygame.font.init()
    grid = make_grid(ROWS, width)
    start = None
    targets = []
    robot = None
    run = True
    clock = pygame.time.Clock()
    sim_running = False
    
    # Input modes
    target_mode = False
    target_priority = 1
    barrier_mode = False
    traffic_light_tool = False
    
    # Robot parameters
    robot_params = {
        'battery': DEFAULT_BATTERY,
        'sensor_range': DEFAULT_SENSOR_RANGE,
        'speed': DEFAULT_ROBOT_SPEED,
        'drain_rate': BATTERY_DRAIN_RATE
    }

    while run:
        clock.tick(30)

        # Update traffic lights
        for row in grid:
            for spot in row:
                if hasattr(spot, 'is_traffic_stop') and spot.is_traffic_stop:
                    spot.update_traffic_light()

        # Draw everything
        draw(win, grid, ROWS, width,
             robot.trails if robot else [],
             robot.get_center() if robot else None, 
             robot)

        # Update robot simulation
        if sim_running and robot:
            if not robot.reached_goal():
                if not robot.step():
                    if robot.battery <= 0:
                        print("Robot battery depleted!")
                        sim_running = False
            else:
                print("All targets reached!")
                sim_running = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Left mouse button - place objects
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] < width:  # Only within grid area
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        spot = grid[row][col]
                        
                        if target_mode:
                            if not spot.is_start() and not spot.is_barrier():
                                spot.make_target(target_priority)
                                targets.append(spot)
                        elif traffic_light_tool:
                            if not spot.is_start() and not spot.is_end():
                                spot.make_traffic_light()
                        elif barrier_mode:
                            if not spot.is_start() and not spot.is_end():
                                spot.make_barrier()
                        elif not start and not spot.is_barrier() and not spot.is_end():
                            start = spot
                            start.make_start()
                        elif spot != start and not spot.is_end():
                            spot.make_barrier()

            # Right mouse button - remove objects
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] < width:  # Only within grid area
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        spot = grid[row][col]
                        if spot == start:
                            start = None
                        elif spot in targets:
                            targets.remove(spot)
                        spot.reset()
                        if hasattr(spot, 'is_traffic_stop'):
                            spot.is_traffic_stop = False

            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and targets:
                    # Start simulation
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    robot = Robot(start, targets, grid,
                                  lambda: draw(win, grid, ROWS, width, robot.trails, robot.get_center(), robot),
                                  **robot_params)
                    if robot.plan_path():
                        sim_running = True
                    else:
                        print("No path found!")
                        
                elif event.key == pygame.K_c:
                    # Clear grid
                    grid = make_grid(ROWS, width)
                    start = None
                    targets = []
                    robot = None
                    sim_running = False
                    
                elif event.key == pygame.K_r:
                    # Reset simulation
                    if robot and start:
                        robot.current = start
                        robot.trails = []
                        robot.index = 0
                        robot.completed_targets = []
                        robot.current_target = None
                        robot.battery = robot.max_battery
                        robot.distance_traveled = 0
                        robot.steps_taken = 0
                        robot.replan_count = 0
                        if robot.plan_path():
                            sim_running = True
                    
                elif event.key == pygame.K_o:
                    # Save obstacles
                    save_obstacles(grid)
                    
                elif event.key == pygame.K_p:
                    # Load obstacles
                    load_obstacles(grid)
                    
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    # Change speed
                    speed_index = event.key - pygame.K_1
                    sim_speed = SPEED_MULTIPLIERS[speed_index]
                    robot_params['speed'] = sim_speed
                    if robot:
                        robot.speed_multiplier = sim_speed

                elif event.key == pygame.K_t:
                    # Toggle traffic light mode
                    traffic_light_tool = not traffic_light_tool
                    target_mode = False
                    barrier_mode = False
                    print(f"Traffic light mode: {'ON' if traffic_light_tool else 'OFF'}")

                elif event.key == pygame.K_m:
                    # Toggle target mode
                    target_mode = not target_mode
                    traffic_light_tool = False
                    barrier_mode = False
                    print(f"Target mode: {'ON' if target_mode else 'OFF'}")

                elif event.key == pygame.K_b:
                    # Toggle barrier mode
                    barrier_mode = not barrier_mode
                    traffic_light_tool = False
                    target_mode = False
                    print(f"Barrier mode: {'ON' if barrier_mode else 'OFF'}")

                elif event.key == pygame.K_s:
                    # Save map
                    map_name = get_text_input("Enter a name for this map:", "Save Map")
                    if map_name:
                        save_map(grid, start, targets, map_name)

                elif event.key == pygame.K_l:
                    # Load map
                    map_name = get_text_input("Enter the name of the map to load:", "Load Map")
                    if map_name:
                        result = load_map(grid, map_name)
                        if result:
                            grid, start, loaded_targets = result
                            targets = loaded_targets if loaded_targets else []

                # Set target priority when in target mode
                elif target_mode and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    target_priority = event.key - pygame.K_0
                    print(f"Target priority set to: {target_priority}")

                elif event.key == pygame.K_q:
                    # Quit
                    run = False

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    WIN = pygame.display.set_mode((WINDOW_WIDTH, WIDTH))
    pygame.display.set_caption("A* Navigation Simulator")
    
    # Initialize global variables
    sim_speed = DEFAULT_SPEED
    traffic_light_tool = False
    
    main(WIN, WIDTH)