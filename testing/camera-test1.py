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

    # Get frames from the camera: RGB and depth
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
        # Get height and width of the depth frame
        height = depth_frame.get_height()
        width = depth_frame.get_width()
        # Create a NumPy array to store depth values
        depth_list = np.zeros((height, width), dtype=np.float32)
        # Populate the depth values in the array
        for x in range(height):
            for y in range(width):
                if x < depth_frame.get_height() and y < depth_frame.get_width():
                    depth_list[x][y] = depth_frame.get_distance(y, x)
        # Normalize the depth values to the range 0-255
        print(depth_list)
        return depth_list


    def get_average_depth_frame(self, num_frames):
        # Set the avg to first frame
        depth_frame_avg = self.get_depth_frame()
        # Loop over the rest for average and divide by frame number
        for i in range(num_frames - 1):
            # Add the frame to the average
            depth_frame_avg = depth_frame_avg + self.get_depth_frame()

        # Average the frames
        depth_frame_avg = depth_frame_avg / num_frames
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


    def calculate_diff_avg_frames(self, image, num_frames):
        # Get average depth frame
        depth_frame1 = self.get_average_depth_frame(num_frames)
        depth_frame2 = self.get_average_depth_frame(num_frames)

        # Compute the difference
        depth_frame_diff = depth_frame1 - depth_frame2

        return depth_frame_diff

    def homographic_transform(self, frame):
        # Set the homography points
        points_I = self.calibration_points
        points_J = input("Enter the ratio of the rectangle sides (Example input: 1.1:2.3 ): ")
        points_J = points_J.split(':')
        points_J = np.array([0, int(points_J[0] * 100), 0, int(points_J[1] * 100)])
        
        # Compute the homography
        H = cv2.getPerspectiveTransform(points_I, points_J)

        # Get ROI for our case
        roi = self.calibration_points

        # Apply the homography
        dst = cv2.warpPerspective(frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]], H, (500, 500))
        
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

        # Get RGB and depth frame
        rgb_image = cameraInstance.get_rgb_frame()
        depth_frame = cameraInstance.get_depth_frame()

        # Display depth frame
        cv2.imshow("Depth Frame", depth_frame)
        key = cv2.waitKey(0)
        if key == ord(' '):
            cv2.destroyAllWindows()


        # Calculate diff frame
        #diff_frame = cameraInstance.calculate_diff_avg_frames(depth_frame, 5)

        # Display the diff frame
        #cv2.imshow("Diff Frame", diff_frame)
        #key = cv2.waitKey(0)
        #if key == ord(' '):
        #    cv2.destroyAllWindows()

        # Apply homographic transform
        #dst = cameraInstance.homographic_transform(diff_frame)

        # Display the diff frame
        #cv2.imshow("Homographic Transform", dst)
        #key = cv2.waitKey(0)
        #if key == ord(' '):
        #    cv2.destroyAllWindows()


    finally:
        # Stop streaming
        cameraInstance.stop()



