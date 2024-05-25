import numpy as np
from match.match_logic.collision_resolver import CollisionResolver
import time


class Motion:
    def __init__(self, R, M, min_velocity=0.1, boundaries=(1920, 1080), goal_size=None, goal_depth=None):
        self.boundaries = boundaries  # boundaries should be a tuple (width, height)
        self.w, self.h = boundaries
        self.R = R
        self.M = M
        self.n = len(M)
        self.min_velocity = min_velocity
        self.cr = CollisionResolver(R=R, M=M, boundaries=boundaries, goal_depth=goal_depth, goal_size=goal_size)

    @staticmethod
    def apply_smooth_friction(V: np.array, velocity_threshold=0.25):
        scale_1 = 1.1
        scale_2 = 1.3
        scale_3 = 1.2
        scale_4 = 1.5

        # Compute the speed (modulus) for each cap
        speeds = np.linalg.norm(V, axis=1)
        
        # Create masks for each scale based on the speed
        mask_1 = speeds > 5
        mask_2 = np.logical_and(speeds > 3, speeds <= 5)
        mask_3 = np.logical_and(speeds > 2, speeds <= 3)
        mask_4 = np.logical_and(speeds > velocity_threshold, speeds <= 2)
        mask_stop = speeds <= velocity_threshold

        # Initialize new velocity matrix
        V_new = V.copy()

        # Apply scales to speeds and update velocities accordingly
        speeds_new = speeds.copy()
        speeds_new[mask_1] /= scale_1
        speeds_new[mask_2] /= scale_2
        speeds_new[mask_3] /= scale_3
        speeds_new[mask_4] /= scale_4
        speeds_new[mask_stop] = 0

        # Update V_new to reflect the new speeds while maintaining direction
        for i, v in enumerate(V):
            if speeds[i] > 0:  # Avoid division by zero
                V_new[i] = v / speeds[i] * speeds_new[i]

        return V_new
        
    def get_cap_velocity_modulus(self, V):
        """
        Get the velocity modulus of the cap
        Returns a matrix of shape (n, 1)
        """
        return np.linalg.norm(V, axis=1)

    def is_system_not_moving(self, V):
        """
        Check if norm of V matrix is >= min_velocity
        """
        caps_mod_velocity = self.get_cap_velocity_modulus(V)
        return np.all(caps_mod_velocity < self.min_velocity)
    
    def simulate_motion(self, X, V, max_iterations=5000, friction_interval=50):
        positions = [X.copy()]
        velocities = [V.copy()]

        iteration = 0
        start_time = time.time()
        while iteration < max_iterations:
            V_next = self.cr.resolve_collision(X=X, V=V)
            if iteration % friction_interval == 0:
                V_next = self.apply_smooth_friction(V=V_next)
            X_next = X + V_next
            positions.append(X_next.copy())
            velocities.append(V_next.copy())
            X = X_next
            V = V_next
            if self.is_system_not_moving(V_next):
                # print(f"System stopped at iteration {iteration}")
                break
            iteration += 1
        end_time = time.time()
        latency = end_time - start_time
        latency_ms = int(np.round(latency,3)*1000)
        return positions, velocities, latency_ms
    
    def simulate_field_motion(self, X, V, max_iterations=5000, friction_interval=50):
        positions = [X.copy()]
        velocities = [V.copy()]

        iteration = 0
        start_time = time.time()
        while iteration < max_iterations:
            V_next = self.cr.resolve_field_collision(X=X, V=V)
            if iteration % friction_interval == 0:
                V_next = self.apply_smooth_friction(V=V_next)
            X_next = X + V_next
            positions.append(X_next.copy())
            velocities.append(V_next.copy())
            X = X_next
            V = V_next
            if self.is_system_not_moving(V_next):
                # print(f"System stopped at iteration {iteration}")
                break
            iteration += 1
        end_time = time.time()
        latency = end_time - start_time
        latency_ms = int(np.round(latency,3)*1000)
        return positions, velocities, latency_ms
    
if __name__ == "__main__":
    from match_logic import utils, game_entities, collision_resolver, formations

    # Import classes
    ur = utils.UtilsRender()
    CollisionResolver = collision_resolver.CollisionResolver
    FormationProducer = formations.FormationProducer
    from game_entities import Arrow, ArrowProperties

    # Match params
    n = 1
    w = 1920
    h = 1080
    margin = 10
    boundaries = (w, h)

    # This is the standardized radii size (for the 29 cm x 17 cm field)
    cap_radii = 1.
    cap_mass = 1
    ratio_radii_cap_h = cap_radii/17

    # This is the radii for current field in pixels (not in cm)
    radii = int(h * ratio_radii_cap_h)
    goal_size = int(radii * 6)
    goal_depth = int(radii * 2)
    ur = utils.UtilsRender(window_size=boundaries, goal_depth=goal_depth, goal_size=goal_size)

    # Match formation
    formation_producer = FormationProducer(w, h, cap_radii=cap_radii, cap_mass=1)
    X, R, M, team_mapping = formation_producer.setup_match_formation("formation1", "formation1")

    # Create a Motion object
    motion = Motion(
        R=R,
        M=M,
        min_velocity=0.1,
        boundaries=boundaries,
        goal_size=goal_size,
        goal_depth=goal_depth
    )

    # ------------------------------------------------- #
    # History
    # ------------------------------------------------- #
    Xhist = []


    # ------------------------------------------------- #
    # Movement 1
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 4
    arrow_power = 190
    angle = 15
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs, Vs, latency = motion.simulate_field_motion(X=X, V=V)
    Xhist.extend(Xs)

    # ------------------------------------------------- #
    # Movement 2
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 5
    arrow_power = 190
    angle = 15
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs2, Vs2, latency2 = motion.simulate_field_motion(X=Xs[-1], V=V)
    Xhist.extend(Xs2)

    # ------------------------------------------------- #
    # Movement 3
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 4
    arrow_power = 190
    angle = 190
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs3, Vs3, latency3 = motion.simulate_field_motion(X=Xs2[-1], V=V)
    Xhist.extend(Xs3)

    # ------------------------------------------------- #
    # Movement 4
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 1
    arrow_power = 190
    angle = 185
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs4, Vs4, latency4 = motion.simulate_field_motion(X=Xs3[-1], V=V)
    Xhist.extend(Xs4)

    # ------------------------------------------------- #
    # Movement 5
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 4
    arrow_power = 190
    angle = 180
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs5, Vs5, latency5 = motion.simulate_field_motion(X=Xs4[-1], V=V)
    Xhist.extend(Xs5)

    # ------------------------------------------------- #
    # Movement 6
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 2
    arrow_power = 100
    angle = 230
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs6, Vs6, latency6 = motion.simulate_field_motion(X=Xs5[-1], V=V)
    Xhist.extend(Xs6)

    # ------------------------------------------------- #
    # Movement 7
    # ------------------------------------------------- #
    # Submit an Arrow with min length 63 and max length 200
    select_cap = 0
    arrow_power = 170
    angle = 190
    arrow_props = ArrowProperties(cap_index=select_cap, arrow_length=arrow_power, angle=angle)
    arrow = Arrow(arrow_props)
    
    # Move one cap
    V = np.zeros_like(X)
    V[select_cap] = arrow.initial_velocity
    print(V)

    # Simulate motion
    Xs7, Vs7, latency7 = motion.simulate_field_motion(X=Xs6[-1], V=V)
    Xhist.extend(Xs7)

    # ------------------------------------------------- #
    # See motion in all movements
    # ------------------------------------------------- #
    # Render the motion
    ur.render_field_motion(positions=Xhist, radius=R, add_delay=5)

