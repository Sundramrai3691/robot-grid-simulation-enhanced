"""
Global settings and configuration
"""

from .constants import DEFAULT_SPEED

# Window dimensions
WIDTH = 800
ROWS = 50
SIDEBAR_WIDTH = 300
WINDOW_WIDTH = WIDTH + SIDEBAR_WIDTH

# Global variables
sim_speed = DEFAULT_SPEED
traffic_light_tool = False
current_map_name = None