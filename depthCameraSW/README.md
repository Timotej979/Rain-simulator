# RealSense Camera GUI

This project provides a graphical user interface (GUI) for working with Intel RealSense camera D435i using Python. The GUI allows you to control and visualize the RGB and depth streams from the camera, perform frame processing, select regions of interest (ROIs), and more.

## Setup

### Conda Environment

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Timotej979/Rain-simulator.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd depthCameraSW
    ```

3. **Create a conda environment using the provided `environment.yml` file:**

    ```bash
    conda env create -f environment.yml
    ```

4. **Activate the conda environment:**

    ```bash
    conda activate realsense-camera-env
    ```

### Pip Requirements

Alternatively, you can use `pip` to install the required packages:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Timotej979/Rain-simulator.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd depthCameraSW
    ```

3. **Install the required packages using `pip` and the provided `requirements.txt` file:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Script

After setting up the environment, you can run the RealSense Camera GUI script:

```bash
python3 RealSenseGUI.py
```

This will launch the Tkinter window with the camera streams and control panel.

## GUI Components

### Stream Control Section

- Start Stream: Initiates the RealSense camera streams.
- Stop Stream: Stops the RealSense camera streams.

### Frame Processing Section

- Enable Frame Averaging: Enables or disables frame averaging.
- Number of Frames: Adjusts the number of frames used for averaging.

### ROI Control Section

- Select ROI: Allows the user to select a region of interest (ROI) in the depth image.
- Reset ROI: Resets the selected ROI.

### Volume Calculation Calibration Section

- Volume Change Threshold: Adjusts the threshold for detecting volume changes.

### Recording Control Section

- Start Recording: Initiates the recording of RGB and depth frames.
- Stop Recording: Stops the recording and performs volume change calculations.

### Measurements Log Section

- Measurements Log: Displays information about frame averaging, the number of frames, volume change threshold, and volume change.
- Clear Log: Clears the log for clearer display
- Delete data folder: Deletes the content of data folder

### RGB and Depth Streams Display

- RGB Stream: Displays the real-time RGB camera stream.
- Depth Stream: Displays the real-time depth camera stream. The depth frames can be processed, and changes can be visualized.

![realsensegui.png](/docs/assets/realsensegui.png)