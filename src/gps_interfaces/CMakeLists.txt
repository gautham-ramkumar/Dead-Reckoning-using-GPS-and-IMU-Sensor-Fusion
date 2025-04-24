cmake_minimum_required(VERSION 3.5)
project(gps_interfaces)

# Find necessary packages
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# Generate the custom message files
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/GPSmsg.msg"
  DEPENDENCIES std_msgs
)

# Include directories for building
include_directories(include)

# Mark the package for installation
ament_package()

# Mark message files for installation
install(DIRECTORY msg
  DESTINATION share/${PROJECT_NAME}/msg
)

