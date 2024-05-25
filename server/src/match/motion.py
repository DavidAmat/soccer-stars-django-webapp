import numpy as np
from match.collision_resolver import CollisionResolver
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
                print(f"System stopped at iteration {iteration}")
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
                print(f"System stopped at iteration {iteration}")
                break
            iteration += 1
        end_time = time.time()
        latency = end_time - start_time
        latency_ms = int(np.round(latency,3)*1000)
        return positions, velocities, latency_ms
    
if __name__ == "__main__":
    X = np.array([[1, 1], [2, 2], [3, 3]])
    R = np.array([1, 1, 1])
    M = np.array([1, 1, 1])
    V = np.array([[1, 1], [1, 1], [1, 1]])
    motion = Motion(X, R, M, V)
    X, V = motion.main()