from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    return LaunchDescription([
        # IMU Device Parameters
        DeclareLaunchArgument(
            'imu_port',
            default_value='/dev/ttyUSB0',
            description='Serial port for the IMU device'
        ),
        DeclareLaunchArgument(
            'imu_baudrate',
            default_value='115200',
            description='Baud rate for the IMU device'
        ),

        # GPS Device Parameters
        DeclareLaunchArgument(
            'gps_port',
            default_value='/dev/ttyUSB1',
            description='Serial port for the GPS device'
        ),
        DeclareLaunchArgument(
            'gps_baudrate',
            default_value='4800',
            description='Baud rate for the GPS device'
        ),

        # IMU Node
        Node(
            package='imu_driver',
            executable='driver',
            name='imu_driver',
            output='screen',
            parameters=[
                {'port': LaunchConfiguration('imu_port')},
                {'baudrate': LaunchConfiguration('imu_baudrate')}
            ]
        ),

        # GPS Node
        Node(
            package='gps_driver',
            executable='driver',
            name='gps_driver',
            output='screen',
            parameters=[
                {'port': LaunchConfiguration('gps_port')},
                {'baudrate': LaunchConfiguration('gps_baudrate')}
            ]
        ),
    ])

