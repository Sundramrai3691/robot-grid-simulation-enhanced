"""
Input handling utilities
"""

import pygame
import tkinter as tk
from tkinter import simpledialog
from config.settings import WINDOW_WIDTH, WIDTH

def get_text_input(prompt, title="Input"):
    """Get text input from user using tkinter dialog"""
    pygame.display.iconify()  # Minimize pygame window
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    user_input = simpledialog.askstring(title, prompt)
    root.destroy()  # Destroy the tkinter window
    pygame.display.set_mode((WINDOW_WIDTH, WIDTH))  # Restore the pygame window
    return user_input