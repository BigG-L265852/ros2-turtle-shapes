"""Start turtlesim and draw a shape: ros2 launch turtle_shapes shapes.launch.py shape:=square"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    shape = LaunchConfiguration('shape')
    size = LaunchConfiguration('size')
    speed = LaunchConfiguration('speed')

    return LaunchDescription([
        DeclareLaunchArgument('shape', default_value='circle', description='circle | square | spiral'),
        DeclareLaunchArgument('size', default_value='2.0', description='radius / side length [m]'),
        DeclareLaunchArgument('speed', default_value='1.0', description='linear speed [m/s]'),
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),
        # give the turtlesim window a moment to come up
        TimerAction(period=1.5, actions=[
            Node(
                package='turtle_shapes',
                executable='shape_drawer',
                output='screen',
                parameters=[{'shape': shape, 'size': size, 'speed': speed}],
            ),
        ]),
    ])
