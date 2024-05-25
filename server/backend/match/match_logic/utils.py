import tkinter as tk
import numpy as np

class UtilsRender:
    def __init__(self, window_size=(1920, 1080), delay=100, goal_depth=50, goal_size=200):
        self.window_size = window_size
        self.delay = delay
        self.goal_depth = goal_depth
        self.goal_size = goal_size

    def debug_motion(self, positions: np.ndarray, radius: np.ndarray, print_velocities=None):
        window_size = self.window_size

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{window_size[0]}x{window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=window_size[0], height=window_size[1])
        canvas.pack()

        # Create a label for displaying the timestep
        timestep_label = tk.Label(root, text="Timestep: 0")
        timestep_label.place(x=10, y=10)

        # Draw the initial circles
        circles = []
        for idx, pos in enumerate(positions[0]):
            x, y = pos
            cap_radius = radius[idx]
            circle = canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
            circles.append(circle)

        # Current index to track the timestep
        current_index = [0]  # Use a list to capture the mutable integer in the nested function

        # Define a function to update the position of the circles
        def update_position(event=None, print_velocities=print_velocities):  # event parameter is needed for Tkinter to pass the event object
            timestep = current_index[0]
            if timestep < len(positions):
                for i, pos in enumerate(positions[timestep]):
                    x, y = pos
                    circle = circles[i]
                    cap_radius = radius[i]
                    canvas.coords(circle, x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
                # Update the timestep label
                label = f"Timestep: {timestep}"

                # Add the print of velocity
                if print_velocities is not None:
                    label += f"\nVelocity: {print_velocities[timestep]}"

                # Display the label
                timestep_label.config(text=label)
                # Increment the timestep
                current_index[0] += 1

        # Bind the Enter key to update_position function
        root.bind('<Return>', update_position)

        # Start the tkinter event loop
        root.mainloop()


    def render_motion(self, positions: np.ndarray, radius: np.ndarray, add_delay=False):
        window_size = self.window_size
        if not add_delay:
            delay = self.delay
        else:
            delay = add_delay

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{window_size[0]}x{window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=window_size[0], height=window_size[1])
        canvas.pack()

        # Create a label for displaying the timestep
        timestep_label = tk.Label(root, text="Timestep: 0")
        timestep_label.place(x=10, y=10)

        # Draw the initial circles with indices
        circles = []
        texts = []
        for idx, pos in enumerate(positions[0]):
            x, y = pos
            cap_radius = radius[idx]
            circle = canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
            text = canvas.create_text(x, y, text=str(idx), fill="black", font=("Helvetica", 16, "bold"))
            circles.append((circle, text))

        # Define a function to update the position of the circles and indices
        def update_position(timestep):
            timestep = int(timestep)
            if timestep < len(positions):
                for i, pos in enumerate(positions[timestep]):
                    x, y = pos
                    circle, text = circles[i]
                    cap_radius = radius[i]
                    canvas.coords(circle, x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
                    canvas.coords(text, x, y)
                # Update the timestep label
                timestep_label.config(text=f"Timestep: {timestep}")
                root.after(delay, update_position, str(timestep+1))

        # Start the animation
        root.after(delay, update_position, "0")

        # Start the tkinter event loop
        root.mainloop()

    def render_snapshot(self, position: np.ndarray, radius: np.ndarray):
        """
        Position is a single 2D element of the positions
        array([[1144,  540],
            [1280,  540]])
        Represents a snapshot of a timestep
        """
        window_size = self.window_size

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{window_size[0]}x{window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=window_size[0], height=window_size[1])
        canvas.pack()

        # Draw the circles
        for idx, pos in enumerate(position):
            x, y = pos

            # Draw the circle
            cap_radius = radius[idx]
            canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)

            # Draw the index in the middle of the oval
            canvas.create_text(x, y, text=str(idx), fill="black", font=("Helvetica", 16, "bold"))

        # Start the tkinter event loop
        root.mainloop()

    @staticmethod
    def render_motion_json(payload, response):
        """
        Example of payload:
        # Define the payload
        payload = {
            "configs": [
                {"capIndex": 0, "capCenter": {"x": 250, "y": 250}, "capRadius": 20},
                {"capIndex": 1, "capCenter": {"x": 200, "y": 250}, "capRadius": 20},
                {"capIndex": 2, "capCenter": {"x": 550, "y": 550}, "capRadius": 20},
            ],
            "arrow": {"capIndex": 0, "arrow_length": 100, "angle": 20},
        }
        Example of response:
        response = {
            "motion": [
                {
                "t": 0,
                "configs": [
                    { "capIndex": 0, "capCenter": { "x": 250, "y": 250 }},
                    { "capIndex": 1, "capCenter": { "x": 200, "y": 250 }},
                    { "capIndex": 2, "capCenter": { "x": 550, "y": 555 }}
                ]
                },
                {
                "t": 1,
                "configs": [
                    { "capIndex": 0, "capCenter": { "x": 255, "y": 250 }},
                    { "capIndex": 1, "capCenter": { "x": 205, "y": 250 }},
                    { "capIndex": 2, "capCenter": { "x": 550, "y": 555 }}
                ]
                },
                {
                "t": 2,
                "configs": [
                    { "capIndex": 0, "capCenter": { "x": 260, "y": 250 }},
                    { "capIndex": 1, "capCenter": { "x": 210, "y": 250 }},
                    { "capIndex": 2, "capCenter": { "x": 550, "y": 559 }}
                ]
                },
                {
                "t": 3,
                "configs": [
                    { "capIndex": 0, "capCenter": { "x": 370, "y": 250 }},
                    { "capIndex": 1, "capCenter": { "x": 220, "y": 250 }},
                    { "capIndex": 2, "capCenter": { "x": 550, "y": 570 }}
                ]
                }
            ]
            }
        """
        window_size=(1920, 1080)

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{window_size[0]}x{window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=window_size[0], height=window_size[1])
        canvas.pack()

        # Create a label for displaying the timestep
        timestep_label = tk.Label(root, text="Timestep: 0")
        timestep_label.place(x=10, y=10)

        # Draw the initial circles
        circles = []
        for config in payload["configs"]:
            x = config["capCenter"]["x"]
            y = config["capCenter"]["y"]
            r = config["capRadius"]
            circle = canvas.create_oval(x-r, y-r, x+r, y+r)
            circles.append(circle)

        # Define a function to update the position of the circles
        def update_position(timestep):
            timestep = int(timestep)
            if timestep < len(response["motion"]):
                for config in response["motion"][timestep]["configs"]:
                    x = config["capCenter"]["x"]
                    y = config["capCenter"]["y"]
                    r = config["capRadius"]
                    circle = circles[config["capIndex"]]
                    canvas.coords(circle, x-r, y-r, x+r, y+r)
                # Update the timestep label
                timestep_label.config(text=f"Timestep: {timestep}")
                root.after(1000, update_position, str(timestep+1))

        # Start the animation
        root.after(1000, update_position, "0")

        # Start the tkinter event loop
        root.mainloop()

    # ----------------------------------------------------------- #
    #   Field with Goals
    # ----------------------------------------------------------- #
    def render_field_snapshot(self, position: np.ndarray, radius: np.ndarray, margin=150):
        """
        Position is a single 2D element of the positions
        array([[1144,  540],
            [1280,  540]])
        Represents a snapshot of a timestep
        """
        w, h = self.window_size
        D = self.goal_depth
        g = self.goal_size

        # Add margins to the window size
        window_size = (w + 2 * margin, h + 2 * margin)

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{window_size[0]}x{window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=window_size[0], height=window_size[1])
        canvas.pack()

        # Adjust positions for margins
        def adjust_pos(pos):
            return pos[0] + margin, pos[1] + margin

        # Define field vertices
        TL = adjust_pos((0, 0))
        BL = adjust_pos((0, h))
        TR = adjust_pos((w, 0))
        BR = adjust_pos((w, h))

        # Define left goal vertices
        TLP = adjust_pos((0, (h - g) / 2))
        BLP = adjust_pos((0, (h + g) / 2))
        TLN = adjust_pos((-D, (h - g) / 2))
        BLN = adjust_pos((-D, (h + g) / 2))

        # Define right goal vertices
        TRP = adjust_pos((w, (h - g) / 2))
        BRP = adjust_pos((w, (h + g) / 2))
        TRN = adjust_pos((w + D, (h - g) / 2))
        BRN = adjust_pos((w + D, (h + g) / 2))

        # Draw field edges
        edges = [
            (TL, TLP), (TLP, TLN), (TLN, BLN), (BLN, BLP), (BLP, BL),
            (BL, BR), (BR, BRP), (BRP, BRN), (BRN, TRN), (TRN, TRP),
            (TRP, TR), (TR, TL)
        ]

        for (x1, y1), (x2, y2) in edges:
            canvas.create_line(x1, y1, x2, y2)

        # Draw the caps
        for idx, pos in enumerate(position):
            x, y = adjust_pos(pos)

            # Draw the circle
            cap_radius = radius[idx]
            canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)

            # Draw the index in the middle of the oval
            canvas.create_text(x, y, text=str(idx), fill="black", font=("Helvetica", 16, "bold"))

        # Start the tkinter event loop
        root.mainloop()

    def render_field_motion(self, positions: np.ndarray, radius: np.ndarray, add_delay=False, margin=150):
        window_size = self.window_size
        if not add_delay:
            delay = self.delay
        else:
            delay = add_delay

        w, h = window_size
        D = self.goal_depth
        g = self.goal_size

        # Add margins to the window size
        full_window_size = (w + 2 * margin, h + 2 * margin)

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{full_window_size[0]}x{full_window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=full_window_size[0], height=full_window_size[1])
        canvas.pack()

        # Adjust positions for margins
        def adjust_pos(pos):
            return pos[0] + margin, pos[1] + margin

        # Define field vertices
        TL = adjust_pos((0, 0))
        BL = adjust_pos((0, h))
        TR = adjust_pos((w, 0))
        BR = adjust_pos((w, h))

        # Define left goal vertices
        TLP = adjust_pos((0, (h - g) / 2))
        BLP = adjust_pos((0, (h + g) / 2))
        TLN = adjust_pos((-D, (h - g) / 2))
        BLN = adjust_pos((-D, (h + g) / 2))

        # Define right goal vertices
        TRP = adjust_pos((w, (h - g) / 2))
        BRP = adjust_pos((w, (h + g) / 2))
        TRN = adjust_pos((w + D, (h - g) / 2))
        BRN = adjust_pos((w + D, (h + g) / 2))

        # Draw field edges
        edges = [
            (TL, TLP), (TLP, TLN), (TLN, BLN), (BLN, BLP), (BLP, BL),
            (BL, BR), (BR, BRP), (BRP, BRN), (BRN, TRN), (TRN, TRP),
            (TRP, TR), (TR, TL)
        ]

        for (x1, y1), (x2, y2) in edges:
            canvas.create_line(x1, y1, x2, y2)

        # Create a label for displaying the timestep
        timestep_label = tk.Label(root, text="Timestep: 0")
        timestep_label.place(x=10, y=10)

        # Draw the initial circles with indices
        circles = []
        texts = []
        for idx, pos in enumerate(positions[0]):
            x, y = adjust_pos(pos)
            cap_radius = radius[idx]
            circle = canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
            text = canvas.create_text(x, y, text=str(idx), fill="black", font=("Helvetica", 16, "bold"))
            circles.append(circle)
            texts.append(text)

        # Define a function to update the position of the circles and indices
        def update_position(timestep):
            timestep = int(timestep)
            if timestep < len(positions):
                for i, pos in enumerate(positions[timestep]):
                    x, y = adjust_pos(pos)
                    circle = circles[i]
                    text = texts[i]
                    cap_radius = radius[i]
                    canvas.coords(circle, x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
                    canvas.coords(text, x, y)
                # Update the timestep label
                timestep_label.config(text=f"Timestep: {timestep}")
                root.after(delay, update_position, str(timestep+1))

        # Start the animation
        root.after(delay, update_position, "0")

        # Start the tkinter event loop
        root.mainloop()
