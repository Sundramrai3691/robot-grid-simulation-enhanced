import json
import os
from core.grid import make_grid
from config.settings import ROWS

def save_map(grid, start, targets, map_name):
    target_data = []
    if targets:
        for target in targets:
            target_data.append({
                'pos': target.get_pos(),
                'priority': getattr(target, 'target_priority', 1)
            })
    
    data = {
        "barriers": [spot.get_pos() for row in grid for spot in row if spot.is_barrier()],
        "traffic_lights": [spot.get_pos() for row in grid for spot in row if hasattr(spot, 'is_traffic_stop') and spot.is_traffic_stop],
        "start": start.get_pos() if start else None,
        "targets": target_data
    }
    
    with open(f"maps/{map_name}.json", "w") as f:
        json.dump(data, f)
    print(f"Map '{map_name}' saved.")

def load_map(grid, map_name):
    filepath = f"maps/{map_name}.json"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            from config.settings import WIDTH
            new_grid = make_grid(ROWS, WIDTH)
            start = None
            targets = []
            
            for row, col in data["barriers"]:
                new_grid[row][col].make_barrier()
            
            if "traffic_lights" in data:
                for row, col in data["traffic_lights"]:
                    new_grid[row][col].make_traffic_light()
            
            if data["start"]:
                r, c = data["start"]
                start = new_grid[r][c]
                start.make_start()
            
            if "targets" in data and data["targets"]:
                for target_data in data["targets"]:
                    r, c = target_data["pos"]
                    target = new_grid[r][c]
                    target.target_priority = target_data.get("priority", 1)
                    target.make_end()
                    targets.append(target)
            
            print(f"Map '{map_name}' loaded.")
            return new_grid, start, targets
    else:
        print(f"No map found with name '{map_name}'.")
        return None

def save_obstacles(grid):
    obstacles = [spot.get_pos() for row in grid for spot in row if spot.is_barrier()]
    with open("obstacles.json", 'w') as f:
        json.dump(obstacles, f)
    print("Obstacles saved.")

def load_obstacles(grid):
    if os.path.exists("obstacles.json"):
        with open("obstacles.json", 'r') as f:
            obstacles = json.load(f)
            for row, col in obstacles:
                grid[row][col].make_barrier()
        print("Obstacles loaded.")
    else:
        print("No saved obstacles found.")