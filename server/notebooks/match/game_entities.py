# game_entities.py
import numpy as np
import math

class Cap:
    def __init__(self, index, position):
        self.radius = 20
        self.index = index
        self.position = np.array(position)

class CapFactory:
    def __init__(self, X: np.ndarray):
        """
        Args:
            X (np.ndarray): Array of shape (n, 2) where n is the number of caps
        Example:
        X = np.array(
            [[  30,  540],
            [1280,  540]]
        )
        """
        self.X = X
        self.caps = [Cap(index=i, position=[x, y]) for i, (x, y) in enumerate(X)]

    def get_x_mat(self):
        l_x = []
        for cap in self.caps:
            l_x.append(cap.position)
        return np.array(l_x)
    
class Arrow:
    def __init__(self, caps: CapFactory, cap_index, arrow_length, angle):
        self.caps = caps

        # Get the index of the cap
        self.cap_index = cap_index
        self.arrow_length = arrow_length
        self.angle = angle

        # Constants
        self.min_velocity = 0.1
        self.max_velocity = 10
        self.max_arrow_distance = 200

        # Get the cap and the angle of the arrow
        self.cap = self.caps.caps[self.cap_index]
        self.angle_rad = np.radians(angle)
        self.direction = np.array([math.cos(self.angle_rad), -math.sin(self.angle_rad)])

        # Get velocity in both modulus and vectorial form
        self.mod_initial_velocity = self.map_arrow_length_to_mod_initial_velocity()
        self.initial_velocity = self.mod_initial_velocity * self.direction
        

    def map_arrow_length_to_mod_initial_velocity(self):
        """
        Get the modulus of the initial velocity of the arrow
        """
        # Range of distances that the arrow can take in the game
        old_min = self.cap.radius
        old_max = self.max_arrow_distance

        # Range of initial velocities that the arrow translates to (from arrow_length in px to velocity in px/t)
        new_min = self.min_velocity
        new_max = self.max_velocity
        value = self.arrow_length

        # Linear mapping of the arrow_length to the velocity
        return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
