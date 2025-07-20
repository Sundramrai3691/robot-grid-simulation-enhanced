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
    start = robot = None
    barrier_mode = False
    traffic_light_tool = False
    click_count = 0
    barrier_placed = False 
    priority_counter = 1
    targets = []
    run = True
    clock = pygame.time.Clock()
    sim_running = False

    while run:
        clock.tick(30)

        # Update traffic lights
        for row in grid:
            for spot in row:
                if spot.is_traffic_stop:
                    spot.update_traffic_light()

        draw(win, grid, ROWS, width,
             robot.trails if robot else [],
             robot.get_center() if robot else None,
             robot,
             barrier_mode)

        if sim_running and robot:
            if not robot.reached_goal():
                robot.step()
            elif targets:
                robot.start = robot.current  # Continue from last position
                _, next_target = targets.pop(0)
                robot.set_new_goal(next_target)
                robot.plan_path()
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
                        print("Traffic light tool: OFF")
                        print("Barrier mode: OFF")

                    elif not barrier_placed:  # ✅ Prevent placing targets after barrier
                        if click_count == 0:
                            start = spot
                            start.make_start()
                            click_count = 1
                        elif spot != start and spot not in [t[1] for t in targets]:
                            spot.priority = priority_counter  # ✅ Set priority before incrementing
                            targets.append((priority_counter, spot))
                            spot.make_end()
                            priority_counter += 1  # ✅ increment after use

            elif pygame.mouse.get_pressed()[2]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]
                    if spot == start:
                        start = None
                        click_count = 0
                    spot.reset()
                    spot.is_traffic_stop = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    if start and targets:
                        _, current_target = targets.pop(0)
                        robot = Robot(start, current_target, grid,
                                      lambda: draw(win, grid, ROWS, width,
                                                   robot.trails,
                                                   robot.get_center(),
                                                   robot, barrier_mode))
                        robot.plan_path()
                        sim_running = True

                if event.key == pygame.K_b:
                    barrier_mode = True
                    traffic_light_tool = False
                    print("Barrier mode: ON")

                if event.key == pygame.K_t:
                    traffic_light_tool = True
                    barrier_mode = False
                    print("Traffic light tool: ON")
                    print("Barrier mode: OFF")

                if event.key == pygame.K_c or event.key == pygame.K_r:
                    grid = make_grid(ROWS, width)
                    start = robot = None
                    sim_running = False
                    click_count = 0
                    priority_counter = 1
                    targets.clear()
                    barrier_mode = False
                    traffic_light_tool = False
                    barrier_placed = False  # ✅ Reset this too

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

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    WIN = pygame.display.set_mode((WINDOW_WIDTH, WIDTH))
    pygame.display.set_caption("A* Navigation Simulator - Ultimate Edition")
    main(WIN, WIDTH)
