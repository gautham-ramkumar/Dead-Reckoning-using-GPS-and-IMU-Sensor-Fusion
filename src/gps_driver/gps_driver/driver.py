import serial
import sys
import utm
import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from gps_msgs.msg import GPSmsg
from builtin_interfaces.msg import Time

def convert_to_decimal(degrees_minutes, direction):
    try:
        degrees = int(degrees_minutes[:2])
        minutes = float(degrees_minutes[2:])
        decimal_degrees = degrees + (minutes / 60)
        return -decimal_degrees if direction in ['S', 'W'] else decimal_degrees
    except ValueError:
        return None

def parse_gpgga(gpgga_sentence):
    parts = gpgga_sentence.split(',')
    if gpgga_sentence.startswith('$GPGGA') and len(parts) > 14:
        time_utc = parts[1]
        latitude = convert_to_decimal(parts[2], parts[3])
        longitude = convert_to_decimal(parts[4], parts[5])
        altitude = float(parts[9]) if parts[9] else None
        return (time_utc, latitude, longitude, altitude) if all((latitude, longitude)) else None
    return None

class GPSPublisher(Node):
    def __init__(self):
        super().__init__('gps_publisher')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('port', '/dev/ttyUSB0'),
                ('baudrate', 4800),
                ('sampling_rate', 10.0),
                ('timeout', 3.0)
            ]
        )

        custom_port = self.parse_command_line_args()
        self.port_name = custom_port or self.get_parameter('port').value
        self.baud_rate = self.get_parameter('baudrate').value
        self.sampling_rate = self.get_parameter('sampling_rate').value
        self.timeout = self.get_parameter('timeout').value

        self.initialize_serial_port()

        self.publisher_ = self.create_publisher(GPSmsg, 'gps', 10)
        self.timer = self.create_timer(1.0 / self.sampling_rate, self.timer_callback)
        self.last_gpgga_time = self.get_clock().now()

    def parse_command_line_args(self):
        return next((arg.split(':')[1] for arg in sys.argv if arg.startswith('port:')), None)

    def initialize_serial_port(self):
        try:
            self.port = serial.Serial(self.port_name, self.baud_rate, timeout=self.timeout)
            self.get_logger().info(f"Connected to GPS device on {self.port_name} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open port {self.port_name}: {e}")
            self.port = None
            rclpy.shutdown()

    def timer_callback(self):
        if not self.port:
            self.get_logger().warn("Serial port is not initialized.")
            return

        try:
            line = self.port.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$GPGGA'):
                self.process_gpgga(line)
            self.check_gpgga_timeout()
        except serial.SerialException as e:
            self.get_logger().error(f"Serial communication error: {e}")

    def process_gpgga(self, line):
        self.get_logger().info(f"Raw GPS Data: {line}")
        parsed_data = parse_gpgga(line)
        if parsed_data:
            self.publish_gps_data(*parsed_data)
            self.last_gpgga_time = self.get_clock().now()

    def publish_gps_data(self, time_utc, latitude, longitude, altitude):
        utm_coords = utm.from_latlon(latitude, longitude)
        msg = GPSmsg()
        msg.header = Header()
        msg.header.stamp = self.create_gps_time(time_utc)
        msg.header.frame_id = "GPS1_Frame"
        msg.latitude = latitude
        msg.longitude = longitude
        msg.altitude = altitude if altitude is not None else float('nan')
        msg.utm_easting, msg.utm_northing, msg.zone, msg.letter = utm_coords

        self.publisher_.publish(msg)
        self.get_logger().info(f"Published Data: Lat: {latitude}, Lon: {longitude}, Alt: {altitude}")

    def create_gps_time(self, time_utc):
        hours, minutes, seconds = int(time_utc[0:2]), int(time_utc[2:4]), float(time_utc[4:])
        gps_time = Time()
        gps_time.sec = int(hours * 3600 + minutes * 60 + int(seconds))
        gps_time.nanosec = int((seconds % 1) * 1e9)
        return gps_time

    def check_gpgga_timeout(self):
        if (self.get_clock().now() - self.last_gpgga_time).nanoseconds > 5e9:
            self.get_logger().warn("No $GPGGA sentence received for over 5 seconds.")

def main(args=None):
    rclpy.init(args=args)
    gps_publisher = GPSPublisher()
    
    if gps_publisher.port:
        try:
            rclpy.spin(gps_publisher)
        except KeyboardInterrupt:
            gps_publisher.get_logger().info("Node stopped cleanly.")
        finally:
            gps_publisher.destroy_node()
            rclpy.shutdown()
    else:
        gps_publisher.get_logger().error("GPS publisher failed to start due to serial port error.")

if __name__ == '__main__':
    main()
