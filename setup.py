from glob import glob

from setuptools import find_packages, setup

package_name = 'turtle_shapes'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gijs van Lankvelt',
    maintainer_email='gijs.v.lankvelt@gmail.com',
    description='Level 1 ROS 2 beginner app: talker/listener and turtlesim shape drawing',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'talker = turtle_shapes.talker:main',
            'listener = turtle_shapes.listener:main',
            'shape_drawer = turtle_shapes.shape_drawer:main',
        ],
    },
)
