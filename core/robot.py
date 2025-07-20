""" Robot class for pathfinding and movement """
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
        # ✅ Track completed targets with priorities
        self.completed_targets = []
        
    def set_new_goal(self, new_goal):
        # ✅ Mark previous goal as completed
        if hasattr(self.end, 'priority') and self.end.priority:
            self.completed_targets.append((self.end.priority, self.end))
            print(f"✅ Target {self.end.priority} completed!")
        
        self.end = new_goal
        self.trails.append(TrailMarker(
            self.get_center(), (*PURPLE, TRAIL_ALPHA), self.current.width
        ))
        print(f"🎯 New target: Priority {getattr(new_goal, 'priority', 'Unknown')}")

    def plan_path(self):
        """Plan a path from current position to end using A*"""
        for row in self.grid:
            for spot in row:
                if not spot.is_barrier() and not spot.is_start() and not spot.is_end() and not spot.is_dynamic():
                    spot.reset()
                spot.previous = None
        self.path.clear()
        self.index = 0
        
        # ✅ Update neighbors to account for dynamic obstacles
        for row in self.grid:
            for spot in row:
                spot.update_neighbors(self.grid)
        
        if a_star(self.draw, self.grid, self.current, self.end):  # Use current position, not start
            self.extract_path()
            return True
        else:
            self.draw_fail_overlay()
            return False

    def draw_fail_overlay(self):
        """Draw overlay when pathfinding fails"""
        print("⚠️ Pathfinding failed - no valid path found!")
        # Could add visual feedback here if needed

    def extract_path(self):
        """Extract the path from the A* result"""
        current = self.end
        path = []
        while hasattr(current, 'previous') and current.previous and current != self.current:  # Changed from self.start
            path.append(current)
            current = current.previous
        path.append(self.current)  # Changed from self.start
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

            # ✅ Check for traffic lights
            if next_spot.is_traffic_stop and next_spot.light_state != "green":
                self.paused = True
                self.pause_time = current_time
                print(f"🚦 Waiting for {next_spot.light_state} light to turn green...")
                return False

            # ✅ Check for dynamic obstacles or new barriers - replan if found
            if next_spot.is_barrier() or next_spot.is_dynamic():
                print("🚧 Path blocked! Replanning...")
                if not self.plan_path():  # Try to replan
                    print("❌ Cannot find alternative path!")
                    return False
                return False  # Skip this step, try again with new path

            # ✅ Add trail marker
            self.trails.append(TrailMarker(
                (self.current.x + self.current.width // 2,
                 self.current.y + self.current.width // 2),
                (*PURPLE, TRAIL_ALPHA),
                self.current.width // 4
            ))

            # ✅ Update all trail markers
            for trail in self.trails:
                trail.update()

            # ✅ Move to next position
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
    
    # ✅ New method to get completion status
    def get_completion_status(self):
        """Get information about completed targets"""
        return {
            'completed_count': len(self.completed_targets),
            'completed_priorities': [priority for priority, _ in self.completed_targets],
            'current_target_priority': getattr(self.end, 'priority', None)
        }