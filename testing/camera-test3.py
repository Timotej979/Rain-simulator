import cv2
import numpy as np
import pyrealsense2 as rs
import tkinter as tk
from PIL import Image, ImageTk

class RealSenseCamera:
    """
    Class for RealSense camera
    Methods:
        - get_rgb_frame(): Get RGB frame
        - get_depth_frame(): Get depth frame
        - normalize_depth_frame(depth_frame): Normalize depth frame
        - calculate_average_depth_frame(): Calculate average depth frame
        - calculate_difference_frames(frame1, frame2): Calculate difference frames
        - run(): Run the camera

    """

    # Initialize the camera object
    def __init__(self, num_frames=10, image_size_x=640, image_size_y=480):
        # Create a pipeline
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, image_size_x, image_size_y, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, image_size_x, image_size_y, rs.format.z16, 30)

        # Additional settings to optimize depth image quality
        profile = self.pipeline.start(config)
        depth_sensor = profile.get_device().first_depth_sensor()

        # Adjustments for optimal depth sensing in the specified range
        depth_sensor.set_option(rs.option.exposure, 3000)  # Adjust exposure time (in microseconds)
        depth_sensor.set_option(rs.option.gain, 16)  # Adjust gain
        depth_sensor.set_option(rs.option.laser_power, 250)  # Adjust laser power

        # General attributes
        self.image_size_x = image_size_x
        self.image_size_y = image_size_y
        self.num_frames = num_frames
        self.rgb_frames = []
        self.canvas = None
        self.is_running = False

        # Attributes for ROI selection
        self.start_roi_point = None
        self.roi_points = None 
        self.roi_flag = False 


    ##########################################################################################################################
    # Stream management functions, use this to start and stop the camera streams
    def start_streams(self):
        self.is_running = True
        self.update()

    def stop_streams(self):
        self.is_running = False


    ##########################################################################################################################
    # Get frames from the camera: RGB and depth
    def get_rgb_frame(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        rgb_frame = np.asanyarray(color_frame.get_data())
        return rgb_frame

    def get_depth_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        return depth_frame


    ##########################################################################################################################
    # Frame processing functions
    def normalize_depth_frame(self, depth_frame):
        depth_image = np.asanyarray(depth_frame.get_data())
        q1 = np.percentile(depth_image, 25)
        q3 = np.percentile(depth_image, 75)
        normalized_depth = np.clip((depth_image - q1) / (q3 - q1), 0, 1) * 255
        return normalized_depth.astype(np.uint8)


    ##########################################################################################################################
    # ROI selection functions
    def set_roi(self, event):
        if self.is_running:
            self.roi_flag = False
            x, y = event.x, event.y
            self.start_roi_point = (x, y)

    def update_roi(self, event):
        if self.is_running and self.start_roi_point:
            x, y = event.x, event.y
            self.roi_points = (self.start_roi_point[0], self.start_roi_point[1], x, y)

    def release_roi(self, event):
        if self.is_running and self.start_roi_point:
            x1, y1 = self.start_roi_point
            x2, y2 = event.x, event.y

            # Store the latest ROI points
            self.roi_points = (x1, y1, x2, y2)
            print("Latest ROI Points:", self.roi_points)

            # Reset the start_roi_point attribute
            self.start_roi_point = None
            self.roi_flag = True

    def reset_roi(self):
        self.roi_points = None
        self.roi_flag = False

    ##########################################################################################################################
    # Window update function
    def update(self):
        if self.is_running:
            # Get current depth and RGB frames
            rgb_frame = self.get_rgb_frame()
            depth_frame = self.get_depth_frame()

            # Normalize depth frame
            normalized_depth_frame = self.normalize_depth_frame(depth_frame)

            # Display the RGB frame with the region of interest
            self.rgb_frames = rgb_frame.copy()

            # Display the frames in the Tkinter window
            self.display_frames_tkinter(self.rgb_frames, normalized_depth_frame)

            # Schedule the update method to be called after a delay
            self.canvas.after(10, self.update)

    ##########################################################################################################################
    # Display function
    def display_frames_tkinter(self, rgb_frame, normalized_depth_frame):

        # Convert frames to RGB format for PIL
        rgb_image = Image.fromarray(cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2RGB))
        depth_image = Image.fromarray(normalized_depth_frame)

        # Get size of the Tkinter canvas
        width, height = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2

        # Convert images to PhotoImage
        rgb_photo = ImageTk.PhotoImage(rgb_image)
        depth_photo = ImageTk.PhotoImage(depth_image)

        # Update the Tkinter canvas with images
        self.canvas.create_image(width, 0, anchor="nw", image=rgb_photo, tags="rgb")
        self.canvas.create_image(0, height, anchor="nw", image=depth_photo, tags="depth")

        # Check if roi flag is true
        if self.roi_flag:
            if self.roi_points is not None:
                # Get roi points
                x, y, w, h = self.roi_points
                # Crop the depth frame
                normalized_depth_frame = normalized_depth_frame[y:h, x:w]
                # Draw new rectangle with adjusted coordinates
                self.canvas.create_rectangle(x, y, w, h, outline="red", tags="roi")
        else:
            if self.roi_points is not None:
                # Get roi points
                x, y, w, h = self.roi_points
                # Delete previous rectangle
                self.canvas.delete("roi")
                # Draw new rectangle with adjusted coordinates
                self.canvas.create_rectangle(x, y, w, h, outline="red", tags="roi")

        # Keep a reference to the images to prevent garbage collection
        self.canvas.rgb_photo = rgb_photo
        self.canvas.depth_photo = depth_photo

    ##########################################################################################################################
    # Main function
    def run(self):
        # Create a new Tkinter window
        root = tk.Tk()
        root.title("RealSense Camera GUI")

        # Create the main canvas
        self.canvas = tk.Canvas(root, width=1300, height=990)
        self.canvas.grid(row=0, column=0, columnspan=2, rowspan=2)

        # Create buttons/control section
        buttons_frame = tk.Frame(root)
        buttons_frame.grid(row=0, column=0, sticky="nsew")

        # Title text
        title_label = tk.Label(buttons_frame, text="RealSense Camera Control", font=("Helvetica", 16))
        title_label.pack()

        # Start button
        start_button = tk.Button(buttons_frame, text="Start", command=self.start_streams)
        start_button.pack()

        # Stop button
        stop_button = tk.Button(buttons_frame, text="Stop", command=self.stop_streams)
        stop_button.pack()

        # Reset ROI button
        reset_roi_button = tk.Button(buttons_frame, text="Reset ROI", command=self.reset_roi)
        reset_roi_button.pack()

        # Bind mouse events for region of interest (ROI) selection
        self.canvas.bind("<ButtonPress-1>", self.set_roi)
        self.canvas.bind("<B1-Motion>", self.update_roi)
        self.canvas.bind("<ButtonRelease-1>", self.release_roi)

        # Start the Tkinter main loop
        root.mainloop()

        # Stop the RealSense pipeline when the Tkinter window is closed
        self.pipeline.stop()


if __name__ == "__main__":
    camera = RealSenseCamera(num_frames=10, image_size_x=640, image_size_y=480)
    camera.run()
