import serial
import sys
import rclpy
from rclpy.node import Node
from imu_msgs.msg import IMUmsg
from std_msgs.msg import Header
import math

class IMUDriver(Node):
    def __init__(self):
        super().__init__('imu_driver')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.serial_port = self.get_serial_port()
        self.publisher_ = self.create_publisher(IMUmsg, 'imu', 10)
        self.timer = self.create_timer(1.0 / 40.0, self.publish_imu_data)  # 40 Hz

    def get_serial_port(self):
        custom_port = self.parse_command_line_args()
        serial_port = custom_port if custom_port else self.get_parameter('port').get_parameter_value().string_value
        serial_baud = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.get_logger().info(f"Using IMU device on port {serial_port} at {serial_baud} baud.")
        try:
            return serial.Serial(serial_port, serial_baud, timeout=200)
        except serial.SerialException as e:
            self.get_logger().error(f"Could not open port {serial_port}: {e}")
            rclpy.shutdown()
            return None

    def parse_command_line_args(self):
        for arg in sys.argv:
            if arg.startswith("port:"):
                return arg.split(":")[1]
        return None

    def publish_imu_data(self):
        if not self.serial_port:
            self.get_logger().warn("Serial port is not initialized.")
            return
        try:
            raw_data = self.serial_port.readline().decode('utf-8').strip()
            self.get_logger().info(f"Raw IMU Data: {raw_data}")
        except serial.SerialException as e:
            self.get_logger().error(f"Error reading from serial port: {e}")
            return
            
        if raw_data.startswith('$VNYMR'):
            parsed_data = self.parse_vnymr(raw_data)
            
            if parsed_data:
                # Create and publish IMU message
                imu_msg = IMUmsg()
                imu_msg.header = Header()
                imu_msg.header.stamp = self.get_clock().now().to_msg()
                imu_msg.header.frame_id = "IMU1_Frame"
                
                # Parse orientation (Yaw, Pitch, Roll)
                imu_msg.imu.orientation.x = parsed_data['quaternion'][0]
                imu_msg.imu.orientation.y = parsed_data['quaternion'][1]
                imu_msg.imu.orientation.z = parsed_data['quaternion'][2]
                imu_msg.imu.orientation.w = parsed_data['quaternion'][3]

                # Parse angular velocity (Gyro)
                imu_msg.imu.angular_velocity.x = parsed_data['gyro'][0]
                imu_msg.imu.angular_velocity.y = parsed_data['gyro'][1]
                imu_msg.imu.angular_velocity.z = parsed_data['gyro'][2]

                # Parse linear acceleration (Accel)
                imu_msg.imu.linear_acceleration.x = parsed_data['accel'][0]
                imu_msg.imu.linear_acceleration.y = parsed_data['accel'][1]
                imu_msg.imu.linear_acceleration.z = parsed_data['accel'][2]
                
                self.publisher_.publish(imu_msg)
                self.get_logger().info(f"Published IMU Data: {parsed_data}")
                
    def parse_vnymr(self, raw_data):
        """Parse the $VNYMR string and extract sensor data."""
        try:
            # Remove checksum and trailing characters
            cleaned_data = raw_data.split('*')[0]  # Discard checksum part
            parts = cleaned_data.split(',')

            # Ensure there are enough parts to unpack
            if len(parts) < 12:
                self.get_logger().error("Insufficient data received from IMU.")
                return None

            return {
                'quaternion': self.euler_to_quaternion(float(parts[3]), float(parts[2]), float(parts[1])),  # roll, pitch, yaw
                'gyro': [float(parts[9]), float(parts[10]), float(parts[11])],  # gyro x, y, z
                'accel': [float(parts[7]), float(parts[8]), float(parts[6])],  # accel x, y, z
                'magnetometer': [float(parts[4]), float(parts[5]), float(parts[3])]  # mag x, y, z
            }
        except ValueError as e:
            self.get_logger().error(f"Value error while parsing IMU data: {e}")
            return None

    def euler_to_quaternion(self, roll, pitch, yaw):
        roll_r = math.radians(roll)
        yaw_r = math.radians(yaw)
        pitch_r = math.radians(pitch)
        
        cy = math.cos(yaw_r * 0.5)
        sy = math.sin(yaw_r * 0.5)
        cp = math.cos(pitch_r * 0.5)
        sp = math.sin(pitch_r * 0.5)
        cr = math.cos(roll_r * 0.5)
        sr = math.sin(roll_r * 0.5)
        
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy
        qw = cr * cp * cy + sr * sp * sy
        
        return [round(qx, 5), round(qy, 5), round(qz, 5), round(qw, 5)]

def main(args=None):
    rclpy.init(args=args)
    imu_driver = IMUDriver()
    if imu_driver.serial_port:
        try:
            rclpy.spin(imu_driver)
        except KeyboardInterrupt:
            pass
        finally:
            imu_driver.destroy_node()
            rclpy.shutdown()
    else:
        imu_driver.get_logger().error("IMU publisher failed to start due to serial port error.")

if __name__ == '__main__':
    main()

