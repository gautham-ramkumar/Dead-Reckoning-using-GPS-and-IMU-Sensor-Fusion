# IMU-GPS Dead Reckoning with VectorNav VN-100

This project implements a full dead reckoning pipeline using data from the VectorNav VN-100 tactical-grade IMU and GPS. It fuses raw accelerometer, gyroscope, and magnetometer data to estimate orientation and velocity, ultimately reconstructing the vehicle trajectory.

## Features

- Magnetometer calibration (hard/soft iron correction)
- Complementary filter for yaw estimation (fusing magnetometer and gyro)
- Low-pass filtering for IMU velocity smoothing
- Trajectory estimation via dead reckoning
- GPS comparison and performance metrics (RMSE, position error)

## Highlights

- **40.95% reduction** in raw accelerometer noise using custom Butterworth filtering
- Fused yaw estimation using complementary filtering improves heading stability
- Full IMU vs GPS trajectory comparison with aligned heading and position normalization

## Requirements

- Python 3.8+
- ROS2 (with `rosbag2_py` and message interfaces)
- NumPy, Matplotlib, SciPy, scikit-learn

## Results
![image](https://github.com/user-attachments/assets/b2832c19-6846-4e09-8201-4091375c4284)
![image](https://github.com/user-attachments/assets/b3aa6a43-ce85-40ad-8cac-10035a0874bf)
![image](https://github.com/user-attachments/assets/a0036938-278c-469a-b713-71ac72ce24cf)
