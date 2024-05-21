import numpy as np
from collision_resolver import CollisionResolver

class Motion:
    def __init__(self, R, M, min_velocity=0.1, boundaries=(1920, 1080)):
        self.boundaries = boundaries  # boundaries should be a tuple (width, height)
        self.w, self.h = boundaries
        self.R = R
        self.M = M
        self.n = len(M)
        self.min_velocity = min_velocity
        self.cr = CollisionResolver(R=R, M=M, boundaries=boundaries)
        
    def get_cap_velocity_modulus(self, V):
        """
        Get the velocity modulus of the cap
        Returns a matrix of shape (n, 1)
        """
        return np.linalg.norm(V, axis=1)

    def is_system_moving(self, V):
        """
        Check if norm of V matrix is >= min_velocity
        """
        caps_mod_velocity = self.get_cap_velocity_modulus(V)
        return np.all(caps_mod_velocity < self.min_velocity)
    
    def run_motion(self, X, V):
        positions = [X]
        velocities = [V]
        t = 0
        cr = self.cr

        # Check if system is moving
        system_moving = self.is_system_moving(V)
        if not system_moving:
            return positions, velocities

        # Use copies of inputs to iterate positions and velocities over timesteps
        X_t = X.copy()
        V_t = V.copy()
        
        # Get the system evolve through the motion dynamics till the system stops moving
        while system_moving:
            # Update timestep
            t += 1

            # Resolve collisions: get V(t+1) and X(t+1)
            V_t_1 = cr.resolve_collision(X=X_t, V=V_t)

            # Apply friction to the system
            

            X_t_1 = X_t + V_t_1

            # Check if collision in the X_next occurs
            positions.append(X_t_1)
            velocities.append(V_t_1)

        return X, V
    
if __name__ == "__main__":
    X = np.array([[1, 1], [2, 2], [3, 3]])
    R = np.array([1, 1, 1])
    M = np.array([1, 1, 1])
    V = np.array([[1, 1], [1, 1], [1, 1]])
    motion = Motion(X, R, M, V)
    X, V = motion.main()