import json
import os
from datetime import datetime
from core.grid import make_grid
from config.settings import ROWS, WIDTH
from entities.dynamic_obstacle import DynamicObstacle

def ensure_directories():
    """Ensure required directories exist"""
    directories = ["maps", "saves", "exports"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def save_map(grid, start, targets, map_name, dynamic_obstacles=None, robot_params=None):
    """Save complete map state including all elements"""
    ensure_directories()
    
    # Collect target data with priorities
    target_data = []
    if targets:
        for target in targets:
            target_data.append({
                'pos': target.get_pos(),
                'priority': getattr(target, 'target_priority', 1)
            })
    
    # Collect dynamic obstacles data
    obstacle_data = []
    if dynamic_obstacles:
        for obstacle in dynamic_obstacles:
            path_positions = [spot.get_pos() for spot in obstacle.path]
            obstacle_data.append({
                'name': obstacle.name,
                'path': path_positions,
                'speed': obstacle.speed,
                'current_index': obstacle.index
            })
    
    # Collect traffic lights data
    traffic_lights = []
    for row in grid:
        for spot in row:
            if hasattr(spot, 'is_traffic_stop') and spot.is_traffic_stop:
                traffic_lights.append({
                    'pos': spot.get_pos(),
                    'state': spot.light_state,
                    'cycle_start': spot.light_cycle_start
                })
    
    # Create comprehensive save data
    data = {
        "version": "1.1",
        "created": datetime.now().isoformat(),
        "grid_size": len(grid),
        "barriers": [spot.get_pos() for row in grid for spot in row if spot.is_barrier()],
        "traffic_lights": traffic_lights,
        "dynamic_obstacles": obstacle_data,
        "start": start.get_pos() if start else None,
        "targets": target_data,
        "robot_params": robot_params or {
            "battery": 100,
            "sensor_range": 3,
            "speed": 1,
            "drain_rate": 1
        }
    }
    
    # Save to file
    filepath = f"maps/{map_name}.json"
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Map '{map_name}' saved successfully to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving map '{map_name}': {e}")
        return False

def load_map(grid, map_name):
    """Load complete map state including all elements"""
    filepath = f"maps/{map_name}.json"
    
    if not os.path.exists(filepath):
        print(f"Map file '{filepath}' not found.")
        return None
    
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        
        # Create new grid
        new_grid = make_grid(ROWS, WIDTH)
        start = None
        targets = []
        dynamic_obstacles = []
        robot_params = data.get("robot_params", {})
        
        # Load barriers
        for row, col in data.get("barriers", []):
            if 0 <= row < len(new_grid) and 0 <= col < len(new_grid[0]):
                new_grid[row][col].make_barrier()
        
        # Load traffic lights
        for traffic_light in data.get("traffic_lights", []):
            row, col = traffic_light["pos"]
            if 0 <= row < len(new_grid) and 0 <= col < len(new_grid[0]):
                spot = new_grid[row][col]
                spot.make_traffic_light()
                spot.light_state = traffic_light.get("state", "green")
                spot.light_cycle_start = traffic_light.get("cycle_start", 0)
        
        # Load dynamic obstacles
        for obstacle_data in data.get("dynamic_obstacles", []):
            path_spots = []
            for row, col in obstacle_data["path"]:
                if 0 <= row < len(new_grid) and 0 <= col < len(new_grid[0]):
                    path_spots.append(new_grid[row][col])
            
            if path_spots:
                obstacle = DynamicObstacle(
                    path=path_spots,
                    name=obstacle_data.get("name", "obstacle"),
                    speed=obstacle_data.get("speed", 1)
                )
                obstacle.index = obstacle_data.get("current_index", 0)
                dynamic_obstacles.append(obstacle)
        
        # Load start position
        if data.get("start"):
            r, c = data["start"]
            if 0 <= r < len(new_grid) and 0 <= c < len(new_grid[0]):
                start = new_grid[r][c]
                start.make_start()
        
        # Load targets
        for target_data in data.get("targets", []):
            r, c = target_data["pos"]
            if 0 <= r < len(new_grid) and 0 <= c < len(new_grid[0]):
                target = new_grid[r][c]
                target.target_priority = target_data.get("priority", 1)
                target.make_end()
                targets.append(target)
        
        print(f"Map '{map_name}' loaded successfully.")
        return new_grid, start, targets, dynamic_obstacles, robot_params
        
    except Exception as e:
        print(f"Error loading map '{map_name}': {e}")
        return None

def save_obstacles(grid, filename="obstacles.json"):
    """Save only obstacle positions to file"""
    ensure_directories()
    
    obstacles = {
        "barriers": [spot.get_pos() for row in grid for spot in row if spot.is_barrier()],
        "traffic_lights": [spot.get_pos() for row in grid for spot in row 
                          if hasattr(spot, 'is_traffic_stop') and spot.is_traffic_stop],
        "dynamic": [spot.get_pos() for row in grid for spot in row if spot.is_dynamic()]
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(obstacles, f, indent=2)
        print(f"Obstacles saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving obstacles: {e}")
        return False

def load_obstacles(grid, filename="obstacles.json"):
    """Load obstacle positions from file"""
    if not os.path.exists(filename):
        print(f"Obstacle file '{filename}' not found.")
        return False
    
    try:
        with open(filename, 'r') as f:
            obstacles = json.load(f)
        
        # Load barriers
        for row, col in obstacles.get("barriers", []):
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                grid[row][col].make_barrier()
        
        # Load traffic lights
        for row, col in obstacles.get("traffic_lights", []):
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                grid[row][col].make_traffic_light()
        
        # Load dynamic obstacles
        for row, col in obstacles.get("dynamic", []):
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                grid[row][col].make_dynamic()
        
        print(f"Obstacles loaded from {filename}")
        return True
    except Exception as e:
        print(f"Error loading obstacles: {e}")
        return False

def export_simulation_data(robot, dynamic_obstacles=None, filename=None):
    """Export simulation statistics and performance data"""
    ensure_directories()
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/simulation_{timestamp}.json"
    
    # Collect robot statistics
    robot_data = {
        "battery_remaining": robot.battery,
        "max_battery": robot.max_battery,
        "steps_taken": robot.steps_taken,
        "distance_traveled": robot.distance_traveled,
        "replan_count": robot.replan_count,
        "targets_completed": len(robot.completed_targets),
        "total_targets": len(robot.targets),
        "sensor_range": robot.sensor_range,
        "speed_multiplier": robot.speed_multiplier,
        "battery_drain_rate": robot.battery_drain_rate
    }
    
    # Collect dynamic obstacle data
    obstacle_data = []
    if dynamic_obstacles:
        for obstacle in dynamic_obstacles:
            obstacle_data.append({
                "name": obstacle.name,
                "speed": obstacle.speed,
                "path_length": len(obstacle.path),
                "current_position": obstacle.index
            })
    
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "robot_stats": robot_data,
        "dynamic_obstacles": obstacle_data,
        "simulation_summary": {
            "success_rate": len(robot.completed_targets) / len(robot.targets) if robot.targets else 0,
            "efficiency": robot.distance_traveled / max(robot.steps_taken, 1),
            "battery_usage": (robot.max_battery - robot.battery) / robot.max_battery
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"Simulation data exported to {filename}")
        return filename
    except Exception as e:
        print(f"Error exporting simulation data: {e}")
        return None

def list_available_maps():
    """Get list of available map files"""
    ensure_directories()
    
    if not os.path.exists("maps"):
        return []
    
    maps = []
    for filename in os.listdir("maps"):
        if filename.endswith(".json"):
            map_name = filename[:-5]  # Remove .json extension
            filepath = os.path.join("maps", filename)
            
            try:
                # Get file modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                maps.append({
                    "name": map_name,
                    "filename": filename,
                    "modified": mod_time.strftime("%Y-%m-%d %H:%M")
                })
            except Exception as e:
                print(f"Error reading map {filename}: {e}")
    
    return sorted(maps, key=lambda x: x["modified"], reverse=True)

def delete_map(map_name):
    """Delete a map file"""
    filepath = f"maps/{map_name}.json"
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"Map '{map_name}' deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting map '{map_name}': {e}")
            return False
    else:
        print(f"Map '{map_name}' not found.")
        return False

def backup_map(map_name):
    """Create a backup copy of a map"""
    ensure_directories()
    
    source_path = f"maps/{map_name}.json"
    if not os.path.exists(source_path):
        print(f"Map '{map_name}' not found.")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"saves/{map_name}_backup_{timestamp}.json"
    
    try:
        with open(source_path, 'r') as source:
            data = json.load(source)
        
        with open(backup_path, 'w') as backup:
            json.dump(data, backup, indent=2)
        
        print(f"Map '{map_name}' backed up to {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Error backing up map '{map_name}': {e}")
        return False