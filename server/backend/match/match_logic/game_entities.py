# game_entities.py
import numpy as np
import math
import dataclasses

# Create a dataclass with Arrow properties
# cap_index, arrow_length, angle, min_velocity = 0.1, cap_radius = 63, max_velocity=10, max_arrow_distance=200


@dataclasses.dataclass
class ArrowProperties:
    cap_index: int
    arrow_length: float
    angle: float
    min_velocity: float = 0.1
    cap_radius: int = 63
    max_velocity: int = 10
    max_arrow_distance: int = 200


class Arrow:
    def __init__(self, arrow_props: ArrowProperties):
        self.arrow_props = arrow_props

        # Arrow angle and direction
        self.angle_rad = np.radians(arrow_props.angle)
        self.direction = np.array([math.cos(self.angle_rad), -math.sin(self.angle_rad)])

        # Get velocity in both modulus and vectorial form
        self.mod_initial_velocity = self.map_arrow_length_to_mod_initial_velocity()
        self.initial_velocity = np.array(self.mod_initial_velocity * self.direction)

    def map_arrow_length_to_mod_initial_velocity(self):
        """
        Get the modulus of the initial velocity of the arrow
        """
        arrow_props = self.arrow_props
        # ------------------------------------------------- #
        #  Normalization Ratio
        # ------------------------------------------------- #
        # Difference betweeen arrow length and cap radius
        assert arrow_props.arrow_length >= arrow_props.cap_radius, "Arrow length must be greater than cap radius"
        diff_arrow_cap = arrow_props.arrow_length - arrow_props.cap_radius

        # Maximum allowed difference for diff_arrow_cap
        max_diff_arrow_cap = arrow_props.max_arrow_distance - arrow_props.cap_radius

        # Ratio of the difference to the maximum allowed difference
        diff_ratio = diff_arrow_cap / max_diff_arrow_cap

        # ------------------------------------------------- #
        #  New velocity range
        # ------------------------------------------------- #
        # Range of initial velocities that the arrow translates to (from arrow_length in px to velocity in px/t)
        range_velocities_px_t = arrow_props.max_velocity - arrow_props.min_velocity

        # Linear mapping of the arrow_length to the velocity
        return diff_ratio * range_velocities_px_t + arrow_props.min_velocity


if __name__ == "__main__":
    # Instantiate ArrowProperties
    arrow_props = ArrowProperties(cap_index=0, arrow_length=70, angle=45)
    arrow = Arrow(arrow_props)

    # Get the velocity in px/t
    print(arrow.mod_initial_velocity)
    print(arrow.initial_velocity)
