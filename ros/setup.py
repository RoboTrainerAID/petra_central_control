import os
from glob import glob
from setuptools import setup

package_name = 'petra_central_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('lib', package_name, 'flask_webserver', "schemas"), glob('../flask_webserver/schemas/*.py')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andreas Zachariae',
    maintainer_email='andreas.zachariae@hs-karlsruhe.de',
    description='Job Manager for PeTRA transports',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'job_manager = petra_central_control.job_manager:main',
            'test_map = petra_central_control.test_map:main',
        ],
    },
)
