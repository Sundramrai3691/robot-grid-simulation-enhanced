import pygame
import time
import math
from config.constants import *
from config.settings import *
from entities.trail import TrailMarker
from .astar import a_star

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
        
        # Robot parameters
        self.battery = params.get('battery', DEFAULT_BATTERY)
        self.max_battery = self.battery
        self.sensor_range = params.get('sensor_range', DEFAULT_SENSOR_RANGE)
        self.speed_multiplier = params.get('speed', DEFAULT_ROBOT_SPEED)
        self.battery_drain_rate = params.get('drain_rate', BATTERY_DRAIN_RATE)
        
        # Statistics
        self.distance_traveled = 0
        self.steps_taken = 0
        self.replan_count = 0
        self.known_map = {}

    def select_next_target(self):
        """Select the next target with highest priority that hasn't been completed"""
        for target in self.targets:
            if target not in self.completed_targets:
                if self.test_reachability(target):
                    self.current_target = target
                    return target
        return None

    def test_reachability(self, target):
        """Test if a target is reachable (placeholder implementation)"""
        return True

    def update_perception(self):
        """Update robot's knowledge of the environment within sensor range"""
        if not self.current:
            return
            
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
                        'cost': getattr(spot, 'cost', 1)
                    }

    def recharge_battery(self, amount=None):
        """Recharge the robot's battery"""
        if amount is None:
            self.battery = self.max_battery
        else:
            self.battery = min(self.max_battery, self.battery + amount)

    def plan_path(self):
        """Plan a path to the current target using A* algorithm"""
        if not self.current_target:
            self.current_target = self.select_next_target()
        
        if not self.current_target:
            return False
            
        # Reset grid for pathfinding
        for row in self.grid:
            for spot in row:
                if not spot.is_barrier() and not spot.is_start() and not spot.is_end():
                    spot.reset()
                spot.previous = None
        
        self.path.clear()
        self.index = 0
        
        # Run A* algorithm
        if a_star(self.draw, self.grid, self.start, self.current_target):
            self.extract_path()
            return True
        else:
            # If no path found, mark target as completed and try next
            self.completed_targets.append(self.current_target)
            self.current_target = None
            self.replan_count += 1
            return self.plan_path()

    def extract_path(self):
        """Extract the path from A* result"""
        current = self.current_target
        path = []
        while hasattr(current, 'previous') and current.previous and current != self.start:
            path.append(current)
            current = current.previous
        path.append(self.start)
        path.reverse()
        self.path = path

    def step(self):
        """Execute one step of robot movement"""
        if self.battery <= 0:
            return False
        
        self.update_perception()
        current_time = time.time()

        # Handle pause state (e.g., waiting at traffic light)
        if self.paused:
            if current_time - self.pause_time >= PAUSE_DURATION:
                self.paused = False
            return False

        # Check if enough time has passed for next move
        move_interval = (MOVE_DELAY / DEFAULT_SPEED) / self.speed_multiplier
        if current_time - self.last_move_time < move_interval:
            return True

        self.last_move_time = current_time

        # Execute movement if path exists
        if self.index < len(self.path):
            next_spot = self.path[self.index]

            # Check for traffic light
            if (hasattr(next_spot, 'is_traffic_stop') and 
                next_spot.is_traffic_stop and 
                next_spot.light_state != "green"):
                self.paused = True
                self.pause_time = current_time
                return False

            # Check for obstacles
            if (next_spot.is_barrier() or 
                (hasattr(next_spot, 'is_dynamic') and next_spot.is_dynamic())):
                self.replan_count += 1
                self.plan_path()
                return False

            # Add trail marker
            self.trails.append(TrailMarker(
                (self.current.x + self.current.width // 2,
                 self.current.y + self.current.width // 2),
                (*PURPLE, TRAIL_ALPHA),
                self.current.width
            ))

            # Update trail markers
            for trail in self.trails[:]:
                trail.update()
                if trail.lifetime <= 0:
                    self.trails.remove(trail)

            # Move to next position
            if self.current != self.start:  # Don't reset start position
                self.current.reset()
            self.current = next_spot
            self.current.make_start()
            self.index += 1
            
            # Update statistics
            self.battery -= self.battery_drain_rate
            self.steps_taken += 1
            if self.index > 0:
                self.distance_traveled += 1
                
            return True
        return False

    def reached_goal(self):
        """Check if robot has reached the current target"""
        if self.current == self.current_target:
            self.completed_targets.append(self.current_target)
            self.current_target = None
            return len(self.completed_targets) == len(self.targets)
        return False

    def get_center(self):
        """Get the center position of the robot"""
        if not self.current:
            return (0, 0)
        return (self.current.x + self.current.width // 2,
                self.current.y + self.current.width // 2)

    def set_new_goal(self, new_goal):
        """Set a new goal for the robot"""
        self.current_target = new_goal
        self.trails.append(TrailMarker(
            self.get_center(), (*PURPLE, TRAIL_ALPHA), self.current.width
        ))