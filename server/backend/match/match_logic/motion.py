import numpy as np
from match.match_logic.collision_resolver import CollisionResolver
import time
from typing import List


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
        latency_ms = int(np.round(latency, 3) * 1000)
        return positions, velocities, latency_ms

    def simulate_field_motion(self, X, V, max_iterations=5000, friction_interval=50, truncate_motion_to_step=None):
        positions = [X.copy()]
        velocities = [V.copy()]
        if truncate_motion_to_step is not None:
            max_iterations = truncate_motion_to_step

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
        latency_ms = int(np.round(latency, 3) * 1000)
        return positions, velocities, latency_ms

    # ------------------------------------------------- #
    #                Move Cap Outside Goal              #
    # ------------------------------------------------- #
    def simulate_cap_moving_from_goal(self, X: np.ndarray, R: np.ndarray) -> List[np.ndarray]:
        """
        Creates a trajectory for the caps to move from the goal to the field, basically starting
        from the current X position of the caps where they are inside the goal aand moving them to the field
        as a linear movement. It returns a list of X positions for each timestep.

        Parameters:
        - X: np.ndarray of shape (n, 2) with the current positions of the caps
        - R: np.ndarray of shape (n,) with the radii of the caps

        Returns:
        - Xs: np.ndarray of shape (timesteps, n, 2) with the positions of the caps at each timestep
        """

        # First call move_cap_from_goal to get the new position of the caps
        X_new = self.move_cap_from_goal(X, R)

        # Overwrite the last row (the ball will not be moved by this logic)
        X_new[-1] = X[-1]

        # Given X and X_new, create an interpolation trajectory (simple, just linear)
        # to create the motion of the caps moving from the X to X_new
        timesteps = 100
        Xs = []
        for t in range(timesteps + 1):
            x_t = X + (X_new - X) * t / timesteps
            Xs.append(x_t)
        return Xs

    def move_cap_from_goal(self, X: np.ndarray, R: np.ndarray) -> np.ndarray:
        """
        To avoid having caps inside the goal, hence blocking completely
        the changes to have a space to core, we need to move them outside
        every time the movement finishes and the last position of the caps
        we see a center of the cap inside the goal.

        In order to decide where to move the cap, we need to check that a given
        perimiter is not occupied by another cap. If it is, we need to move the cap
        either further or either in a different angle to avoid collision.
        """
        # Check which of the caps x coordinate is less than xfield_left
        mask_caps_inside_left_goal = X[:, 0] < self.cr.gc.xfield_left
        mask_caps_inside_right_goal = X[:, 0] > self.cr.gc.xfield_right
        d_masks = {
            "left": mask_caps_inside_left_goal,
            "right": mask_caps_inside_right_goal,
        }

        # Overwrite the final position of the cap in the X matrix
        X_final = X.copy()

        # ------------------------------- #
        #        Left Goal                #
        # ------------------------------- #
        for side, mask in d_masks.items():
            # Check if the side is left or right
            if side == "left":
                is_left_goal = True
            else:
                is_left_goal = False

            # Remove caps outside the LEFT/RIGHT goal (depending on the iteration)
            for cap_idx_in_goal in np.where(mask)[0]:
                x_cap_inside_goal, y_cap_inside_goal = X_final[cap_idx_in_goal]

                # Get the displacements factors allowed to avoid collisions
                X_test = X_final.copy()
                kx, ky = self.select_kx_ky(
                    X_test=X_test,
                    cap_idx_in_goal=cap_idx_in_goal,
                    x_cap_inside_goal=x_cap_inside_goal,
                    y_cap_inside_goal=y_cap_inside_goal,
                    r=R[cap_idx_in_goal],
                    is_left_goal=is_left_goal,
                )

                # Displace the cap outside the goal Kx times the radii on the x axis
                # and Ky times the radii on the y axis
                X_final[cap_idx_in_goal] = self.remove_cap_inside_goal(
                    x=x_cap_inside_goal,
                    y=y_cap_inside_goal,
                    r=R[cap_idx_in_goal],
                    kx=kx,
                    ky=ky,
                    is_left_goal=is_left_goal,
                )
        return X_final

    def remove_cap_inside_goal(self, x, y, r, kx, ky, is_left_goal=True):
        """
        Check the angle of the y_cap_inside_goal. We should map:
        If the y_cap_inside_goal = ynet_top_lateral, angle = 70
        If the y_cap_inside_goal = ynet_bottom_lateral, angle = -70
        If the y_cap_inside_goal = y_mid_field, angle = 0
        Now we will displace the cap outside the goal (for left net we will add, for right net we will subtract on the x component)
        and we will displace the cap on the x axis by K * radii on the x axis and tan(angle) * radii on the y axis

        Since the displacement depends on which of the two goals we are moving the cap from, we need to check
        if is_left_goal is True or False to decide if we add or subtract the displacement on the x axis.
        """
        y_departure_scale = (y - self.cr.gc.y_mid_field) / (self.cr.gc.ynet_top_lateral - self.cr.gc.y_mid_field)
        angle = 70 * y_departure_scale
        if is_left_goal:
            # LEFT GOAL
            return x + kx * r, y - ky * r * np.tan(np.radians(angle))
        else:
            # RIGHT GOAL
            return x - kx * r, y - ky * r * np.tan(np.radians(angle))

    def select_kx_ky(self, X_test, cap_idx_in_goal, x_cap_inside_goal, y_cap_inside_goal, r, is_left_goal=True):
        """
        When there is a collision after trying to displace a cap inside a goal to the outisde,
        we need to displace the cap outside the goal into an available position. This function
        iterates over the kx and ky arguments until it finds a valid position.
        kx is the displacement on the x axis, how many times we multiply the radii to make the displacement horizontal
        ky is the displacement on the y axis, how many times we multiply the radii to make the displacement vertical

        In case we find a valid position with the initial kx and ky we return those params
        In case we don't find a valid position, we will loop for the kx, ky argument on a grid search manner until
        we find any combination that allows moving that cap.

        It overwrite the X_test matrix with the new position of the cap after having moved it outside the goal
        to check if that position is valid. This is why X_test should be a copy of the X matrix but not the same object.

        is_left_goal is a boolean that indicates if we are moving the cap from the left goal or the right goal.
        """
        kx = 4
        ky = 4
        # Displace the cap outside the goal
        X_test[cap_idx_in_goal] = self.remove_cap_inside_goal(
            x=x_cap_inside_goal, y=y_cap_inside_goal, r=r, kx=kx, ky=ky, is_left_goal=is_left_goal
        )

        # Check if the updated position collides with any other cap
        check_collision_after_displacement = self.check_if_cap_is_in_colliding(X_test, cap_idx_in_goal)

        # Create a for loop modifying  the kx argument until we find a valid position
        # In case we don't find a valid position, we will loop for the ky argument
        l_cap_collisions = self.cr.get_cap_collisions(X_test)
        if len(l_cap_collisions) < 1:
            return kx, ky

        # If there are collisions
        it_num = 0
        max_iterations = 100
        while check_collision_after_displacement and it_num < max_iterations:
            it_num += 1
            for kx in [3.5, 4, 4.5, 5, 5.5, 1.5, 2.5, 3]:
                X_test[cap_idx_in_goal] = self.remove_cap_inside_goal(
                    x=x_cap_inside_goal, y=y_cap_inside_goal, r=r, kx=kx, ky=ky, is_left_goal=is_left_goal
                )
                check_collision_after_displacement = self.check_if_cap_is_in_colliding(X_test, cap_idx_in_goal)
                if not check_collision_after_displacement:
                    break
            # When we leave the for loop, we check if we found a valid position
            # otherwise we trigger another grid search with a different factory ky
            if not check_collision_after_displacement:
                break
            else:
                ky += 0.25
        return kx, ky

    def check_if_cap_is_in_colliding(self, X, cap_idx):
        # Get the tuples of cap collisions
        cap_collisions = self.cr.get_cap_collisions(X)

        # Convert the list of tuples into a single list
        l_cap_collisions = [cap for cap_tuple in cap_collisions for cap in cap_tuple]

        # Check if the cap is in l_cap_collisions
        return cap_idx in l_cap_collisions


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
    cap_radii = 1.0
    cap_mass = 1
    ratio_radii_cap_h = cap_radii / 17

    # This is the radii for current field in pixels (not in cm)
    radii = int(h * ratio_radii_cap_h)
    goal_size = int(radii * 6)
    goal_depth = int(radii * 2)
    ur = utils.UtilsRender(window_size=boundaries, goal_depth=goal_depth, goal_size=goal_size)

    # Match formation
    formation_producer = FormationProducer(w, h, cap_radii=cap_radii, cap_mass=1)
    X, R, M, team_mapping = formation_producer.setup_match_formation("formation1", "formation1")

    # Create a Motion object
    motion = Motion(R=R, M=M, min_velocity=0.1, boundaries=boundaries, goal_size=goal_size, goal_depth=goal_depth)

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
