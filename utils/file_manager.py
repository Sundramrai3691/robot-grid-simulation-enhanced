"""
File management utilities for saving and loading maps
"""

import json
import os
from core.grid import make_grid
from config.settings import ROWS

def save_map(grid, start, end, map_name):
    """Save current map layout to file"""
    data = {
        "barriers": [spot.get_pos() for row in grid for spot in row if spot.is_barrier()],
        "traffic_lights": [spot.get_pos() for row in grid for spot in row if spot.is_traffic_stop],
        "start": start.get_pos() if start else None,
        "end": end.get_pos() if end else None
    }
    with open(f"maps/{map_name}.json", "w") as f:
        json.dump(data, f)
    print(f"Map '{map_name}' saved.")

def load_map(grid, map_name):
    """Load a named map from file"""
    filepath = f"maps/{map_name}.json"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            from config.settings import WIDTH
            new_grid = make_grid(ROWS, WIDTH)
            start = end = None
            
            for row, col in data["barriers"]:
                new_grid[row][col].make_barrier()
            for row, col in data["traffic_lights"]:
                new_grid[row][col].make_traffic_light()
            if data["start"]:
                r, c = data["start"]
                start = new_grid[r][c]
                start.make_start()
            if data["end"]:
                r, c = data["end"]
                end = new_grid[r][c]
                end.make_end()
            print(f"Map '{map_name}' loaded.")
            return new_grid, start, end
    else:
        print(f"No map found with name '{map_name}'.")
        return None

def save_obstacles(grid):
    """Save only obstacles to file"""
    with open("obstacles.json", 'w') as f:
        json.dump([[spot.get_pos() for spot in row if spot.is_barrier()] for row in grid], f)
    print("Obstacles saved.")

def load_obstacles(grid):
    """Load obstacles from file"""
    if os.path.exists("obstacles.json"):
        with open("obstacles.json", 'r') as f:
            obstacle_positions = json.load(f)
            for positions in obstacle_positions:
                for row, col in positions:
                    grid[row][col].make_barrier()
        print("Obstacles loaded.")
    else:
        print("No saved obstacles found.")