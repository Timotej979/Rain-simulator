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
    def __init__(self):
        # Create a pipeline
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Additional settings to optimize depth image quality
        profile = self.pipeline.start(config)
        depth_sensor = profile.get_device().first_depth_sensor()

        # Adjustments for optimal depth sensing in the specified range
        depth_sensor.set_option(rs.option.exposure, 3000)  # Adjust exposure time (in microseconds)
        depth_sensor.set_option(rs.option.gain, 16)  # Adjust gain
        depth_sensor.set_option(rs.option.laser_power, 250)  # Adjust laser power

        # General attributes
        self.num_frames = 10
        self.rgb_frames = []
        self.canvas = None
        self.is_running = False

        # Attributes for ROI selection
        self.roi_points = None 

        # Attributes for tkinter display
        self.cp_width = 100
        self.cp_height = 200


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
    def select_roi(self):
        # Get the current depth frame and normalize it
        depth_frame = self.normalize_depth_frame(self.get_depth_frame())
        # Convert depth frame to RGB for display
        depth_frame = cv2.cvtColor(depth_frame, cv2.COLOR_GRAY2RGB)
        # Open new window for ROI selection
        cv2.namedWindow("Select ROI")
        cv2.imshow("Select ROI", depth_frame)
        # Select ROI
        roi_points = cv2.selectROI("Select ROI", depth_frame, fromCenter=False, showCrosshair=True)
        # Close window when ROI is selected
        cv2.destroyWindow("Select ROI")
        # Save ROI points
        self.roi_points = roi_points
        self.roi_flag = True

    def reset_roi(self):
        self.roi_points = None

    ##########################################################################################################################
    # Window update function
    def update(self):
        if self.is_running:
            # Get current depth and RGB frames
            rgb_frame = self.get_rgb_frame()
            depth_frame = self.get_depth_frame()

            # Save current RGB frame
            self.rgb_frame = rgb_frame

            # Save current depth frame and normalize it
            self.normalized_depth_frame = self.normalize_depth_frame(depth_frame)

            # Display the frames in the Tkinter window
            self.display_frames_tkinter()

            # Schedule the update method to be called after a delay
            self.canvas.after(10, self.update)

    ##########################################################################################################################
    # Display function
    def display_frames_tkinter(self):
        # Crop depth image if ROI is selected
        if self.roi_points is not None:
            # Get ROI points
            x, y, w, h = self.roi_points
            # Crop depth image
            self.normalized_depth_frame = self.normalized_depth_frame[y:y + h, x:x + w]

        # Convert frames to RGB format for PIL
        rgb_image = Image.fromarray(cv2.cvtColor(self.rgb_frame, cv2.COLOR_BGR2RGB))
        depth_image = Image.fromarray(self.normalized_depth_frame)

        # Convert images to PhotoImage
        self.rgb_photo = ImageTk.PhotoImage(rgb_image)
        self.depth_photo = ImageTk.PhotoImage(depth_image)

        # Update the Tkinter rgb frame
        self.rgb_stream_frame.imgtk = self.rgb_photo
        self.rgb_stream_frame.configure(image=self.rgb_photo)

        # Update the Tkinter depth frame
        self.depth_stream_frame.imgtk = self.depth_photo
        self.depth_stream_frame.configure(image=self.depth_photo)

        # Keep a reference to the images to prevent garbage collection
        self.rgb_stream_frame.rgb_photo = self.rgb_photo
        self.depth_stream_frame.depth_photo = self.depth_photo


    ##########################################################################################################################
    # Main function
    def run(self):
        # Create a new Tkinter window
        root = tk.Tk()
        root.title("RealSense Camera GUI")

        # Create the main canvas
        self.canvas = tk.Canvas(root, width=1200, height=990)
        self.canvas.grid(row=0, column=1, padx=10, pady=5)

        # Create the Control Panel
        control_pannel = tk.Frame(root, width=self.cp_width, height=self.cp_height)
        control_pannel.grid(row=0, column=0, sticky="nsew")

        # Inside the control panel, create frames for each section
        # Stream Control Section
        stream_control_frame = tk.Frame(control_pannel)
        stream_control_frame.grid(row=0, column=0, padx=10, pady=5)
        stream_control_label = tk.Label(stream_control_frame, text="Stream Control")
        stream_control_label.grid(row=0, column=0, padx=10, pady=5)

        # Buttons Frame
        buttons_frame = tk.Frame(stream_control_frame)
        buttons_frame.grid(row=1, column=0, padx=10, pady=5)

        # Add buttons
        start_stream_button = tk.Button(buttons_frame, text="Start Stream", command=self.start_streams)
        start_stream_button.grid(row=0, column=0, padx=10, pady=5)

        stop_stream_button = tk.Button(buttons_frame, text="Stop Stream", command=self.stop_streams)
        stop_stream_button.grid(row=0, column=1, padx=10, pady=5)


        # Frame processing section
        frame_processing_frame = tk.Frame(control_pannel)
        frame_processing_frame.grid(row=1, column=0, padx=10, pady=5)
        frame_processing_label = tk.Label(frame_processing_frame, text="Frame Processing", font=("Helvetica", 14))
        frame_processing_label.grid(row=0, column=0, padx=10, pady=5)

        # Buttons Frame
        buttons_frame = tk.Frame(frame_processing_frame)
        buttons_frame.grid(row=1, column=0, padx=10, pady=5)

        # Add buttons
        enable_frame_averaging_button = tk.Button(buttons_frame, text="Enable Frame Averaging")
        enable_frame_averaging_button.grid(row=0, column=0, padx=10, pady=5)

        # Add numeric input field and set the value to self.num_frames and always update self.num_frames when the value is changed
        self.num_frames_var = tk.StringVar()
        self.num_frames_var.set(str(self.num_frames))
        num_frames_input = tk.Entry(buttons_frame, textvariable=self.num_frames_var)
        num_frames_input.grid(row=0, column=1, padx=10, pady=5)


        # ROI Control Section
        roi_control_frame = tk.Frame(control_pannel)
        roi_control_frame.grid(row=2, column=0, padx=10, pady=5)
        roi_control_label = tk.Label(roi_control_frame, text="ROI Control", font=("Helvetica", 14))
        roi_control_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Buttons Frame
        buttons_frame = tk.Frame(roi_control_frame)
        buttons_frame.grid(row=1, column=0, padx=10, pady=5)

        # Add buttons
        select_roi_button = tk.Button(buttons_frame, text="Select ROI", command=self.select_roi)
        select_roi_button.grid(row=0, column=0, padx=10, pady=5)

        reset_roi_button = tk.Button(buttons_frame, text="Reset ROI", command=self.reset_roi)
        reset_roi_button.grid(row=0, column=1, padx=10, pady=5)


        # Create the rgb stream frame
        self.rgb_stream_frame = tk.Label(self.canvas)
        self.rgb_stream_frame.grid(row=0, column=0, padx=10, pady=5)

        # Create the depth stream frame
        self.depth_stream_frame = tk.Label(self.canvas)
        self.depth_stream_frame.grid(row=1, column=0, padx=10, pady=5)





        # Start the Tkinter main loop
        root.mainloop()

        # Stop the RealSense pipeline when the Tkinter window is closed
        self.pipeline.stop()




if __name__ == "__main__":
    camera = RealSenseCamera()
    camera.run()
