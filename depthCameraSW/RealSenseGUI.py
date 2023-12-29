import os, cv2, logging
import numpy as np
import pyrealsense2 as rs
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


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
        self.rgb_frames = []
        self.canvas = None
        self.is_running = False

        # Attributes for ROI selection
        self.roi_points = None 

        # Attributes for recording
        self.recording = False

        # Attributes for frame averaging
        self.frame_averaging_enabled = True
        self.num_frames = 10

        # Volume calculation
        self.volume_change = None
        self.volume_change_threshold = 0.7

        # Attributes for tkinter display
        self.cp_width = 70
        self.cp_height = 100


    ##########################################################################################################################
    # Stream management functions, use this to start and stop the camera streams
    def start_streams(self):
        print("Starting streams")
        print("Frame averaging enabled: ", self.frame_averaging_enabled)
        print("Number of frames: ", self.num_frames)
        print("ROI points: ", self.roi_points)
        print("Volume change threshold: {:.2f}".format(self.volume_change_threshold))
        print("Recording: ", self.recording)
        self.is_running = True
        self.update()

    def stop_streams(self):
        print("Stopping streams")
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

    def get_real_depth_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        depth_image = np.zeros((480, 640), dtype=np.float32)
        for i in range(480):
            for j in range(640):
                depth_image[i, j] = depth_frame.get_distance(j, i)
        return depth_image


    ##########################################################################################################################
    # Frame processing functions
    def normalize_depth_frame(self, depth_frame):
        depth_image = np.asanyarray(depth_frame.get_data())
        q1 = np.percentile(depth_image, 25)
        q3 = np.percentile(depth_image, 75)
        normalized_depth = np.clip((depth_image - q1) / (q3 - q1), 0, 1) * 255
        return normalized_depth.astype(np.uint8)

    def calculate_average_depth_frame(self):
        # Create the average depth frame
        average_depth_frame = np.asanyarray(self.get_depth_frame().get_data())
        for i in range(self.num_frames - 1):
            average_depth_frame = average_depth_frame + np.asanyarray(self.get_depth_frame().get_data())
        # Normalize the average depth frame
        average_depth_frame = average_depth_frame / self.num_frames
        return average_depth_frame

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
    # Recording functions
    def start_recording(self):
        # Check if average frame is enabled
        if self.frame_averaging_enabled:
            # Get the average depth frame
            self.first_depth_frame = self.calculate_average_depth_frame()
        else:
            # Get current depth frame
            self.first_depth_frame = self.get_depth_frame()

        # Check if ROI is selected and crop the real depth frame
        if self.roi_points is not None:
            real_first_depth_frame = self.get_real_depth_frame()
            self.real_first_depth_frame = real_first_depth_frame[self.roi_points[1]:self.roi_points[1] + self.roi_points[3],
                                                                    self.roi_points[0]:self.roi_points[0] + self.roi_points[2]]
        else:
            self.real_first_depth_frame = self.get_real_depth_frame()

        # Record depth and rgb frames to a folder videos
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.rgb_video = cv2.VideoWriter('videos/rgb.avi', fourcc, 15.0, (640, 480))
        self.depth_video = cv2.VideoWriter('videos/depth.avi', fourcc, 15.0, (640, 480), isColor=False)

        self.recording = True

    def stop_recording(self):
        # Release the video objects
        self.recording = False
        self.rgb_video.release()
        self.depth_video.release()

        # Check if average frame is enabled
        if self.frame_averaging_enabled:
            # Get the average depth frame
            self.last_depth_frame = self.calculate_average_depth_frame()
        else:
            # Get current depth frame
            self.last_depth_frame = self.get_depth_frame()

        # Check if ROI is selected and crop the real depth frame
        if self.roi_points is not None:
            real_last_depth_frame = self.get_real_depth_frame()
            self.real_last_depth_frame = real_last_depth_frame[self.roi_points[1]:self.roi_points[1] + self.roi_points[3],
                                                                self.roi_points[0]:self.roi_points[0] + self.roi_points[2]]
        else:
            self.real_last_depth_frame = self.get_real_depth_frame()
        
        # Calculate the difference between the last and first depth frames depending on the frame averaging setting
        if not self.frame_averaging_enabled:
            # Convert depth frames to NumPy arrays
            first_depth_array = np.asanyarray(self.first_depth_frame.get_data())
            last_depth_array = np.asanyarray(self.last_depth_frame.get_data())

            # Calculate the difference between the last and first depth frames
            self.difference_depth_frame = first_depth_array - last_depth_array

        else:
            # Calculate the difference between the last and first depth frames
            self.difference_depth_frame = self.first_depth_frame - self.last_depth_frame

        self.real_difference_depth_frame = self.real_first_depth_frame - self.real_last_depth_frame

        # Calculate the change in volume between the last and first depth frames
        self.volume_change = np.sum(self.real_difference_depth_frame) / 1e3
        print("Volume change is {:.1f} liters".format(self.volume_change))

        # Find out which pixels have changed
        self.changed_pixels = np.where(self.real_difference_depth_frame > self.volume_change_threshold)

        # Normalize the differnce depth frame
        q1 = np.percentile(self.difference_depth_frame, 25)
        q3 = np.percentile(self.difference_depth_frame, 75)
        normalized_diff_frame = np.clip((self.difference_depth_frame - q1) / (q3 - q1), 0, 1) * 255
        self.normalized_diff_frame = normalized_diff_frame.astype(np.uint8)

        # Check if ROI is selected
        if self.roi_points is not None:
            # Get ROI points
            x, y, w, h = self.roi_points
            # Crop depth image
            self.normalized_diff_frame = self.normalized_diff_frame[y:y + h, x:x + w]

        # Display the difference depth frame
        cv2.namedWindow("Frame difference")
        cv2.imshow("Frame difference", self.normalized_diff_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Convert the difference depth frame to an RGB image and highlight the changed pixels
        self.norm_diff_depth_frame_changed = cv2.cvtColor(self.normalized_diff_frame, cv2.COLOR_GRAY2RGB)
        self.norm_diff_depth_frame_changed[self.changed_pixels] = [0, 0, 255]

        # Display the same frame but with the changed pixels highlighted and a legend with volume change
        cv2.namedWindow("Volume change: {:.1f} liters".format(self.volume_change))
        cv2.imshow("Volume change: {:.1f} liters".format(self.volume_change), self.norm_diff_depth_frame_changed)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Write the volume change to the measurements log
        self.measurements_log.insert(tk.END, "Meassurement settings: \n")
        self.measurements_log.insert(tk.END, "Frame averaging enabled: {}\n".format(self.frame_averaging_enabled))
        self.measurements_log.insert(tk.END, "Number of frames: {}\n".format(self.num_frames))
        self.measurements_log.insert(tk.END, "Volume change threshold: {:.2f}\n".format(self.volume_change_threshold))
        self.measurements_log.insert(tk.END, "Volume change: {:.1f} liters\n".format(self.volume_change))
        self.measurements_log.insert(tk.END, "----------------------------------------\n")
        self.measurements_log.see(tk.END)


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
        if self.recording:
            # Write RGB frame to video
            self.rgb_video.write(self.rgb_frame)
            # Write depth frame to video
            self.depth_video.write(self.normalized_depth_frame)

        # Check if ROI is selected for depth image
        if self.roi_points is not None:
            # Get ROI points for depth image
            x_depth, y_depth, w_depth, h_depth = self.roi_points
            # Convert depth image to RGB format for PIL
            depth_image_rgb = Image.fromarray(cv2.cvtColor(self.normalized_depth_frame, cv2.COLOR_GRAY2RGB))
            # Create a drawing object for depth image
            draw_depth = ImageDraw.Draw(depth_image_rgb)
            # Draw blue rectangle on the depth image using ROI points
            draw_depth.rectangle([x_depth, y_depth, x_depth + w_depth, y_depth + h_depth], outline=(255, 0, 0), width=2)
            # Use the modified depth image with the rectangle
            depth_image = depth_image_rgb
        else:
            depth_image = Image.fromarray(self.normalized_depth_frame)

        # Convert frames to RGB format for PIL
        rgb_image = Image.fromarray(cv2.cvtColor(self.rgb_frame, cv2.COLOR_BGR2RGB))

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
        enable_frame_averaging_var = tk.IntVar()
        enable_frame_averaging_button = tk.Checkbutton(buttons_frame,
                                                       text="Enable Frame Averaging",
                                                       variable=enable_frame_averaging_var,
                                                       command=lambda: setattr(self, 'frame_averaging_enabled', enable_frame_averaging_var.get() == 1))
        enable_frame_averaging_button.grid(row=0, column=0, padx=10, pady=5)

        # Add numeric input field and set the value to self.num_frames and always update self.num_frames when the value is changed
        num_frames_var = tk.IntVar()
        num_frames_scale = tk.Scale(buttons_frame,
                                    from_=1, to=100,
                                    variable=num_frames_var,
                                    orient=tk.HORIZONTAL,
                                    command=lambda value: setattr(self, 'num_frames', num_frames_var.get()))
        num_frames_scale.set(self.num_frames)  # Set the initial value
        num_frames_scale.grid(row=0, column=1, padx=10, pady=5)


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


        # Volume calibration
        volume_calibration_frame = tk.Frame(control_pannel)
        volume_calibration_frame.grid(row=3, column=0, padx=10, pady=5)
        volume_calibration_label = tk.Label(volume_calibration_frame, text="Volume Calculation Calibration", font=("Helvetica", 14))
        volume_calibration_label.grid(row=0, column=0, padx=10, pady=5)

        # Buttons Frame
        buttons_frame = tk.Frame(volume_calibration_frame)
        buttons_frame.grid(row=1, column=0, padx=10, pady=5)

        # Add buttons
        volume_change_threshold_var = tk.DoubleVar()
        volume_change_threshold_scale = tk.Scale(buttons_frame,
                                                 from_=0, to=5,
                                                 resolution=0.02,
                                                 length=200,
                                                 variable=volume_change_threshold_var,
                                                 orient=tk.HORIZONTAL,
                                                 command=lambda value: setattr(self, 'volume_change_threshold', volume_change_threshold_var.get()))
        volume_change_threshold_scale.set(self.volume_change_threshold)  # Set the initial value
        volume_change_threshold_scale.grid(row=0, column=0, padx=10, pady=5)


        # Recording section
        recording_frame = tk.Frame(control_pannel)
        recording_frame.grid(row=4, column=0, padx=10, pady=5)
        recording_label = tk.Label(recording_frame, text="Recording control", font=("Helvetica", 14))
        recording_label.grid(row=0, column=0, padx=10, pady=5)

        # Buttons Frame
        buttons_frame = tk.Frame(recording_frame)
        buttons_frame.grid(row=1, column=0, padx=10, pady=5)

        # Add buttons
        start_recording_button = tk.Button(buttons_frame, text="Start Recording", command=self.start_recording)
        start_recording_button.grid(row=0, column=0, padx=10, pady=5)

        stop_recording_button = tk.Button(buttons_frame, text="Stop Recording", command=self.stop_recording)
        stop_recording_button.grid(row=0, column=1, padx=10, pady=5)

        
        # Meassurements log section
        measurements_log_frame = tk.Frame(control_pannel)
        measurements_log_frame.grid(row=5, column=0, padx=10, pady=5)
        measurements_log_label = tk.Label(measurements_log_frame, text="Measurements", font=("Helvetica", 14))
        measurements_log_label.grid(row=0, column=0, padx=10, pady=5)

        # Create a text box for the measurements log
        self.measurements_log = tk.Text(measurements_log_frame, width=50, height=30)
        self.measurements_log.grid(row=1, column=0, padx=10, pady=5)

        # Create a scrollbar for the measurements log
        measurements_log_scrollbar = tk.Scrollbar(measurements_log_frame)
        measurements_log_scrollbar.grid(row=1, column=1, sticky="ns")

        # Attach the scrollbar to the measurements log
        self.measurements_log.config(yscrollcommand=measurements_log_scrollbar.set)
        measurements_log_scrollbar.config(command=self.measurements_log.yview)

        # Clear the measurements log button
        clear_measurements_log_button = tk.Button(measurements_log_frame, text="Clear log", command=lambda: self.measurements_log.delete(1.0, tk.END))
        clear_measurements_log_button.grid(row=2, column=0, padx=10, pady=5)


        # Create the frames for the RGB and depth streams
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
