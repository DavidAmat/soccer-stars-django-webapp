# collision_resolver.py
import numpy as np
from typing import Tuple, List


class CollisionResolver:
    def __init__(self, R, M, boundaries=(1920, 1080), goal_depth=100, goal_size=600):
        """
        X: np.ndarray
            Array of shape (n, 2) where n is the number of caps
        V: np.ndarray
            Array of shape (n, 2) where n is the number of caps and its value is the velocity
        R: np.ndarray
            Array of shape (n,) where n is the number of caps and its value is the element radius
        M: np.ndarray
            Array of shape (n,) where n is the number of caps and its value is the element mass
        """
        self.boundaries = boundaries  # boundaries should be a tuple (width, height)
        self.w, self.h = boundaries
        self.R = R
        self.M = M
        self.n = len(R)  # Number of caps
        self.goal_depth = goal_depth
        self.goal_size = goal_size
        self.R_dist = self.get_radius_distances_matrix()

    # ------------------------------------------------- #
    #       Get Final Velocity
    # ------------------------------------------------- #
    def resolve_collision(self, X, V):
        """
        Main function to resolve collisions. It takes the position matrix X and the velocity matrix V
        and returns the final velocity matrix after resolving the collisions.

        Parameters:
        X : np.ndarray
            Position matrix of shape (n, 2) where n is the number of caps.
        V : np.ndarray
            Velocity matrix of shape (n, 2) where n is the number of caps.

        Returns:
        np.ndarray
            Final velocity matrix after resolving the collisions with shape (n, 2).
        """

        # Get the naive X_next position in time if no collisions occur
        X_next = X + V

        # Check if collisions occur
        edge_collisions = self.get_edge_collisions(X_next=X_next)
        cap_collisions = self.get_cap_collisions(X_next=X_next)

        # If not collisions (empty lists) return the X_next and V
        if not edge_collisions and not cap_collisions:
            return V
        
        # If collisions, resolve the collision priority (priority on cap collisions)
        r_edge_collisions = self.resolve_collision_priority(
            edge_collisions=edge_collisions, 
            cap_collisions=cap_collisions
        )

        # ************************ #
        #   Cap Collisions
        # ************************ #
        V_coll_cap_after, idx_coll_cap_final = self.resolve_cap_collisions(
            cap_collisions=cap_collisions, V=V, X=X
        )

        # ************************ #
        #   Edge Collisions
        # ************************ #
        # Get a list of tuples with the cap index, the coordinate index (0 for x and 1 for y) and the new velocity
        l_new_velocity_components = self.resolve_edge_collisions(V=V, r_edge_collisions=r_edge_collisions)

        # ************************ #
        #   Final velocities
        # ************************ #
        # Keep the original velocity matrix and replace the velocities of the caps that collided
        Vf = V.copy()

        # Iterate over the cap indices for the edge collisions
        if l_new_velocity_components is not None and len(l_new_velocity_components) > 0:
            # For every idx of the cap, take the coordinate index we need to flip and the new velocity
            for idx, coord_idx, new_vel in l_new_velocity_components:
                Vf[idx, coord_idx] = new_vel

        # Iterate over the cap indices for the cap collisions
        if V_coll_cap_after is not None:
            for i, idx in enumerate(idx_coll_cap_final):
                Vf[idx] = V_coll_cap_after[i]

        return Vf
    
    def resolve_field_collision(self, X, V):
        """
        Main function to resolve collisions. It takes the position matrix X and the velocity matrix V
        and returns the final velocity matrix after resolving the collisions.

        Parameters:
        X : np.ndarray
            Position matrix of shape (n, 2) where n is the number of caps.
        V : np.ndarray
            Velocity matrix of shape (n, 2) where n is the number of caps.

        Returns:
        np.ndarray
            Final velocity matrix after resolving the collisions with shape (n, 2).
        """

        # Get the naive X_next position in time if no collisions occur
        X_next = X + V

        # Check if collisions occur
        field_idx_collisions, edge_collisions = self.get_field_collisions(X_prev=X, X_next=X_next)
        cap_collisions = self.get_cap_collisions(X_next=X_next)

        # If not collisions (empty lists) return the X_next and V
        if not edge_collisions and not cap_collisions:
            return V
        
        # If collisions, resolve the collision priority (priority on cap collisions)
        first_priority_edge_coll, second_priority_edge_coll = self.resolve_multiple_collision(
            edge_collisions=edge_collisions, 
            cap_collisions=cap_collisions
        )

        # ************************ #
        #   Cap Collisions
        # ************************ #
        V_coll_cap_after, idx_coll_cap_final = self.resolve_cap_collisions(
            cap_collisions=cap_collisions, V=V, X=X
        )

        # ********************************** #
        #   First Priority Edge Collisions
        # ********************************** #
        # Get a list of tuples with the cap index, the coordinate index (0 for x and 1 for y) and the new velocity
        l_velocity_first_coll = self.resolve_edge_collisions(V=V, r_edge_collisions=first_priority_edge_coll)
        l_velocity_second_coll = self.resolve_edge_collisions(V=V_coll_cap_after, r_edge_collisions=second_priority_edge_coll)

        # ************************ #
        #   Final velocities
        # ************************ #
        # Keep the original velocity matrix and replace the velocities of the caps that collided
        Vf = V.copy()

        # Iterate over the cap indices for the edge collisions
        if l_velocity_first_coll is not None and len(l_velocity_first_coll) > 0:
            # For every idx of the cap, take the coordinate index we need to flip and the new velocity
            for idx, coord_idx, new_vel in l_velocity_first_coll:
                Vf[idx, coord_idx] = new_vel

        # Iterate over the cap indices for the cap collisions
        if V_coll_cap_after is not None:
            for i, idx in enumerate(idx_coll_cap_final):
                Vf[idx] = V_coll_cap_after[i]

        # Iterate over the cap indices for the edge collisions that underwent first a cap collision
        if l_velocity_second_coll is not None and len(l_velocity_second_coll) > 0:
            # For every idx of the cap, take the coordinate index we need to flip and the new velocity
            for idx, coord_idx, new_vel in l_velocity_second_coll:
                Vf[idx, coord_idx] = new_vel

        # ************************ #
        #   Net velocity reduction
        # ************************ #
        # When any cap collides with the net, reduce it's velocity by 50%
        # if the ball is the one hitting the net (goal), reduce the velocity by 90%
        for cap_idx, edge_idx in field_idx_collisions:
            # Net collisions
            if edge_idx in [0,1,2,5,6,7]:
                # Check if the cap is the ball (last index of Vf rows)
                if cap_idx == Vf.shape[0] - 1:
                    Vf[cap_idx] *= 0.1
                else:
                    Vf[cap_idx] *= 0.5

        return Vf



    # ------------------------------------------------- #
    #   Radii distances (threshold for cap collisions)
    # ------------------------------------------------- #
    def get_radius_distances_matrix(self):
        R = self.R

        # Radii matrix: Create a 2D array representing the sum of radii for each pair of caps
        R_i = R[:, np.newaxis]  # Shape (n, 1)
        R_j = R[np.newaxis, :]  # Shape (1, n)
        R_distances = R_i + R_j  # Shape (n, n) 
        return R_distances


    # ------------------------------------------------- #
    #       Cap collisions
    # ------------------------------------------------- #
    def get_cap_collisions(self, X_next):
        """
        Returns a list of tuples where each tuple contains the indices of the colliding caps.
        Example: [(0, 1), (2, 3), ...] means that cap 0 is colliding with cap 1 and cap 2 is colliding with cap 3.
        """
        

        # Position matrices to allow broadcasting
        X_i = X_next[:, np.newaxis, :]  # Shape (n, 1, 2)
        X_j = X_next[np.newaxis, :, :]  # Shape (1, n, 2)

        # Compute distances between all pairs
        delta_Xij = X_i - X_j  # Shape (n, n, 2)

        # The norm of the result is the distance between each pair of points
        modulus_pairs = np.sum((delta_Xij) ** 2, axis=2) # Shape (n, n)
        distances = np.sqrt(modulus_pairs)  # Shape (n, n)

        # Boolean masking indicating if cap i and cap j are colliding (distance < 2 * R_dist)
        # where self.R_dist is the sum of the radii of the two caps
        collision_matrix = distances <= self.R_dist

        np.fill_diagonal(collision_matrix, False) # Exclude self-collisions

        # Make it upper triangular
        collision_matrix = np.triu(collision_matrix)

        # Get the list of indices in tuples like [(i, j), ...]
        colliding_indices = np.argwhere(collision_matrix)
        colliding_indices = [tuple(idx) for idx in colliding_indices]

        # Ensure that a single cap cannot be in multiple collision
        corrected_colliding_indices = self.ensure_single_cap_collision(distances, colliding_indices)

        return corrected_colliding_indices
    
    def ensure_single_cap_collision(self, distances, cap_collisions):
        """
        Takes the output list of tuples from get_cap_collisions and checks that a single cap cannot be in multiple collisions.
        If a cap is in multiple collisions, we keep the collision with the smallest distance.
        Make sure we don't include the same interaction twice (i.e. (i, j) and (j, i)), imposing i < j.

        Returns a list of tuples with the corrected collisions.
        """

        # Create a dictionary to store the collisions for each cap
        d_caps_coll = {i: [] for i in range(self.n)}

        # Fill the dictionary with the collisions
        for i, j in cap_collisions:
            if i < j:
                d_caps_coll[i].append(j)
            if j < i:
                d_caps_coll[j].append(i)

        # Check if a cap is in multiple collisions
        for i, colliding_caps in d_caps_coll.items():
            if len(colliding_caps) > 1:
                # Get the distances for the colliding caps
                distances_i = distances[i, colliding_caps]
                # Get the index of the closest cap
                closest_cap = colliding_caps[np.argmin(distances_i)]
                # Keep only the closest cap
                d_caps_coll[i] = [closest_cap]

        # Convert the dictionary back to a list of tuples
        corrected_collisions = [(i, j) for i, caps in d_caps_coll.items() for j in caps]
        return corrected_collisions
    
    # ------------------------------------------------- #
    #       Edge collisions
    # ------------------------------------------------- #
    def get_edge_collisions(self, X_next):
        """
        Matrix of shape (n, 4) where n is the number of caps. 
        The element (i, j) is True if cap i is colliding with edge j.
        Edge order (startin from left edge and going counter-clockwise): 
        [left, top, right, bottom] -> [0, 1, 2, 3]

        Converts the final collision matrix (n x 4) into a list of tuples
        where the first element is the cap index and the second the edge index
        like [(cap_i, edge_j), ...]
        """
        R = self.R
        w, h = self.boundaries

        # Get edge collision matrix
        edge_collision_matrix = np.zeros((self.n, 4), dtype=bool)

        # Left to the cap
        X_left = X_next - R[:, np.newaxis]

        # Right to the cap
        X_right = X_next + R[:, np.newaxis]

        # Left edge and right edge
        edge_collision_matrix[:, 0] = X_left[:, 0] <= 0
        edge_collision_matrix[:, 2] = X_right[:, 0] >= w

        # Top edge and bottom edge
        edge_collision_matrix[:, 1] = X_left[:, 1] <= 0
        edge_collision_matrix[:, 3] = X_right[:, 1] >= h

        # Convert to list of tuples
        colliding_indices = np.argwhere(edge_collision_matrix)
        colliding_indices = [tuple(idx) for idx in colliding_indices]

        return colliding_indices
    
    def get_field_collisions(self, X_prev, X_next):
        """
        Matrix of shape (n, 4) where n is the number of caps.
        The element (i, j) is True if cap i is colliding with edge j.
        Edge order (starting from left edge and going counter-clockwise):
        [left, top, right, bottom] -> [0, 1, 2, 3]

        Converts the final collision matrix (n x 10) into a list of tuples
        where the first element is the cap index and the second the edge index
        like [(cap_i, edge_j), ...]
        """
        R = self.R
        w, h = self.boundaries
        D = self.goal_depth
        g = self.goal_size

        # Calculate goal positions
        TL = (0,0)
        BL = (0, h)
        TR = (w, 0)
        BR = (w, h)
        TLP = (0, (h - g) / 2)
        BLP = (0, (h + g) / 2)
        TLN = (-D, (h - g) / 2)
        BLN = (-D, (h + g) / 2)
        TRP = (w, (h - g) / 2)
        BRP = (w, (h + g) / 2)
        TRN = (w + D, (h - g) / 2)
        BRN = (w + D, (h + g) / 2)

        # Initialize edge collision matrix
        edge_collision_matrix = np.zeros((self.n, 12), dtype=bool)

        for i in range(self.n):
            xn, yn = X_next[i]
            xp, yp = X_prev[i]
            r = R[i]

            # ------------------------------------------------- #
            #  Define constants
            # ------------------------------------------------- #
            # Horizontal limits
            xnet_left = TLN[0]
            xfield_left = TLP[0]
            xfield_right = TRP[0]
            xnet_right = TRN[0]

            # Vertical limits
            yfield_top = TL[1]
            yfield_bottom = BL[1]
            ynet_top_lateral = TLP[1]
            ynet_bottom_lateral = BLP[1]

            # ------------------------------------------------- #
            #  Left Field Collisions
            # ------------------------------------------------- #
            # ***************************** #
            # Collision with the main left net
            # ***************************** #
            # since nothing can go through the net, we can just check if the cap surpases the left net
            edge_collision_matrix[i, 0] = xn - r <= xnet_left
            
            # ***************************** #
            # Collision with top lateral net
            # ***************************** #
            # Chech the cap collides with the top lateral of the left goal net
            edge_collision_matrix[i, 1] = (
                yp - r > ynet_top_lateral and yn - r <= ynet_top_lateral and
                xn - r <= xfield_left
            )

            # ***************************** #
            # Collision with bottom lateral net
            # ***************************** #
            # Check the cap collides with the bottom lateral of the left goal net
            edge_collision_matrix[i, 2] = (
                yp + r < ynet_bottom_lateral and yn + r >= ynet_bottom_lateral and
                xn - r <= xfield_left
            )

            # ***************************** #
            # Collision with top left field edge
            # ***************************** #
            # Check the cap collides with the field left edge on top ynet_top_lateral
            edge_collision_matrix[i, 3] = (
                xn - r <= xfield_left and
                yp - r < ynet_top_lateral and yn - r <= ynet_top_lateral
            )

            # ***************************** #
            # Collision with bottom left field edge
            # ***************************** #
            # Check the cap collides with the field left edge on bottom ynet_bottom_lateral
            edge_collision_matrix[i, 4] = (
                xn - r <= xfield_left and
                # yn + r > ynet_bottom_lateral
                yp + r > ynet_bottom_lateral and yn + r >= ynet_bottom_lateral
            )

            # ------------------------------------------------- #
            #  Right Field Collisions
            # ------------------------------------------------- #
            # ***************************** #
            # Collision with the main right net
            # ***************************** #
            # since nothing can go through the net, we can just check if the cap surpases the right net
            edge_collision_matrix[i, 5] = (
                xn + r >= xnet_right
            )

            # ***************************** #
            # Collision with top lateral net
            # ***************************** #
            # Check the cap collides with the top lateral of the right goal net
            edge_collision_matrix[i, 6] = (
                yp - r > ynet_top_lateral and yn - r <= ynet_top_lateral and
                xn + r >= xfield_right
            )

            # ***************************** #
            # Collision with bottom lateral net
            # ***************************** #
            # Check the cap collides with the bottom lateral of the right goal net
            edge_collision_matrix[i, 7] = (
                yp + r < ynet_bottom_lateral and yn + r >= ynet_bottom_lateral and
                xn + r >= xfield_right
            )

            # ***************************** #
            # Collision with top right field edge
            # ***************************** #
            # Check the cap collides with the field right edge on top ynet_top_lateral
            edge_collision_matrix[i, 8] = (
                xn + r >= xfield_right and
                yp - r < ynet_top_lateral and yn - r <= ynet_top_lateral
            )

            # ***************************** #
            # Collision with bottom right field edge
            # ***************************** #
            # Check the cap collides with the field right edge on bottom ynet_bottom_lateral
            edge_collision_matrix[i, 9] = (
                xn + r >= xfield_right and
                yp + r > ynet_bottom_lateral and yn + r >= ynet_bottom_lateral
            )

            # ------------------------------------------------- #
            #  Top and Bottom Field Collisions
            # ------------------------------------------------- #
            # ***************************** #
            # Collision with top field edge
            # ***************************** #
            edge_collision_matrix[i, 10] = yn - r <= yfield_top

            # ***************************** #
            # Collision with bottom field edge
            # ***************************** #
            edge_collision_matrix[i, 11] = yn + r >= yfield_bottom


        # Convert to list of tuples
        colliding_indices = np.argwhere(edge_collision_matrix)
        colliding_indices = [tuple(idx) for idx in colliding_indices]

        # For every collision, convert the collision id (from 0 to 11)
        # into the edge id (0 to 3), where 0 is a collision with an element
        # that will revert the x velocity to a positive value, 1 is a collision
        # with an element that will revert the y velocity to a positive value,
        # 2 is a collision with an element that will revert the x velocity to a negative value
        # and 3 is a collision with an element that will revert the y velocity to a negative value.
        map_collision_to_edge = {
            0: 0, 1: 1, 2: 3, 3: 0, 4: 0, 5: 2, 6: 1, 7: 3, 8: 2, 9: 2, 10: 1, 11: 3
        }


        colliding_edges = [(idx[0], map_collision_to_edge[idx[1]]) for idx in colliding_indices]


        return colliding_indices, colliding_edges
    
    # ------------------------------------------------- #
    #       Resolve multiple collisions
    # ------------------------------------------------- #
    def resolve_collision_priority(self, edge_collisions, cap_collisions):
        """
        Gets all the caps with the collisions and imposes that the cap indices that are 
        present in a cap collision are not present in an edge collision. If a cap is present
        in both, the cap collision takes priority.

        Returns
        -------
        List of tuples
            List of tuples with the cap index and the edge index that the cap is colliding with.
        """
        resolved_edge_collisions = []
        set_edge_coll = set()

        # Cap Collisions
        for cap_i, cap_j in cap_collisions:
            set_edge_coll.add(cap_i)
            set_edge_coll.add(cap_j)

        # Edge Collisions
        for cap_i, edge_idx in edge_collisions:
            if cap_i not in set_edge_coll:
                resolved_edge_collisions.append((cap_i, edge_idx))

        return resolved_edge_collisions
    
    def resolve_multiple_collision(self, edge_collisions, cap_collisions):
        """
        Gets all the caps with the collisions and imposes that the cap indices that are 
        present in a cap collision are not present in the first priority edge_collisions.
        But, for the edge collisions whose cap is involved into a cap_collision
        first priority is given to the cap_collisions and once we have the output velocity
        from the collision of the caps, then we will invert the component of the velocity
        of the affected cap that is colliding with the edge.
        Edge indices reminder: 0: left, 1: top, 2: right, 3: bottom

        Returns
        -------
        first_priority_edge_collisions : List of tuples
            List of tuples with the cap index and the edge index that the cap is colliding with.
            Example: [(0, 1), (2, 3), ...] means that cap 0 is colliding with edge 1 and cap 2 is colliding with edge 3.
        second_priority_edge_collisions : List of tuples
            List of tuples with the cap index and the edge index that the cap is colliding with.
            Example: [(0, 1), (2, 3), ...] means that cap 0 is colliding with edge 1 and cap 2 is colliding with edge 3.
        """
        first_priority_edge_collisions = []
        second_priority_edge_collisions = []
        set_edge_coll = set()

        # Cap Collisions
        for cap_i, cap_j in cap_collisions:
            set_edge_coll.add(cap_i)
            set_edge_coll.add(cap_j)

        # Edge Collisions
        for cap_i, edge_idx in edge_collisions:
            if cap_i not in set_edge_coll:
                first_priority_edge_collisions.append((cap_i, edge_idx))
            else:
                second_priority_edge_collisions.append((cap_i, edge_idx))

        return first_priority_edge_collisions, second_priority_edge_collisions
    
    # ------------------------------------------------- #
    #       Caps Collision Velocity resolver
    # ------------------------------------------------- #
    def resolve_cap_collisions(self, cap_collisions: List[Tuple], V: np.array, X: np.array):
        """
        Takes a list of pairs of cap indices that are colliding and resolves the collision
        using the resolve_cap_pair_collision function. The V matrix is the velocity matrix
        of shape (n, 2) where n is the number of total caps. The X matrix is the position matrix
        of shape (n, 2) and the M matrix is the mass matrix of shape (n,).

        Returns the new velocity matrix after the collisions and the indices of the caps that
        were involved in the collisions. The dimensions of V is (m, 2) and the dimensions of the
        indices is (m,) where m is the number of caps that were involved in the collisions.
        """
        M = self.M
        V_coll_cap_final = None
        idx_coll_cap_final = None

        for coll_idx_pair in cap_collisions:
            X_coll_cap = np.take(X, coll_idx_pair, axis=0)
            V_coll_cap = np.take(V, coll_idx_pair, axis=0)
            M_coll_cap = np.take(M, coll_idx_pair, axis=0)

            # Get the velocity after the collision of those pairs
            V_coll_cap_after = self.resolve_cap_pair_collision(V=V_coll_cap, X=X_coll_cap, M=M_coll_cap)

            if V_coll_cap_final is None:
                V_coll_cap_final = V_coll_cap_after
                idx_coll_cap_final = np.array(coll_idx_pair)
            else:
                V_coll_cap_final = np.vstack((V_coll_cap_final, V_coll_cap_after))
                idx_coll_cap_final = np.hstack((idx_coll_cap_final, coll_idx_pair))
        
        return V_coll_cap_final, idx_coll_cap_final


    def resolve_cap_pair_collision(self, V: np.array, X: np.array, M: np.array):
        """
        Gets the velocities from two cap indices (i,j) colliding, where the V shape is (2,2) and takes
        that pair positions and masses to calculate the new velocities after the collision. The mass 
        vector M is a vector of masses for each body of shape (2,).
        """
        V_new = np.copy(V)

        # Step 1: Calculate the normal and tangent unit vectors
        delta_pos = X[1] - X[0]
        distance = np.linalg.norm(delta_pos)
        if distance == 0:
            return V

        un = delta_pos / distance  # Unit normal vector
        ut = np.array([-un[1], un[0]])  # Unit tangent vector

        # Step 2: Create velocity vectors
        v1 = V[0]
        v2 = V[1]

        # Step 3: Project velocities onto normal and tangential components
        v1n = np.dot(v1, un)
        v1t = np.dot(v1, ut)
        v2n = np.dot(v2, un)
        v2t = np.dot(v2, ut)

        # Step 4: New tangential velocities (they don't change)
        v1t_prime = v1t
        v2t_prime = v2t

        # Step 5: New normal velocities (using 1D collision formulas)
        m1, m2 = M
        v1n_prime = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
        v2n_prime = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

        # Step 6: Convert scalar normal and tangential velocities to vectors
        v1n_vec = v1n_prime * un
        v1t_vec = v1t_prime * ut
        v2n_vec = v2n_prime * un
        v2t_vec = v2t_prime * ut

        # Step 7: Final velocities by adding normal and tangential components
        V_new[0] = v1n_vec + v1t_vec
        V_new[1] = v2n_vec + v2t_vec

        return V_new

    # ------------------------------------------------- #
    #       Edge Collision Velocity resolver
    # ------------------------------------------------- #
    def resolve_edge_collisions(self, V: np.array, r_edge_collisions: np.array):
        """
        Receives r_edge_collisions as a list of tuples with the cap index, the edge index and the new velocity.
        Returns a list of tuples with the cap index, the coordinate index (0 for x and 1 for y) and the new velocity.
        Basically, detects how to flip the sign of the velocity based on the edge collision.
        
        Returns
        -------
        List of tuples
            List of tuples with the cap index, the coordinate index (0 for x and 1 for y) and the new velocity.
        """
        if len(r_edge_collisions) == 0:
            return []
        
        # Createa list of tuples of 3 elements (cap index, coordinate index, new velocity)
        # where coordinate index is 0 for x and 1 for y
        new_velocities_components = []

        for cap_idx, edge_idx in r_edge_collisions:
            if edge_idx == 0:
                # Collision with left edge, turn the velocity into the right (positive)
                new_velocities_components.append((cap_idx, 0, abs(V[cap_idx, 0])))
            if edge_idx == 1:
                # Collision with top edge, turn the velocity into the bottom (positive)
                new_velocities_components.append((cap_idx, 1, abs(V[cap_idx, 1])))
            if edge_idx == 2:
                # Collision with right edge, turn the velocity into the left (negative)
                new_velocities_components.append((cap_idx, 0, -abs(V[cap_idx, 0])))
            if edge_idx == 3:
                # Collision with bottom edge, turn the velocity into the top (negative)
                new_velocities_components.append((cap_idx, 1, -abs(V[cap_idx, 1])))

        return new_velocities_components
    
    # ------------------------------------------------- #
    #       Momentum Conservation
    # ------------------------------------------------- #
    @staticmethod
    def check_momentum_conservation(V_initial, V_final, M):
        """
        Checks if momentum is conserved between initial and final velocities.

        Parameters:
        V_initial : np.ndarray
            Initial velocity matrix (n x 2).
        V_final : np.ndarray
            Final velocity matrix (n x 2).
        M : np.ndarray
            Vector of masses for each body (length n).

        Returns:
        bool
            True if momentum is conserved, False otherwise.
        """

        momentum_initial = np.sum(V_initial * M[:, np.newaxis], axis=0)
        momentum_final = np.sum(V_final * M[:, np.newaxis], axis=0)
        
        return momentum_initial, momentum_final
    
    # ------------------------------------------------- #
    #       Kinetic Energy Conservation
    # ------------------------------------------------- #
    @staticmethod
    def check_kinetic_energy_conservation(V_initial, V_final, M):
        """
        Checks if kinetic energy is conserved between initial and final velocities.

        Parameters:
        V_initial : np.ndarray
            Initial velocity matrix (n x 2).
        V_final : np.ndarray
            Final velocity matrix (n x 2).
        M : np.ndarray
            Vector of masses for each body (length n).

        Returns:
        bool
            True if kinetic energy is conserved, False otherwise.
        """
        ke_initial = np.sum(0.5 * M * np.sum(V_initial ** 2, axis=1))
        ke_final = np.sum(0.5 * M * np.sum(V_final ** 2, axis=1))
        
        return ke_initial, ke_final



if __name__ == "__main__":

    w = 1920
    h = 1080
    X = np.array(
        [[  1275,  530],
        [1307,  500],
        [1310,  700],
        [1310,  560],
        [20,  100],
        ], dtype=np.float32
    )
    R = np.array([25, 25, 25, 25, 25], dtype=np.float32)
    M = np.array([1, 1, 1, 1, 1], dtype=np.float32)

    V = np.array(
        [[2, 2],
        [0, 0],
        [0, 0],
        [0, 0],
        [-1, 0],
        ], dtype=np.float32
    )
    X_next = X + V
    cr = CollisionResolver(X, R, M)
