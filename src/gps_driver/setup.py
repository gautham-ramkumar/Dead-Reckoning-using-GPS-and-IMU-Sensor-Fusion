from setuptools import setup

package_name = 'gps_driver'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/gps_launch.py']),
    ],
    install_requires=['setuptools', 'serial', 'utm'],
    zip_safe=True,
    maintainer='rgautham20',
    maintainer_email='ramkumar.g@northeastern.edu',
    description='ROS Driver for GNSS Puck',
    license='Apache-2.0',
    #tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'driver = gps_driver.driver:main',
        ],
    },
)

