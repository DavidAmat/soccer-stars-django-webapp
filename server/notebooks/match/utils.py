import tkinter as tk

class UtilsRender:
    def __init__(self, cap_radius, window_size=(1920, 1080), delay=100):
        self.cap_radius = cap_radius
        self.window_size = window_size
        self.delay = delay


    def render_motion(self, positions):
        cap_radius = self.cap_radius
        window_size = self.window_size
        delay = self.delay

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
        for pos in positions[0]:
            x, y = pos
            circle = canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
            circles.append(circle)

        # Define a function to update the position of the circles
        def update_position(timestep):
            timestep = int(timestep)
            if timestep < len(positions):
                for i, pos in enumerate(positions[timestep]):
                    x, y = pos
                    circle = circles[i]
                    canvas.coords(circle, x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)
                # Update the timestep label
                timestep_label.config(text=f"Timestep: {timestep}")
                root.after(delay, update_position, str(timestep+1))

        # Start the animation
        root.after(delay, update_position, "0")

        # Start the tkinter event loop
        root.mainloop()

    def render_snapshot(self, position):
        """
        Position is a single 2D element of the positions
        array([[1144,  540],
            [1280,  540]])
        Represents a snapshot of a timestep
        """
        cap_radius = self.cap_radius
        window_size = self.window_size

        # Create the tkinter window
        root = tk.Tk()
        root.geometry(f"{window_size[0]}x{window_size[1]}")

        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=window_size[0], height=window_size[1])
        canvas.pack()

        # Draw the circles
        for pos in position:
            x, y = pos
            canvas.create_oval(x-cap_radius, y-cap_radius, x+cap_radius, y+cap_radius)

        # Start the tkinter event loop
        root.mainloop()

    @staticmethod
    def render_motion_json(payload, response):
        """
        Example of payload:
        # Define the payload
        payload = {
            "capRadius": 20,
            "configs": [
                {"capIndex": 0, "capCenter": {"x": 250, "y": 250}},
                {"capIndex": 1, "capCenter": {"x": 200, "y": 250}},
                {"capIndex": 2, "capCenter": {"x": 550, "y": 550}},
            ],
            "arrow": {"capIndex": 0, "distance": 100, "angle": 20},
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
            r = payload["capRadius"]
            circle = canvas.create_oval(x-r, y-r, x+r, y+r)
            circles.append(circle)

        # Define a function to update the position of the circles
        def update_position(timestep):
            timestep = int(timestep)
            if timestep < len(response["motion"]):
                for config in response["motion"][timestep]["configs"]:
                    x = config["capCenter"]["x"]
                    y = config["capCenter"]["y"]
                    r = payload["capRadius"]
                    circle = circles[config["capIndex"]]
                    canvas.coords(circle, x-r, y-r, x+r, y+r)
                # Update the timestep label
                timestep_label.config(text=f"Timestep: {timestep}")
                root.after(1000, update_position, str(timestep+1))

        # Start the animation
        root.after(1000, update_position, "0")

        # Start the tkinter event loop
        root.mainloop()