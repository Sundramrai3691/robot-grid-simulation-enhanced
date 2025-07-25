import pygame
import time
from config.constants import *

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.target_priority = None  
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.original_color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.previous = None
        self.cost = 1
        
        # Traffic light properties
        self.is_traffic_stop = False
        self.light_state = "green"
        self.light_cycle_start = time.time()

    def get_pos(self):
        """Get the grid position of this spot"""
        return self.row, self.col
    # Add these methods to your existing Spot class:

def make_dynamic(self):
    """Make this spot a dynamic obstacle"""
    self.color = ORANGE  # Use orange color for dynamic obstacles

def is_dynamic(self):
    """Check if this spot is a dynamic obstacle"""
    return self.color == ORANGE

# Modify the existing draw method to include dynamic obstacle rendering:
def draw(self, win):
    pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    # Draw priority numbers for targets
    if self.is_end() and hasattr(self, 'priority') and self.priority:
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.priority), True, WHITE)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.width//2))
        win.blit(text, text_rect)
    
    # Draw traffic lights
    if self.is_traffic_stop:
        radius = self.width // 4
        offset = self.width // 4
        if self.light_state == "green":
            pygame.draw.circle(win, GREEN,
                               (self.x + offset, self.y + offset), radius)
        elif self.light_state == "yellow":
            pygame.draw.circle(win, YELLOW,
                               (self.x + self.width // 2, self.y + offset), radius)
        else:
            pygame.draw.circle(win, RED,
                               (self.x + self.width - offset, self.y + offset), radius)
    
    # Draw dynamic obstacle indicator (moving animation)
    if self.is_dynamic():
        import time
        # Create a pulsing effect
        pulse = int(50 * (1 + 0.5 * abs(time.time() * 2 % 2 - 1)))
        color_with_pulse = (min(255, ORANGE[0] + pulse), 
                           min(255, ORANGE[1] + pulse), 
                           min(255, ORANGE[2]))
        pygame.draw.rect(win, color_with_pulse, (self.x, self.y, self.width, self.width))
        
        # Draw movement indicator
        center_x, center_y = self.x + self.width//2, self.y + self.width//2
        pygame.draw.circle(win, WHITE, (center_x, center_y), 3)

# Modify the update_neighbors method to handle dynamic obstacles:
def update_neighbors(self, grid):
    self.neighbors = []
    dirs = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for d in dirs:
        r, c = self.row + d[0], self.col + d[1]
        if 0 <= r < self.total_rows and 0 <= c < self.total_rows:
            neighbor = grid[r][c]

            # Check if neighbor is a red traffic light or dynamic obstacle
            if neighbor.is_traffic_stop and neighbor.light_state == "red":
                continue  # Skip this neighbor if it's a red light
            
            # Dynamic obstacles block movement
            if neighbor.is_dynamic():
                continue  # Skip dynamic obstacles
            
            if not neighbor.is_barrier():
                self.neighbors.append(neighbor)

    def is_closed(self):
        """Check if this spot is in the closed set (A* algorithm)"""
        return self.color == RED

    def is_open(self):
        """Check if this spot is in the open set (A* algorithm)"""
        return self.color == GREEN

    def is_barrier(self):
        """Check if this spot is a barrier/obstacle"""
        return self.color == BLACK

    def is_start(self):
        """Check if this spot is the start position"""
        return self.color == ORANGE

    def is_end(self):
        """Check if this spot is an end/target position"""
        return self.color == TURQUOISE

    def is_dynamic(self):
        """Check if this spot is a dynamic obstacle"""
        return self.color == BLUE

    def is_target_spot(self):
        """Check if this spot is a target (alias for is_end)"""
        return self.is_end()

    def reset(self):
        """Reset the spot to its original state"""
        self.color = WHITE
        self.original_color = WHITE
        self.cost = 1
        self.previous = None
        self.target_priority = None

    def make_start(self):
        """Mark this spot as the start position"""
        self.color = ORANGE
        self.original_color = ORANGE

    def make_closed(self):
        """Mark this spot as closed (A* algorithm)"""
        self.color = RED

    def make_open(self):
        """Mark this spot as open (A* algorithm)"""
        self.color = GREEN

    def make_barrier(self):
        """Mark this spot as a barrier/obstacle"""
        self.color = BLACK
        self.original_color = BLACK

    def make_end(self):
        """Mark this spot as an end/target position"""
        self.color = TURQUOISE
        self.original_color = TURQUOISE

    def make_target(self, priority=1):
        """Mark this spot as a target with given priority"""
        self.target_priority = priority
        self.make_end()

    def make_path(self):
        """Mark this spot as part of the path"""
        self.color = PURPLE

    def make_dynamic(self):
        """Mark this spot as a dynamic obstacle"""
        self.color = BLUE
        self.original_color = BLUE

    def make_traffic_light(self):
        """Mark this spot as a traffic light"""
        self.is_traffic_stop = True
        self.light_cycle_start = time.time()
        self.update_traffic_light()

    def update_traffic_light(self):
        """Update traffic light state based on timing"""
        if not self.is_traffic_stop:
            return
            
        current_time = time.time()
        cycle_pos = ((current_time - self.light_cycle_start) % TRAFFIC_LIGHT_CYCLE) / TRAFFIC_LIGHT_CYCLE

        if cycle_pos < 0.7:  # 70% of cycle is green
            self.light_state = "green"
            self.color = GREEN
        elif cycle_pos < 0.8:  # 10% of cycle is yellow
            self.light_state = "yellow"
            self.color = YELLOW
        else:  # 20% of cycle is red
            self.light_state = "red"
            self.color = RED

    def draw(self, win):
        """Draw this spot on the window"""
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

        # Draw traffic light indicators
        if self.is_traffic_stop:
            radius = self.width // 6
            center_y = self.y + self.width // 2
            
            # Draw three circles for traffic light states
            red_center = (self.x + self.width // 4, center_y)
            yellow_center = (self.x + self.width // 2, center_y)
            green_center = (self.x + 3 * self.width // 4, center_y)
            
            # Draw inactive circles
            pygame.draw.circle(win, GRAY, red_center, radius)
            pygame.draw.circle(win, GRAY, yellow_center, radius)
            pygame.draw.circle(win, GRAY, green_center, radius)
            
            # Highlight active light
            if self.light_state == "red":
                pygame.draw.circle(win, RED, red_center, radius)
            elif self.light_state == "yellow":
                pygame.draw.circle(win, YELLOW, yellow_center, radius)
            elif self.light_state == "green":
                pygame.draw.circle(win, GREEN, green_center, radius)

    def update_neighbors(self, grid):
        """Update the list of valid neighbors for pathfinding"""
        self.neighbors = []
        # 8-directional movement (including diagonals)
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            
            # Check bounds
            if 0 <= r < self.total_rows and 0 <= c < self.total_rows:
                neighbor = grid[r][c]

                # Skip red traffic lights
                if (hasattr(neighbor, 'is_traffic_stop') and 
                    neighbor.is_traffic_stop and 
                    neighbor.light_state == "red"):
                    continue

                # Skip barriers
                if not neighbor.is_barrier():
                    self.neighbors.append(neighbor)