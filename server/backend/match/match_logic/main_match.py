import numpy as np
from match.match_logic import game_entities, formations, motion


class Match:
    def __init__(
        self,
        width=1920,
        height=1080,
        cap_radii=1.0,
        cap_mass=1.0,
        goal_size=None,
        goal_depth=None,
        ball_mass=0.5,
        ball_radii=0.5,
    ):
        self.width = width
        self.height = height
        self.cap_radii_px = cap_radii * 63
        self.cap_radii = cap_radii
        self.cap_mass = cap_mass
        self.ball_mass = ball_mass
        self.ball_radii = ball_radii
        self.boundaries = (width, height)
        self.goal_size = goal_size if goal_size else int(self.cap_radii_px * 6)
        self.goal_depth = goal_depth if goal_depth else int(self.cap_radii_px * 2)

        self.X = None
        self.R = None
        self.M = None
        self.team_mapping = None
        self.motion: motion.Motion = None

    # ----------------------------------------------------------------- #
    #                  Main Function: create_formation                  #
    # ----------------------------------------------------------------- #
    def initial_setup(self, left_formation, right_formation, debug_formation=None):
        """
        Provides the namings for the formations and the debug formation in case
        we want to start the match in a given formation providing the 2D arrays
        manually in the formations debug section.
        """
        formation_producer = formations.FormationProducer(
            width=self.width,
            height=self.height,
            cap_radii=self.cap_radii,
            cap_mass=self.cap_mass,
            ball_mass=self.ball_mass,
            ball_radii=self.ball_radii,
        )
        self.X, self.R, self.M, self.team_mapping = formation_producer.setup_match_formation(
            left_formation, right_formation, debug_formation=debug_formation
        )
        self.motion = motion.Motion(
            R=self.R,
            M=self.M,
            min_velocity=0.1,
            boundaries=self.boundaries,
            goal_size=self.goal_size,
            goal_depth=self.goal_depth,
        )
        return self.X

    # ----------------------------------------------------------------- #
    #                  Main Function: submit_arrow                      #
    # ----------------------------------------------------------------- #
    def move_cap(self, cap_idx, arrow_power, angle, X_last, truncate_motion_to_step=None):
        """
        Main function callend in the MatchConsumer in consumers.py
        """
        if self.X is None or self.R is None or self.M is None or self.team_mapping is None:
            raise ValueError("Initial setup has not been performed.")

        arrow_props = game_entities.ArrowProperties(cap_index=cap_idx, arrow_length=arrow_power, angle=angle)
        arrow = game_entities.Arrow(arrow_props)

        # Initialize velocities
        V = np.zeros_like(X_last)
        V[cap_idx] = arrow.initial_velocity

        # Simulate motion (assuming `simulate_motion` is a method in the `Motion` class)
        X_hist, _, _ = self.motion.simulate_field_motion(X=X_last, V=V, truncate_motion_to_step=truncate_motion_to_step)

        # --------------------------------------- #
        # Remove caps from inside the goal
        # --------------------------------------- #
        # If the cap center is inside the goal, remove it
        # making a trajectory from the last position to the outside of the goal
        # X_move_outside_goal is a (timesteps, n, 2) array
        X_move_outside_goal = self.motion.simulate_cap_moving_from_goal(X=X_hist[-1], R=self.R)

        # Integrate the trajectory to the X_hist
        X_hist.extend(X_move_outside_goal)

        return X_hist  # Return the list of X positions of the system at each timestep

    @staticmethod
    def adjust_coordinates(positions, scale_factor=(1, 1), margin=(0, 0)):
        scale_factor_x, scale_factor_y = scale_factor
        margin_x, margin_y = margin
        adjusted_positions = []
        for position in positions:
            x, y = position
            new_x = x * scale_factor_x + margin_x
            new_y = y * scale_factor_y + margin_y
            adjusted_positions.append([new_x, new_y])
        return adjusted_positions


# Example usage
if __name__ == "__main__":
    match = Match()
    X_i = match.initial_setup("formation1", "formation2")

    cap_idx = 4
    arrow_power = 190
    angle = 15

    X_hist = match.move_cap(cap_idx, arrow_power, angle, X_last=X_i)
    print(len(X_hist))
