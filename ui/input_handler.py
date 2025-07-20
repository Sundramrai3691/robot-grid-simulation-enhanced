"""
Input handling utilities
"""

import pygame
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
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

def get_file_path(title="Select File", filetypes=[("JSON files", "*.json"), ("All files", "*.*")]):
    """Get file path from user using tkinter file dialog"""
    pygame.display.iconify()  # Minimize pygame window
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()  # Destroy the tkinter window
    pygame.display.set_mode((WINDOW_WIDTH, WIDTH))  # Restore the pygame window
    return file_path

def get_save_path(title="Save File", defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")]):
    """Get save file path from user using tkinter file dialog"""
    pygame.display.iconify()  # Minimize pygame window
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.asksaveasfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)
    root.destroy()  # Destroy the tkinter window
    pygame.display.set_mode((WINDOW_WIDTH, WIDTH))  # Restore the pygame window
    return file_path

def show_message(title, message, msg_type="info"):
    """Show message dialog to user"""
    pygame.display.iconify()  # Minimize pygame window
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    
    if msg_type == "info":
        messagebox.showinfo(title, message)
    elif msg_type == "warning":
        messagebox.showwarning(title, message)
    elif msg_type == "error":
        messagebox.showerror(title, message)
    
    root.destroy()  # Destroy the tkinter window
    pygame.display.set_mode((WINDOW_WIDTH, WIDTH))  # Restore the pygame window

def get_numeric_input(prompt, title="Input", min_val=None, max_val=None):
    """Get numeric input from user with validation"""
    while True:
        user_input = get_text_input(prompt, title)
        if user_input is None:  # User cancelled
            return None
        
        try:
            value = float(user_input)
            if min_val is not None and value < min_val:
                show_message("Invalid Input", f"Value must be at least {min_val}", "warning")
                continue
            if max_val is not None and value > max_val:
                show_message("Invalid Input", f"Value must be at most {max_val}", "warning")
                continue
            return value
        except ValueError:
            show_message("Invalid Input", "Please enter a valid number", "warning")

def handle_mouse_click(pos, grid, width, rows, start, targets, robot_params, modes):
    """Handle mouse click events based on current mode"""
    if pos[0] >= width:  # Click outside grid area
        return start, targets
    
    row, col = get_clicked_pos(pos, rows, width)
    if not (0 <= row < rows and 0 <= col < rows):
        return start, targets
    
    spot = grid[row][col]
    
    # Handle different modes
    if modes.get('target_mode', False):
        if not spot.is_start() and not spot.is_barrier():
            priority = modes.get('target_priority', 1)
            spot.make_target(priority)
            targets.append(spot)
    elif modes.get('traffic_light_tool', False):
        if not spot.is_start() and not spot.is_end():
            spot.make_traffic_light()
    elif modes.get('barrier_mode', False):
        if not spot.is_start() and not spot.is_end():
            spot.make_barrier()
    elif modes.get('dynamic_mode', False):
        if not spot.is_start() and not spot.is_end():
            spot.make_dynamic()
    elif not start and not spot.is_barrier() and not spot.is_end():
        start = spot
        start.make_start()
    elif spot != start and not spot.is_end():
        spot.make_barrier()
    
    return start, targets

def handle_right_click(pos, grid, width, rows, start, targets):
    """Handle right mouse click to remove objects"""
    if pos[0] >= width:  # Click outside grid area
        return start, targets
    
    row, col = get_clicked_pos(pos, rows, width)
    if not (0 <= row < rows and 0 <= col < rows):
        return start, targets
    
    spot = grid[row][col]
    
    if spot == start:
        start = None
    elif spot in targets:
        targets.remove(spot)
    
    spot.reset()
    if hasattr(spot, 'is_traffic_stop'):
        spot.is_traffic_stop = False
    
    return start, targets

def get_clicked_pos(pos, rows, width):
    """Get the grid position from mouse click coordinates"""
    gap = width // rows
    y, x = pos
    return y // gap, x // gap