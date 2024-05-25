import numpy as np
from match_logic import game_entities, formations, motion

class Match:
    def __init__(self, width=1920, height=1080, cap_radii=1.0, cap_mass=1.0, goal_size=None, goal_depth=None, ball_mass=0.5, ball_radii=0.5):
        self.width = width
        self.height = height
        self.cap_radii = cap_radii
        self.cap_mass = cap_mass
        self.ball_mass = ball_mass
        self.ball_radii = ball_radii
        self.boundaries = (width, height)
        self.goal_size = goal_size if goal_size else int(cap_radii * 6)
        self.goal_depth = goal_depth if goal_depth else int(cap_radii * 2)

        self.X = None
        self.R = None
        self.M = None
        self.team_mapping = None
        self.motion: motion.Motion = None

    def initial_setup(self, left_formation, right_formation):
        formation_producer = formations.FormationProducer(
            width=self.width, 
            height=self.height, 
            cap_radii=self.cap_radii, 
            cap_mass=self.cap_mass,
            ball_mass=self.ball_mass,
            ball_radii=self.ball_radii
        )
        self.X, self.R, self.M, self.team_mapping = formation_producer.setup_match_formation(
            left_formation, right_formation
        )
        self.motion = motion.Motion(
            R=self.R,
            M=self.M,
            min_velocity=0.1,
            boundaries=self.boundaries,
            goal_size=self.goal_size,
            goal_depth=self.goal_depth
        ) 
        return self.X

    def move_cap(self, cap_idx, arrow_power, angle, X_last):
        if self.X is None or self.R is None or self.M is None or self.team_mapping is None:
            raise ValueError("Initial setup has not been performed.")

        arrow_props = game_entities.ArrowProperties(cap_index=cap_idx, arrow_length=arrow_power, angle=angle)
        arrow = game_entities.Arrow(arrow_props)

        # Initialize velocities
        V = np.zeros_like(X_last)
        V[cap_idx] = arrow.initial_velocity

        # Simulate motion (assuming `simulate_motion` is a method in the `Motion` class)
        X_hist, _, _ = self.motion.simulate_field_motion(X=X_last, V=V)

        return X_hist  # Return the list of X positions of the system at each timestep

# Example usage
if __name__ == "__main__":
    match = Match()
    X_i = match.initial_setup("formation1", "formation2")

    cap_idx = 4
    arrow_power = 190
    angle = 15

    X_hist = match.move_cap(cap_idx, arrow_power, angle, X_last=X_i)
    print(len(X_hist))
