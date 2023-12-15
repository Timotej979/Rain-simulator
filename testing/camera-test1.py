#!/usr/bin/env python3
import cv2
import numpy as np
import pyrealsense2 as rs


class RealSense():
    """
    Class for RealSense camera
    Methods:
        start(): Start streaming
        stop(): Stop streaming
        get_rgb_frame(): Get RGB frame
        get_depth_frame(): Get depth frame
        average_depth_frames(num_frames): Average depth frames
        select_calibration_points(): Select calibration points
        difference_avg_frames(image, num_frames): Difference average frames
    """

    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    # Stream management functions, use this to start and stop the camera
    def start(self):
        self.pipeline.start(self.config)
        self.frames = self.pipeline.wait_for_frames()

    def stop(self):
        cv2.destroyAllWindows()
        self.pipeline.stop()

    # Get frames from the camera RGB and depth
    def get_rgb_frame(self):
        color_frame = self.frames.get_color_frame()
        if not color_frame:
            return None
        # Convert the frame to a numpy array
        rgb_frame = np.asanyarray(color_frame.get_data())
        return rgb_frame

    def get_depth_frame(self):
        depth_frame = self.frames.get_depth_frame()
        if not depth_frame:
            return None
        # Convert the frame to a numpy array
        depth_frame = np.asanyarray(depth_frame.get_data())
        return depth_frame

    def average_depth_frames(self, num_frames):
        # Loop over the number of frames
        for i in range(num_frames):
            # Loop to always get a new frame
            depth_frame = None
            while(depth_frame == None):
                depth_frame = self.get_depth_frame()
            # Add the frame to the average
            depth_frame_avg = depth_frame_avg + depth_frame

        # Average the frames
        depth_frame_avg = num_frames
        return depth_frame_avg


    def select_calibration_points(self):
        # Loop to always get a new frame
        color_frame = None
        while(color_frame == None):
            color_frame = self.frames.get_color_frame()

        # Convert the frame to a numpy array
        frame = np.asanyarray(color_frame.get_data())

        # Select ROI, spacebar to exit
        roi = cv2.selectROI("Select the region of interest", frame, fromCenter=False, showCrosshair=False)

        # Crop the image
        croped_image = frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        cv2.destroyAllWindows()
        
        # Display the cropped image exit with spacebar
        cv2.imshow("Cropped Image", croped_image)
        key = cv2.waitKey(0)
        if key == ord(' '):
            cv2.destroyAllWindows()

        # Save the ROI to a class variable
        self.calibration_points = np.array([roi])


    def difference_avg_frames(self, image, num_frames):
        # Get average depth frame
        depth_frame1 = self.average_depth_frames(num_frames)
        depth_frame2 = self.average_depth_frames(num_frames)

        # Compute the difference
        depth_frame_diff = depth_frame1 - depth_frame2

        return depth_frame_diff

    def homographic_transform(self):
        points_I = self.calibration_points
        points_J = [0, 300, 0, 300]
        # Compute the homography
        H = cv2.getPerspectiveTransform(points_I, points_J)
        # Apply the homography
        dst = cv2.warpPerspective(image, H, (300, 300))
        return dst




if __name__ == '__main__':
    
    # Create a RealSense object
    cameraInstance = RealSense()
    
    # Start streaming
    cameraInstance.start()

    # Catch all errors
    try:
        # Select calibration points
        cameraInstance.select_calibration_points()

        



    finally:
        # Stop streaming
        cameraInstance.stop()



