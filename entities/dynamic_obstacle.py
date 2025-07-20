"""
Dynamic obstacles that move around the grid
"""
import random
import time
from config.constants import *

class DynamicObstacle:
    def __init__(self, row, col, grid):
        self.row = row
        self.col = col
        self.grid = grid
        self.last_move_time = time.time()
        self.move_interval = random.uniform(1.0, 3.0)  # Move every 1-3 seconds
        self.direction = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
        self.id = f"dynamic_{row}_{col}_{int(time.time())}"
        
        # Mark the initial position as dynamic
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            grid[row][col].make_dynamic()
    
    def update(self):
        """Update the obstacle position"""
        current_time = time.time()
        
        if current_time - self.last_move_time >= self.move_interval:
            self.move()
            self.last_move_time = current_time
            self.move_interval = random.uniform(1.0, 3.0)  # Random next interval
    
    def move(self):
        """Move the obstacle to a new position"""
        # Clear current position
        if 0 <= self.row < len(self.grid) and 0 <= self.col < len(self.grid[0]):
            current_spot = self.grid[self.row][self.col]
            if current_spot.is_dynamic():
                current_spot.reset()
        
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
                
                # Check if the new position is valid (not barrier, start, end, or another dynamic)
                if (not new_spot.is_barrier() and 
                    not new_spot.is_start() and 
                    not new_spot.is_end() and 
                    not new_spot.is_dynamic() and
                    not new_spot.is_traffic_stop):
                    
                    # Move to new position
                    self.row = new_row
                    self.col = new_col
                    new_spot.make_dynamic()
                    return
            
            # If current direction doesn't work, try a random one
            self.direction = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
            attempts += 1

class DynamicObstacleManager:
    def __init__(self):
        self.obstacles = []
    
    def add_obstacle(self, row, col, grid):
        """Add a new dynamic obstacle"""
        obstacle = DynamicObstacle(row, col, grid)
        self.obstacles.append(obstacle)
        return obstacle
    
    def remove_obstacle(self, obstacle):
        """Remove a dynamic obstacle"""
        # Clear its position
        if 0 <= obstacle.row < len(obstacle.grid) and 0 <= obstacle.col < len(obstacle.grid[0]):
            spot = obstacle.grid[obstacle.row][obstacle.col]
            if spot.is_dynamic():
                spot.reset()
        
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
            if 0 <= obstacle.row < len(obstacle.grid) and 0 <= obstacle.col < len(obstacle.grid[0]):
                spot = obstacle.grid[obstacle.row][obstacle.col]
                if spot.is_dynamic():
                    spot.reset()
        self.obstacles.clear()
    
    def get_obstacle_count(self):
        """Get the number of active obstacles"""
        return len(self.obstacles)