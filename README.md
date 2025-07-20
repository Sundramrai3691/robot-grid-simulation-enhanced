# Robot Grid Simulator

A grid-based simulator for robot pathfinding in a dynamic, urban-style environment using A* algorithm.

## Features

- Realistic map with static and dynamic obstacles
- Smart robot with path planning and re-planning
- Traffic light logic with red, yellow, and green states
- Trail effect for visualizing robot movement
- Support for saving and loading map layouts
- Adjustable simulation speed and grid control

## Controls

- Left Click: Set Start / End / Barrier / Traffic Light (when holding `T`)
- Right Click: Remove cell
- Space: Start simulation
- C: Clear grid
- R: Reset simulation
- S: Save map
- L: Load map
- I: Import image map (future feature)
- 1–4: Change robot speed
- T: Toggle traffic light tool

## Requirements

- Python 3.x
- pygame
- pillow

Install dependencies using:

```bash
pip install -r requirements.txt
