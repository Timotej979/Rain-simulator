import cv2
import numpy as np
import pyrealsense2 as rs

class RealSenseCamera:
    def __init__(self, num_frames=10):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.pipeline.start(config)
        
        self.num_frames = num_frames
        self.depth_frames = []
        self.rgb_frames = []

    def get_rgb_frame(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        rgb_frame = np.asanyarray(color_frame.get_data())
        return rgb_frame

    def get_depth_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        return depth_frame

    def normalize_depth_frame(self, depth_frame):
        depth_image = np.asanyarray(depth_frame.get_data())
        normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
        return normalized_depth.astype(np.uint8)

    def calculate_average_depth_frame(self):
        for _ in range(self.num_frames):
            depth_frame = self.get_depth_frame()
            self.depth_frames.append(np.asanyarray(depth_frame.get_data()))

        average_depth_frame_data = np.mean(self.depth_frames, axis=0).astype(np.uint16)
        self.depth_frames = []  # Reset the list for the next iteration
        
        # Update the buffer data with the averaged data
        depth_frame = self.get_depth_frame()
        depth_frame_data = np.asanyarray(depth_frame.get_data())
        depth_frame_data[:, :] = average_depth_frame_data
        
        return depth_frame

    def calculate_difference_frames(self, frame1, frame2):
        diff_frame = cv2.absdiff(frame1, frame2)
        return diff_frame

    def run(self):
        while True:
            # Get current depth and RGB frames
            depth_frame = self.get_depth_frame()
            rgb_frame = self.get_rgb_frame()

            # Normalize depth frame
            normalized_depth_frame = self.normalize_depth_frame(depth_frame)

            # Calculate and display the current depth frame
            cv2.imshow("Current Depth Frame", normalized_depth_frame)

            # Calculate and display the average depth frame
            average_depth_frame = self.calculate_average_depth_frame()
            normalized_average_depth_frame = self.normalize_depth_frame(average_depth_frame)
            cv2.imshow("Average Depth Frame", normalized_average_depth_frame)

            # Calculate and display the difference between current and average frames
            diff_frame = self.calculate_difference_frames(normalized_depth_frame, normalized_average_depth_frame)
            cv2.imshow("Difference Frame", diff_frame)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    camera = RealSenseCamera(num_frames=10)
    camera.run()
