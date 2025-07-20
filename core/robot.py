import pygame
import time
import math
from config.constants import *
from config.settings import *
from entities.trail import TrailMarker
from .astar import a_star

DEFAULT_BATTERY = 100
DEFAULT_SENSOR_RANGE = 3
DEFAULT_ROBOT_SPEED = 1
BATTERY_DRAIN_RATE = 1
SPEED_MULTIPLIERS = [0.1, 0.3, 0.5, 1.0]

class Robot:
    def __init__(self, start, targets, grid, draw_func, **params):
        self.grid = grid
        self.draw = draw_func
        self.start = start
        self.targets = sorted(targets, key=lambda t: getattr(t, 'target_priority', 1), reverse=True) if targets else []
        self.current_target = None
        self.completed_targets = []
        self.path = []
        self.index = 0
        self.current = start
        self.trails = []
        self.last_move_time = time.time()
        self.paused = False
        self.pause_time = 0
        
        self.battery = params.get('battery', DEFAULT_BATTERY)
        self.max_battery = self.battery
        self.sensor_range = params.get('sensor_range', DEFAULT_SENSOR_RANGE)
        self.speed_multiplier = params.get('speed', DEFAULT_ROBOT_SPEED)
        self.battery_drain_rate = params.get('drain_rate', BATTERY_DRAIN_RATE)
        
        self.distance_traveled = 0
        self.steps_taken = 0
        self.replan_count = 0
        self.known_map = {}

    def select_next_target(self):
        for target in self.targets:
            if target not in self.completed_targets:
                if self.test_reachability(target):
                    self.current_target = target
                    return target
        return None

    def test_reachability(self, target):
        return True

    def update_perception(self):
        current_pos = self.current.get_pos()
        
        for row in range(max(0, current_pos[0] - self.sensor_range),
                        min(len(self.grid), current_pos[0] + self.sensor_range + 1)):
            for col in range(max(0, current_pos[1] - self.sensor_range),
                           min(len(self.grid[0]), current_pos[1] + self.sensor_range + 1)):
                distance = math.sqrt((row - current_pos[0])**2 + (col - current_pos[1])**2)
                if distance <= self.sensor_range:
                    spot = self.grid[row][col]
                    self.known_map[(row, col)] = {
                        'is_barrier': spot.is_barrier(),
                        'is_dynamic': getattr(spot, 'is_dynamic', lambda: False)(),
                        'cost': spot.cost
                    }

    def recharge_battery(self, amount=None):
        if amount is None:
            self.battery = self.max_battery
        else:
            self.battery = min(self.max_battery, self.battery + amount)

    def plan_path(self):
        if not self.current_target:
            self.current_target = self.select_next_target()
        
        if not self.current_target:
            return False
            
        for row in self.grid:
            for spot in row:
                if not spot.is_barrier() and not spot.is_start() and not hasattr(spot, 'is_target_spot') or not spot.is_target_spot():
                    spot.reset()
                spot.previous = None
        
        self.path.clear()
        self.index = 0
        
        if a_star(self.draw, self.grid, self.start, self.current_target):
            self.extract_path()
            return True
        else:
            self.completed_targets.append(self.current_target)
            self.current_target = None
            self.replan_count += 1
            return self.plan_path()

    def extract_path(self):
        current = self.current_target
        path = []
        while hasattr(current, 'previous') and current.previous and current != self.start:
            path.append(current)
            current = current.previous
        path.append(self.start)
        path.reverse()
        self.path = path

    def step(self):
        if self.battery <= 0:
            return False
        
        self.update_perception()
        current_time = time.time()

        if self.paused:
            if current_time - self.pause_time >= 2:
                self.paused = False
            return False

        if current_time - self.last_move_time < (0.4 / DEFAULT_SPEED) / self.speed_multiplier:
            return True

        self.last_move_time = current_time

        if self.index < len(self.path):
            next_spot = self.path[self.index]

            if hasattr(next_spot, 'is_traffic_stop') and next_spot.is_traffic_stop and next_spot.light_state != "green":
                self.paused = True
                self.pause_time = current_time
                return False

            if next_spot.is_barrier() or (hasattr(next_spot, 'is_dynamic') and next_spot.is_dynamic()):
                self.replan_count += 1
                self.plan_path()
                return False

            self.trails.append(TrailMarker(
                (self.current.x + self.current.width // 2,
                 self.current.y + self.current.width // 2),
                (*PURPLE, TRAIL_ALPHA),
                self.current.width
            ))

            for trail in self.trails[:]:
                trail.update()
                if trail.lifetime <= 0:
                    self.trails.remove(trail)

            self.current.reset()
            self.current = next_spot
            self.current.make_start()
            self.index += 1
            
            self.battery -= self.battery_drain_rate
            self.steps_taken += 1
            if self.index > 0:
                self.distance_traveled += 1
                
            return True
        return False

    def reached_goal(self):
        if self.current == self.current_target:
            self.completed_targets.append(self.current_target)
            self.current_target = None
            return len(self.completed_targets) == len(self.targets)
        return False

    def get_center(self):
        return (self.current.x + self.current.width // 2,
                self.current.y + self.current.width // 2)

    def set_new_goal(self, new_goal):
        self.current_target = new_goal
        self.trails.append(TrailMarker(
            self.get_center(), (*PURPLE, TRAIL_ALPHA), self.current.width
        ))