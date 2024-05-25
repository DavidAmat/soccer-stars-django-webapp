import numpy as np

class FormationProducer:
    
    
    
    def __init__(self, width, height, cap_radii=1):
        self.width = width
        self.height = height
        self.cap_radii = cap_radii
        self.reference_width = 29
        self.reference_height = 17

    def get_formations(self, formation_name, radii=1, n=5):
        if n == 5:
            formations_5 = {
                "formation1": {
                    "positions": [
                        (1, 8.5),  # goalkeeper
                        (4.5, 4), (4.5, 13),  # defenders
                        (7.8, 8.5),  # midfielder
                        (11, 8.5)  # striker
                    ],
                    "radii": [radii] * n
                },
                "formation2": {
                    "positions": [
                        (2, 6), (2, 11),  # goalkeepers
                        (6, 8.5),  # midfielder
                        (11, 3), (11, 14)  # strikers
                    ],
                    "radii": [radii] * n
                }
            }
            return formations_5.get(formation_name, {})
        
    def scale_formation(self, formation_name):
        if formation_name not in self.formations:
            raise ValueError(f"Formation {formation_name} not found.")
        
        formation = self.formations[formation_name]
        positions = formation["positions"]
        radii = formation["radii"]
        
        scaled_positions = [
            (x / self.reference_width * self.width, y / self.reference_height * self.height)
            for x, y in positions
        ]
        
        scaled_radii = [r / self.reference_width * self.width for r in radii]
        
        return np.array(scaled_positions, dtype=np.float32), np.array(scaled_radii, dtype=np.float32)
    
    def setup_match_formation(self, left_formation_name, right_formation_name):
        left_positions, left_radii = self.scale_formation(left_formation_name)
        right_positions, right_radii = self.scale_formation(right_formation_name)

        # Mirror the right team's formation
        right_positions[:, 0] = self.width - right_positions[:, 0]
        
        # Combine positions and radii
        all_positions = np.vstack((left_positions, right_positions))
        all_radii = np.hstack((left_radii, right_radii))
        
        # Create team mapping
        #team_mapping = {i: 'left' for i in range(len(left_positions))}
        #team_mapping.update({i + len(left_positions): 'right' for i in range(len(right_positions))})
        # Create team mapping like {"left": [0, 1, 2, 3, 4], "right": [5, 6, 7, 8, 9]}
        team_mapping = {
            "left": list(range(len(left_positions))), 
            "right": list(range(len(left_positions), len(all_positions)))}
        
        return all_positions, all_radii, team_mapping

# Example usage and testing
if __name__ == "__main__":
    from match import utils

    width = 1920  # new field width
    height = 1080  # new field height
    formation_name = "formation1"
    left_formation_name = "formation1"
    right_formation_name = "formation2"
    
    # Single formation
    scaler = FormationProducer(width, height)
    X, R = scaler.scale_formation(formation_name)
    
    # Match formation
    scaler = FormationProducer(width, height)
    X, R, team_mapping = scaler.setup_match_formation(left_formation_name, right_formation_name)

    # Get the coordinates of a team
    X_team = X[team_mapping["right"]]

    # Render formation
    ur = utils.UtilsRender()
    ur.render_snapshot(position=X, radius=R)