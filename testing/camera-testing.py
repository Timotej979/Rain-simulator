#!/usr/bin/env python3
import cv2
import pyrealsense2 as rs

class RealSense():
    """
    Class for RealSense camera
    """

    # Configure RealSense pipeline
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30) 
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

    # Start streaming
    def start(self):
        # Start streaming
        self.pipeline.start(self.config)
        
    # Stop streaming
    def stop(self):
        # Close all windows
        cv2.destroyAllWindows()
        # Stop streaming
        self.pipeline.stop()

    # Pick reference points from the RGB image
    def pick_reference_points(self, color_frame):
        # Display the RGB image for picking reference points
        rgb_image = np.asanyarray(color_frame.get_data())
        cv2.imshow('Pick Reference Points', rgb_image)

        # Set the callback function for mouse events
        reference_points = []

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONUP:
                reference_points.append([x, y])
                # Draw a circle at the clicked point
                cv2.circle(rgb_image, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow('Pick Reference Points', rgb_image)

                # If four points are picked, close the window
                if len(reference_points) == 4:
                    cv2.destroyAllWindows()

        # Set the mouse callback
        cv2.setMouseCallback('Pick Reference Points', mouse_callback)

        # Wait until the user picks four points
        while len(reference_points) < 4:
            cv2.waitKey(1)

        return reference_points

    # Get RGB frames from the camera
    def get_rgb_frame(self):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        return color_image

    # Get depth frames from the camera with hole filling
    def get_depth_frame(self):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        # Apply hole filling filter
        hole_filling = rs.hole_filling_filter()
        depth_frame = hole_filling.process(depth_frame)

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        return depth_image

    def transform_point_cloud(self, reference_points, point_cloud):
        # Convert reference points to a numpy array
        reference_points = np.array(reference_points, dtype=np.float32)

        # Compute the transformation matrix
        transformation_matrix = cv2.getPerspectiveTransform(reference_points[:3], reference_points[1:])

        # Flatten the point cloud
        flat_point_cloud = point_cloud.reshape(-1, 3)

        # Homogeneous coordinates
        hom_point_cloud = np.hstack((flat_point_cloud, np.ones((flat_point_cloud.shape[0], 1))))

        # Apply transformation
        transformed_point_cloud = np.dot(transformation_matrix, hom_point_cloud.T).T[:, :3]

        return transformed_point_cloud


if __name__ == '__main__':
    # Create a RealSense object
    rs_obj = RealSense()

    rs_obj.start()

    while True:
        color_frame = rs_obj.get_rgb_frame()
        depth_frame = rs_obj.get_depth_frame()

        # Pick reference points
        reference_points = rs_obj.pick_reference_points(color_frame)

        # Extract planar surface
        planar_surface = rs_obj.extract_planar_surface(depth_frame)

        # Transform point cloud
        transformed_point_cloud = rs_obj.transform_point_cloud(reference_points, planar_surface.to_array())

        # Display the frames
        cv2.imshow('Color Image', np.asanyarray(color_frame))
        cv2.imshow('Depth Image', np.asanyarray(depth_frame))

        # Optionally display the transformed point cloud
        pcl.visualization.CloudViewing().showPointCloud(transformed_point_cloud.astype(np.float32))

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            rs_obj.stop()
            break