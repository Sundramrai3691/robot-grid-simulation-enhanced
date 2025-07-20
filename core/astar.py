import math
from queue import PriorityQueue

def heuristic(a, b):
    """Calculate heuristic distance between two spots"""
    x1, y1 = a.get_pos()
    x2, y2 = b.get_pos()
    return math.hypot(x1 - x2, y1 - y2)

def reconstruct_path(came_from, current, draw):
    """Reconstruct the path from start to end"""
    while current in came_from:
        current = came_from[current]
        if not current.is_start():  # Don't color the start node
            current.make_path()
        draw()

def a_star(draw_func, grid, start, end, known_map=None):
    """A* pathfinding algorithm implementation"""
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    # Initialize g_score and f_score for all nodes
    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}
    
    g_score[start] = 0
    f_score[start] = heuristic(start, end)
    
    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw_func)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            # Skip if using known map and neighbor is not passable
            if known_map is not None:
                neighbor_pos = (neighbor.row, neighbor.col)
                if neighbor_pos in known_map and not known_map[neighbor_pos]['is_barrier']:
                    continue
            
            # Calculate movement cost (diagonal moves cost more)
            dx = abs(current.row - neighbor.row)
            dy = abs(current.col - neighbor.col)
            step_cost = 1.41 if dx + dy == 2 else 1
            
            # Get neighbor cost (default to 1 if not available)
            neighbor_cost = getattr(neighbor, 'cost', 1)
            temp_g = g_score[current] + step_cost * neighbor_cost

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score[neighbor] = temp_g + heuristic(neighbor, end)
                neighbor.previous = current

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if not neighbor.is_end():
                        neighbor.make_open()

        draw_func()
        if current != start:
            current.make_closed()

    return False