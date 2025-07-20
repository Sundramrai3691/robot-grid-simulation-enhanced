"""
A* pathfinding algorithm implementation
"""

import math
from queue import PriorityQueue

def heuristic(a, b):
    """Calculate heuristic distance between two points"""
    x1, y1 = a.get_pos()
    x2, y2 = b.get_pos()
    return math.hypot(x1 - x2, y1 - y2)

def reconstruct_path(came_from, current, draw):
    """Reconstruct the path from start to end"""
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def a_star(draw_func, grid, start, end):
    """A* pathfinding algorithm"""
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
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
            dx = abs(current.row - neighbor.row)
            dy = abs(current.col - neighbor.col)
            step_cost = 1.41 if dx + dy == 2 else 1
            temp_g = g_score[current] + step_cost * neighbor.cost

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score[neighbor] = temp_g + heuristic(neighbor, end)
                neighbor.previous = current

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        draw_func()
        if current != start:
            current.make_closed()

    return False