# main.py
from game_entities import Cap
from arrow import Arrow
from motion_resolver import MotionResolver

# Initialize game components
caps = [Cap(index=i, position=[x, y]) for i, (x, y) in enumerate([(30, 540), (1280, 540)])]
arrow = Arrow(cap_index=0, arrow_length=100, angle=0)
motion_resolver = MotionResolver(caps=caps, initial_velocity=2, min_velocity=0.1)

# Start the movement simulation for a selected cap
motion_resolver.start_movement(arrow.cap_index, arrow.direction)