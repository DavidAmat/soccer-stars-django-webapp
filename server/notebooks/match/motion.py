import numpy as np
from collision_resolver import CollisionResolver

class Motion:
    def __init__(self, X, R, M, min_velocity=0.1, boundaries=(1920, 1080)):
        self.boundaries = boundaries  # boundaries should be a tuple (width, height)
        self.w, self.h = boundaries
        self.X = X
        self.R = R
        self.M = M
        self.n = X.shape[0]  # Number of caps
        self.min_velocity = min_velocity
        
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
    
    def main(self, V):
        # Check if system is moving
        self.V = V
        system_moving = self.is_system_moving(V)
        if not system_moving:
            return self.X, self.V
         
        # Duplicate V and X matrix for iterate over them
        V = self.V.copy()
        X = self.X.copy()
            
        # Get the system evolve through the motion dynamics till the system stops moving
        while system_moving:

            # Calculate the next position X(t+1) = X(t) + V(t)
            X_next = X + V

            # Check if collision in the X_next occurs

            # Update cap position after handling potential collisions
            X = X_next
            print("--------------------")
            print("Current Velocity:", V)
            # Calculate new velocity
            V = self.next_velocity(V)
            print("New Velocity:", V)
            print("--------------------")
        return X, V
    
if __name__ == "__main__":
    X = np.array([[1, 1], [2, 2], [3, 3]])
    R = np.array([1, 1, 1])
    M = np.array([1, 1, 1])
    V = np.array([[1, 1], [1, 1], [1, 1]])
    motion = Motion(X, R, M, V)
    X, V = motion.main()