cmake_minimum_required(VERSION 3.8)
project(imu_interfaces)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Define message files
set(msg_files
  "msg/IMUmsg.msg"
)

# Generate messages in the 'msg' folder
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/IMUmsg.msg"
  DEPENDENCIES std_msgs sensor_msgs
)

# Export dependencies
ament_export_dependencies(rosidl_default_runtime)

# Enable testing (optional)
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
