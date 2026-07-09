import os
from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch_ros.actions import Node

map_yaml_file = os.path.join(
        get_package_prefix('petra_central_control'),
        '..',
        '..',
        'src',
        'petra_central_control',
        'ros',
        'maps',
        'aws_robomaker_hospital.yaml'
    )

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'yaml_filename': map_yaml_file}],
            arguments=['--ros-args', '--log-level', 'info']),
        Node(
            package='petra_central_control',
            executable='test_map',
            name='test_map',
            output='screen',
            emulate_tty=True
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            arguments=['--ros-args', '--log-level', 'info'],
            parameters=[{'autostart': True},
                        {'node_names': ['map_server']}])
    ])