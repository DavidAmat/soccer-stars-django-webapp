#%%
import numpy as np
# from collision_resolver import CollisionResolver
from config import cap_radius, w, h
from game_entities import Cap, CapFactory, Arrow

class MotionResolver:
    """
    When the Arrow length is submitted, one cap starts moving and then things will start to occur:
    - Either the cap collides with another one
    - Either the cap collides with the field edges
    - Either the cap stops moving due to friction
    - All of them ...
    """
    def __init__(self, caps: CapFactory, arrow: Arrow):
        self.caps = caps
        self.arrow = arrow
        self.min_velocity = arrow.min_velocity

        # Get matrix of positions and velocities
        self.X = caps.X
        self.V = np.zeros_like(self.X)

        # Get arrow and modify matrix of velocities
        self.V[self.arrow.cap_index] = self.arrow.initial_velocity

        # Instantiate collision resolver
        # self.collision_resolver = CollisionResolver(caps=caps, boundaries=(w, h))

        # Instantiate history of X and V
        self.X_history = [self.X]
        self.V_history = [self.V]
        self.t = 0

    def start_movement(self):
        # Get the modulus velocity of each cap
        self.caps_mod_velocity = np.linalg.norm(self.V, axis=1)

        # Set global flag for system moving
        system_moving = True
        if np.all(self.caps_mod_velocity < self.min_velocity):
            system_moving = False
            return self.X_history, self.V_history
        
        # Duplicate V and X matrix for iterate over them
        V = self.V.copy()
        X = self.X.copy()
            
        # Get the system evolve through the motion dynamics till the system stops moving
        while system_moving:

            # Calculate the next position X(t+1) = X(t) + V(t)
            X_next = X + V

            # Check if collision in the X_next occurs

            
            new_pos, self.velocity = self.collision_resolver.resolve_collision(
                self.caps[move_idx].position, move_idx, direction, self.velocity, cap_radius)

            if new_pos is None:  # Check if collision stopped the motion
                print("Collision with field edges")
                break

            # Update cap position after handling potential collisions
            self.caps[move_idx].position = new_pos
            print("--------------------")
            print("Timestamp:", t)
            print("Current Velocity:", self.velocity)
            # Calculate new velocity
            new_velocity = self.next_velocity(self.velocity)
            print("New Velocity:", new_velocity)
            print("--------------------")
            self.velocity = new_velocity

            # Update timestamp
            self.t += 1

    def next_velocity(self, velocity):
        arr_vel_threshold = np.array([0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10])
        vel_delta = np.linspace(-0.01, -0.02, len(arr_vel_threshold))

        for i, vel in enumerate(arr_vel_threshold):
            if velocity < vel:
                delta = vel_delta[i]
                break
            else:
                delta = vel_delta[-1]
        velocity += delta
        velocity = np.round(velocity, 4)
        return velocity

    


# if __name__ == "__main__":
#%%
import numpy as np
from utils import UtilsRender
from game_entities import CapFactory, Arrow

# %%
from importlib import reload
import utils
import collision_resolver
utils = reload(utils)
ur = utils.UtilsRender()
collision_resolver = reload(collision_resolver)
CollisionResolver = collision_resolver.CollisionResolver

#%%

w = 1920
h = 1080
X = np.array(
    [[  1280,  540],
    [1310,  540],
    [1290,  600],
    ], dtype=np.float32
)
R = np.array([10, 20, 30], dtype=np.float32)
M = np.array([2, 1, 1], dtype=np.float32)

cap_factory = CapFactory(X=X)
arrow = Arrow(
    caps=cap_factory,
    cap_index=0,
    arrow_length=100,
    angle=0
)
mr = MotionResolver(caps=cap_factory, arrow=arrow)
V = mr.V
# mr.start_movement()

#%%
# Collision Resolver
cr = CollisionResolver(
    boundaries=(w, h),
    X=X,
    V=V,
    R=R,
    M=M
)
d_caps_coll = cr.collision_caps()
d_edges_coll = cr.collision_edges()
V_caps = cr.resolve_cap_collisions(d_caps_coll)
V_edges = cr.resolve_edge_collisions(d_edges_coll)


# %%
# ---------------------------------------- #
#   Render
# ---------------------------------------- #
ur.render_snapshot(X, R)
# %%
