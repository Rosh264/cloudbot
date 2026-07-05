import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'cloudbot_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # This line tells Colcon to include your launch files during the build
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='roshan',
    maintainer_email='Roshansharma9591@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'controller = cloudbot_core.controller_node:main',
            'teleop = cloudbot_core.teleop_node:main',
            'sensor = cloudbot_core.sensor_node:main',
        ],
    },
)