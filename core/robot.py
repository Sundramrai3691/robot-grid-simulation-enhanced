"""
Robot class for pathfinding and movement
"""

import pygame
import time
from config.constants import *
from config.settings import *
from entities.trail import TrailMarker
from .astar import a_star

class Robot:
    def __init__(self, start, end, grid, draw_func):
        self.grid = grid
        self.draw = draw_func
        self.start = start
        self.end = end
        self.path = []
        self.index = 0
        self.current = start
        self.trails = []
        self.last_move_time = time.time()
        self.paused = False
        self.pause_time = 0

    

    def set_new_goal(self, new_goal):
        self.end = new_goal
        self.trails.append(TrailMarker(
            self.get_center(), (*PURPLE, TRAIL_ALPHA), self.current.width
        ))



    def plan_path(self):
        """Plan a path from start to end using A*"""
        for row in self.grid:
            for spot in row:
                if not spot.is_barrier() and not spot.is_start() and not spot.is_end():
                    spot.reset()
                spot.previous = None
        self.path.clear()
        self.index = 0
        if a_star(self.draw, self.grid, self.start, self.end):
            self.extract_path()
        else:
            self.draw_fail_overlay()

    def draw_fail_overlay(self):
        """Draw overlay when pathfinding fails"""
        from config.settings import WIDTH, ROWS
        for _ in range(3):
            for row in self.grid:
                for spot in row:
                    if not spot.is_barrier():
                        # Note: WIN needs to be passed or accessed differently
                        pass  # This will need to be handled in the calling code
            time.sleep(0.2)

    def extract_path(self):
        """Extract the path from the A* result"""
        current = self.end
        path = []
        while hasattr(current, 'previous') and current.previous and current != self.start:
            path.append(current)
            current = current.previous
        path.append(self.start)
        path.reverse()
        self.path = path

    def step(self):
        current_time = time.time()

        if self.paused:
            if current_time - self.pause_time >= 2:
                self.paused = False
            return False

        if current_time - self.last_move_time < 0.4 / DEFAULT_SPEED:
            return True

        self.last_move_time = current_time

        if self.index < len(self.path):
            next_spot = self.path[self.index]

            if next_spot.is_traffic_stop and next_spot.light_state != "green":
                self.paused = True
                self.pause_time = current_time
                return False

            if next_spot.is_barrier() or next_spot.is_dynamic():
                self.plan_path()
                return False

            self.trails.append(TrailMarker(
                (self.current.x + self.current.width // 2,
                self.current.y + self.current.width // 2),
                (*PURPLE, TRAIL_ALPHA),
                self.current.width // 4
            ))

            for trail in self.trails:
                trail.update()

            self.current.reset()
            self.current = next_spot
            self.current.make_start()
            self.index += 1
            return True
        return False


    def reached_goal(self):
        """Check if robot has reached the goal"""
        return self.current == self.end
    


    def get_center(self):
        """Get the center position of the robot"""
        return (self.current.x + self.current.width // 2,
                self.current.y + self.current.width // 2)