"""
Dynamic obstacle system
"""

import time

class DynamicObstacle:
    def __init__(self, path, name="obstacle", speed=1):
        self.path = path
        self.index = 0
        self.name = name
        self.current = None
        self.speed = speed
        self.cycle_time = time.time()

    def move(self):
        """Move the dynamic obstacle along its path"""
        current_time = time.time()
        if current_time - self.cycle_time >= 0.4 / self.speed:
            self.cycle_time = current_time
            if self.current:
                self.current.reset()
            self.current = self.path[self.index]
            self.current.make_dynamic()
            self.index = (self.index + 1) % len(self.path)