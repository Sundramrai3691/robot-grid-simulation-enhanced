import pygame
import os
from config.settings import *
from config.constants import *
from core.grid import make_grid, get_clicked_pos
from core.robot import Robot
from ui.renderer import draw
from ui.input_handler import get_text_input
from utils.file_manager import save_map, load_map, save_obstacles, load_obstacles
from entities.dynamic_obstacle import DynamicObstacleManager

def main(win, width):
    global sim_speed, traffic_light_tool

    # Create maps directory if it doesn't exist
    if not os.path.exists("maps"):
        os.makedirs("maps")

    pygame.font.init()
    grid = make_grid(ROWS, width)
    start = robot = None
    barrier_mode = False
    traffic_light_tool = False
    dynamic_obstacle_tool = False  # ✅ New tool for dynamic obstacles
    click_count = 0
    barrier_placed = False 
    priority_counter = 1
    targets = []
    run = True
    clock = pygame.time.Clock()
    sim_running = False
    
    # ✅ Dynamic obstacle manager
    dynamic_manager = DynamicObstacleManager()

    while run:
        clock.tick(30)

        # Update traffic lights
        for row in grid:
            for spot in row:
                if spot.is_traffic_stop:
                    spot.update_traffic_light()
        
        # ✅ Update dynamic obstacles
        dynamic_manager.update_all()

        draw(win, grid, ROWS, width,
             robot.trails if robot else [],
             robot.get_center() if robot else None,
             robot,
             barrier_mode,
             dynamic_obstacle_tool)  # ✅ Pass dynamic tool state

        if sim_running and robot:
            if not robot.reached_goal():
                robot.step()
            elif targets:
                robot.start = robot.current  # Continue from last position
                # ✅ Sort targets by priority before getting next one
                targets.sort(key=lambda x: x[0])
                _, next_target = targets.pop(0)
                robot.set_new_goal(next_target)
                robot.plan_path()
                print(f"Moving to target with priority {_}")  # Debug info
            else:
                sim_running = False
                print("All targets completed.")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]

                    if barrier_mode:
                        spot.make_barrier()
                        barrier_placed = True

                    elif traffic_light_tool:
                        spot.make_traffic_light()
                        traffic_light_tool = False
                        barrier_mode = False
                        dynamic_obstacle_tool = False
                        print("Traffic light tool: OFF")
                        print("All tools: OFF")
                    
                    # ✅ Handle dynamic obstacle placement
                    elif dynamic_obstacle_tool:
                        if (not spot.is_barrier() and not spot.is_start() and 
                            not spot.is_end() and not spot.is_traffic_stop() and 
                            not spot.is_dynamic()):
                            dynamic_manager.add_obstacle(row, col, grid)
                            print(f"Dynamic obstacle added at ({row}, {col})")

                    elif not barrier_placed:  # ✅ Prevent placing targets after barrier
                        if click_count == 0:
                            start = spot
                            start.make_start()
                            click_count = 1
                        elif spot != start and spot not in [t[1] for t in targets]:
                            spot.priority = priority_counter  # ✅ Set priority before incrementing
                            targets.append((priority_counter, spot))
                            spot.make_end()
                            print(f"Target {priority_counter} placed at ({row}, {col})")  # Debug info
                            priority_counter += 1  # ✅ increment after use

            elif pygame.mouse.get_pressed()[2]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]
                    
                    # ✅ Handle removing dynamic obstacles
                    if spot.is_dynamic():
                        # Find and remove the dynamic obstacle at this position
                        for obstacle in dynamic_manager.obstacles[:]:  # Copy list to avoid modification during iteration
                            if obstacle.row == row and obstacle.col == col:
                                dynamic_manager.remove_obstacle(obstacle)
                                print(f"Dynamic obstacle removed from ({row}, {col})")
                                break
                    
                    if spot == start:
                        start = None
                        click_count = 0
                    
                    # ✅ Remove from targets list if it's a target
                    targets = [t for t in targets if t[1] != spot]
                    
                    spot.reset()
                    spot.is_traffic_stop = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    if start and targets:
                        # ✅ Sort targets by priority
                        targets.sort(key=lambda x: x[0])
                        _, current_target = targets.pop(0)
                        robot = Robot(start, current_target, grid,
                                      lambda: draw(win, grid, ROWS, width,
                                                   robot.trails,
                                                   robot.get_center(),
                                                   robot, barrier_mode, dynamic_obstacle_tool))
                        robot.plan_path()
                        sim_running = True
                        print(f"Starting navigation to target with priority {_}")

                if event.key == pygame.K_b:
                    barrier_mode = True
                    traffic_light_tool = False
                    dynamic_obstacle_tool = False
                    print("Barrier mode: ON")

                if event.key == pygame.K_t:
                    traffic_light_tool = True
                    barrier_mode = False
                    dynamic_obstacle_tool = False
                    print("Traffic light tool: ON")
                    print("Other tools: OFF")
                
                # ✅ Dynamic obstacle tool toggle
                if event.key == pygame.K_d:
                    dynamic_obstacle_tool = True
                    barrier_mode = False
                    traffic_light_tool = False
                    print("Dynamic obstacle tool: ON")
                    print("Other tools: OFF")

                if event.key == pygame.K_c or event.key == pygame.K_r:
                    grid = make_grid(ROWS, width)
                    start = robot = None
                    sim_running = False
                    click_count = 0
                    priority_counter = 1
                    targets.clear()
                    barrier_mode = False
                    traffic_light_tool = False
                    dynamic_obstacle_tool = False
                    barrier_placed = False  # ✅ Reset this too
                    
                    # ✅ Clear all dynamic obstacles
                    dynamic_manager.clear_all()

                    # Clear priority from each spot
                    for row in grid:
                        for spot in row:
                            if hasattr(spot, 'priority'):
                                spot.priority = None

                if event.key == pygame.K_o:
                    save_obstacles(grid)

                if event.key == pygame.K_p:
                    load_obstacles(grid)

                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    sim_speed = [0.1, 0.3, 0.5, 1.0][event.key - pygame.K_1]

                if event.key == pygame.K_s:
                    map_name = get_text_input("Enter a name for this map:", "Save Map")
                    if map_name:
                        save_map(grid, start, None, map_name)

                if event.key == pygame.K_l:
                    map_name = get_text_input("Enter the name of the map to load:", "Load Map")
                    if map_name:
                        result = load_map(grid, map_name)
                        if result:
                            grid, start, _ = result
                
                # ✅ Display help/controls
                if event.key == pygame.K_h:
                    print("\n=== CONTROLS ===")
                    print("Left Click: Place start (first click) or targets")
                    print("Right Click: Remove obstacles/targets")
                    print("SPACE: Start simulation")
                    print("B: Barrier mode")
                    print("T: Traffic light tool")
                    print("D: Dynamic obstacle tool")  # New
                    print("C/R: Clear/Reset grid")
                    print("1-4: Set simulation speed")
                    print("S: Save map")
                    print("L: Load map")
                    print("O: Save obstacles")
                    print("P: Load obstacles")
                    print("H: Show this help")
                    print("================\n")

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    WIN = pygame.display.set_mode((WINDOW_WIDTH, WIDTH))
    pygame.display.set_caption("A* Navigation Simulator - Ultimate Edition with Dynamic Obstacles")
    main(WIN, WIDTH)