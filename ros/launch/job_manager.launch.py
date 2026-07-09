import os
from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    config = os.path.join(
        get_package_prefix('petra_central_control'),
        '..',
        '..',
        'src',
        'petra_central_control',
        'ros',
        'config',
        'params.yaml'
    )

    return LaunchDescription([
        Node(
            package='petra_central_control',
            executable='job_manager',
            name='job_manager',
            output='screen',
            emulate_tty=True,
            parameters=[config]
        ),
        Node(
            package='petra_central_control',
            executable='test_map',
            name='test_map',
            output='screen',
            emulate_tty=True
        ),
    ])
