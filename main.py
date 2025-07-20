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
    
    target_mode = False
    target_priority = 1
    barrier_mode = False
    traffic_light_tool = False
    
    robot_params = {
        'battery': 100,
        'sensor_range': 3,
        'speed': 1,
        'drain_rate': 1
    }

    while run:
        clock.tick(30)

        for row in grid:
            for spot in row:
                if hasattr(spot, 'is_traffic_stop') and spot.is_traffic_stop:
                    spot.update_traffic_light()

        draw(win, grid, ROWS, width,
             robot.trails if robot else [],
             robot.get_center() if robot else None, robot)

        if sim_running and robot:
            if not robot.reached_goal():
                if not robot.step():
                    if robot.battery <= 0:
                        print("Robot battery depleted!")
                        sim_running = False
            else:
                print("All targets reached!")
                sim_running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] < width:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        spot = grid[row][col]
                        
                        if target_mode:
                            if not spot.is_start() and not spot.is_barrier():
                                spot.make_end()
                                spot.target_priority = target_priority
                                targets.append(spot)
                        elif traffic_light_tool:
                            spot.make_traffic_light()
                        elif barrier_mode:
                            spot.make_barrier()
                        elif not start and not spot.is_barrier():
                            start = spot
                            start.make_start()
                        elif spot != start:
                            spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] < width:
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and targets:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    robot = Robot(start, targets, grid,
                                  lambda: draw(win, grid, ROWS, width, robot.trails, robot.get_center(), robot),
                                  **robot_params)
                    robot.plan_path()
                    sim_running = True
                    
                elif event.key == pygame.K_c:
                    grid = make_grid(ROWS, width)
                    start = None
                    targets = []
                    robot = None
                    sim_running = False
                    
                elif event.key == pygame.K_r:
                    if robot:
                        robot.current = start
                        robot.trails = []
                        robot.index = 0
                        robot.completed_targets = []
                        robot.current_target = None
                        robot.battery = robot.max_battery
                        robot.plan_path()
                        sim_running = True
                    
                elif event.key == pygame.K_o:
                    save_obstacles(grid)
                    
                elif event.key == pygame.K_p:
                    load_obstacles(grid)
                    
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    speed_index = event.key - pygame.K_1
                    sim_speed = [0.1, 0.3, 0.5, 1.0][speed_index]
                    robot_params['speed'] = sim_speed
                    if robot:
                        robot.speed_multiplier = sim_speed

                elif event.key == pygame.K_t:
                    traffic_light_tool = not traffic_light_tool
                    target_mode = False
                    barrier_mode = False

                elif event.key == pygame.K_m:
                    target_mode = not target_mode
                    traffic_light_tool = False
                    barrier_mode = False

                elif event.key == pygame.K_b:
                    barrier_mode = not barrier_mode
                    traffic_light_tool = False
                    target_mode = False

                elif event.key == pygame.K_s:
                    map_name = get_text_input("Enter a name for this map:", "Save Map")
                    if map_name:
                        save_map(grid, start, targets, map_name)

                elif event.key == pygame.K_l:
                    map_name = get_text_input("Enter the name of the map to load:", "Load Map")
                    if map_name:
                        result = load_map(grid, map_name)
                        if result:
                            grid, start, loaded_targets = result
                            targets = loaded_targets if loaded_targets else []

                elif target_mode and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    target_priority = event.key - pygame.K_0

                elif event.key == pygame.K_q:
                    run = False

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH + SIDEBAR_WIDTH, WIDTH))
    pygame.display.set_caption("A* Navigation Simulator")
    sim_speed = DEFAULT_SPEED
    traffic_light_tool = False
    main(WIN, WIDTH)