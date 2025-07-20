"""
Dynamic obstacles that move around the grid
"""
import random
import time
from config.constants import *

class DynamicObstacle:
    def __init__(self, row=None, col=None, grid=None, path=None, name="Dynamic Obstacle", speed=1):
        if path:
            # Path-based obstacle
            self.path = path
            self.row = path[0].row if path else row
            self.col = path[0].col if path else col
            self.grid = path[0].grid if hasattr(path[0], 'grid') else grid
            self.index = 0
            self.current = path[0] if path else None
        else:
            # Random movement obstacle
            self.row = row
            self.col = col
            self.grid = grid
            self.path = []
            self.index = 0
            self.current = grid[row][col] if grid and 0 <= row < len(grid) and 0 <= col < len(grid[0]) else None
        
        self.name = name
        self.speed = speed
        self.last_move_time = time.time()
        self.move_interval = random.uniform(1.0, 3.0) / speed  # Move interval affected by speed
        self.direction = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
        self.id = f"dynamic_{row}_{col}_{int(time.time())}"
        
        # Mark the initial position as dynamic
        if self.current:
            self.current.make_dynamic()
    
    def update(self):
        """Update the obstacle position"""
        current_time = time.time()
        
        if current_time - self.last_move_time >= self.move_interval:
            self.move()
            self.last_move_time = current_time
            self.move_interval = random.uniform(1.0, 3.0) / self.speed
    
    def move(self):
        """Move the obstacle to a new position"""
        if self.path:
            self._move_along_path()
        else:
            self._move_randomly()
    
    def _move_along_path(self):
        """Move along predefined path"""
        if not self.path:
            return
        
        # Clear current position
        if self.current and self.current.is_dynamic():
            self.current.reset()
        
        # Move to next position in path
        self.index = (self.index + 1) % len(self.path)
        self.current = self.path[self.index]
        self.row = self.current.row
        self.col = self.current.col
        
        # Only mark as dynamic if it's not a barrier, start, or end
        if (not self.current.is_barrier() and 
            not self.current.is_start() and 
            not self.current.is_end() and
            not self.current.is_traffic_stop):
            self.current.make_dynamic()
    
    def _move_randomly(self):
        """Move randomly around the grid"""
        if not self.grid:
            return
            
        # Clear current position
        if self.current and self.current.is_dynamic():
            self.current.reset()
        
        # Try to find a valid new position
        attempts = 0
        while attempts < 8:  # Try 8 different directions
            # Randomly change direction sometimes
            if random.random() < 0.3:
                self.direction = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
            
            new_row = self.row + self.direction[0]
            new_col = self.col + self.direction[1]
            
            # Check bounds
            if 0 <= new_row < len(self.grid) and 0 <= new_col < len(self.grid[0]):
                new_spot = self.grid[new_row][new_col]
                
                # Check if the new position is valid
                if (not new_spot.is_barrier() and 
                    not new_spot.is_start() and 
                    not new_spot.is_end() and 
                    not new_spot.is_dynamic() and
                    not new_spot.is_traffic_stop):
                    
                    # Move to new position
                    self.row = new_row
                    self.col = new_col
                    self.current = new_spot
                    new_spot.make_dynamic()
                    return
            
            # If current direction doesn't work, try a random one
            self.direction = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
            attempts += 1

class DynamicObstacleManager:
    def __init__(self):
        self.obstacles = []
    
    def add_obstacle(self, row=None, col=None, grid=None, path=None, name=None, speed=1):
        """Add a new dynamic obstacle"""
        if name is None:
            name = f"Obstacle {len(self.obstacles) + 1}"
        
        obstacle = DynamicObstacle(row, col, grid, path, name, speed)
        self.obstacles.append(obstacle)
        return obstacle
    
    def remove_obstacle(self, obstacle):
        """Remove a dynamic obstacle"""
        # Clear its position
        if obstacle.current and obstacle.current.is_dynamic():
            obstacle.current.reset()
        
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
    
    def update_all(self):
        """Update all dynamic obstacles"""
        for obstacle in self.obstacles:
            obstacle.update()
    
    def clear_all(self):
        """Clear all dynamic obstacles"""
        for obstacle in self.obstacles:
            # Clear their positions
            if obstacle.current and obstacle.current.is_dynamic():
                obstacle.current.reset()
        self.obstacles.clear()
    
    def get_obstacle_count(self):
        """Get the number of active obstacles"""
        return len(self.obstacles)
    
    def get_obstacles(self):
        """Get all obstacles"""
        return self.obstacles