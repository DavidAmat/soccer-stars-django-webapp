import numpy as np


class FormationProducer:

    def __init__(self, width, height, cap_radii=1, cap_mass=1, ball_radii=0.5, ball_mass=0.5):
        self.width = width
        self.height = height
        self.cap_radii = cap_radii
        self.cap_mass = cap_mass
        self.ball_radii = ball_radii
        self.ball_mass = ball_mass
        self.reference_width = 29
        self.reference_height = 17

    def get_formations(self, formation_name, cap_radii=1, cap_mass=1, n=5):
        if n == 5:
            formations_5 = {
                "formation1": {
                    "positions": [
                        (1, 8.5),  # goalkeeper
                        (4.5, 4),
                        (4.5, 13),  # defenders
                        (7.8, 8.5),  # midfielder
                        (11, 8.5),  # striker
                    ],
                    "radii": [cap_radii] * n,
                    "masses": [cap_mass] * n,
                },
                "formation2": {
                    "positions": [
                        (2, 6),
                        (2, 11),  # goalkeepers
                        (6, 8.5),  # midfielder
                        (11, 3),
                        (11, 14),  # strikers
                    ],
                    "radii": [cap_radii] * n,
                    "masses": [cap_mass] * n,
                },
            }
            return formations_5.get(formation_name, {})

    def get_debug_formation(self, debug_version):
        if debug_version == "debug_v1":
            return np.array(
                [
                    [66.20689392, 540.0],
                    [416.8189679, 143.16512266],
                    [297.93103027, 825.88232422],
                    [1176.90280353, 75.57212601],
                    [1834.55503557, 82.12137688],
                    [1356.06420811, 136.25778259],
                    [1928.81678107, 497.30319019],
                    [1603.35612785, 475.25641742],
                    [1433.24008953, 303.85371106],
                    [633.17534266, 374.4646326],
                    [2017.43184618, 449.08918782],
                ]
            )
        return None

    def scale_formation(self, formation_name):
        formation = self.get_formations(formation_name, cap_radii=self.cap_radii, cap_mass=self.cap_mass)
        positions = formation["positions"]
        radii = formation["radii"]
        masses = formation["masses"]

        scaled_positions = [
            (x / self.reference_width * self.width, y / self.reference_height * self.height) for x, y in positions
        ]

        scaled_radii = [r / self.reference_width * self.width for r in radii]

        return (
            np.array(scaled_positions, dtype=np.float32),
            np.array(scaled_radii, dtype=np.float32),
            np.array(masses, dtype=np.float32),
        )

    def scale_ball(self):
        ball_position = np.array([self.width / 2, self.height / 2])
        ball_radii = self.ball_radii / self.reference_width * self.width
        ball_mass = self.ball_mass
        return (
            np.array(ball_position, dtype=np.float32),
            np.array(ball_radii, dtype=np.float32),
            np.array(ball_mass, dtype=np.float32),
        )

    def setup_match_formation(self, left_formation_name, right_formation_name, debug_formation=None):
        left_positions, left_radii, left_masses = self.scale_formation(left_formation_name)
        right_positions, right_radii, right_masses = self.scale_formation(right_formation_name)

        # Mirror the right team's formation
        right_positions[:, 0] = self.width - right_positions[:, 0]

        # Create the ball
        ball_position, ball_radii, ball_mass = self.scale_ball()

        # Combine positions and radii
        all_positions = np.vstack((left_positions, right_positions, ball_position))
        all_radii = np.hstack((left_radii, right_radii, ball_radii))
        all_masses = np.hstack((left_masses, right_masses, ball_mass))

        # Create team mapping
        # team_mapping = {i: 'left' for i in range(len(left_positions))}
        # team_mapping.update({i + len(left_positions): 'right' for i in range(len(right_positions))})
        # Create team mapping like {"left": [0, 1, 2, 3, 4], "right": [5, 6, 7, 8, 9]}
        team_mapping = {
            "left": list(range(len(left_positions))),
            "right": list(range(len(left_positions), len(left_positions) + len(right_positions))),
            "ball": len(all_positions) - 1,
        }

        # If debug is enabled, make the positions array be the one provided as input
        if debug_formation:
            positions_debug = self.get_debug_formation(debug_version=debug_formation)
            if positions_debug is not None:
                all_positions = positions_debug

        return all_positions, all_radii, all_masses, team_mapping


# Example usage and testing
if __name__ == "__main__":
    from match_logic import utils

    width = 1920  # new field width
    height = 1080  # new field height
    formation_name = "formation1"
    left_formation_name = "formation1"
    right_formation_name = "formation2"

    # Single formation
    scaler = FormationProducer(width, height)
    X, R, M = scaler.scale_formation(formation_name)

    # Match formation
    scaler = FormationProducer(width, height)
    X, R, M, team_mapping = scaler.setup_match_formation(left_formation_name, right_formation_name)

    # Get the coordinates of a team
    X_team = X[team_mapping["right"]]

    # Render formation
    ur = utils.UtilsRender()
    ur.render_snapshot(position=X, radius=R)
