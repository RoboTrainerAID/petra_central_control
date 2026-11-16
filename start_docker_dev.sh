#!/bin/bash

source start_db.sh

IMAGE_NAME="petra_central_control_dev/ros:humble"

echo "Run Container (Dev Mode)"
xhost + local:root

# Detect Operating System
OS="$(uname -s)"

if [ "$OS" = "Linux" ]; then
    echo "Running on Linux (using --net host)..."
    docker run --name petra_central_control_dev \
        -v $PWD/flask_webserver:/home/docker/ros2_ws/src/petra_central_control/flask_webserver \
        -v $PWD/ros:/home/docker/ros2_ws/src/petra_central_control/ros \
        -v $PWD/data:/home/docker/data \
        --env-file .env \
        -it \
        --privileged \
        --net host \
        -e DISPLAY=$DISPLAY \
        --rm \
        $IMAGE_NAME
else
    echo "Running on macOS (using port mapping)..."
    docker run --name petra_central_control_dev \
        -v $PWD/flask_webserver:/home/docker/ros2_ws/src/petra_central_control/flask_webserver \
        -v $PWD/ros:/home/docker/ros2_ws/src/petra_central_control/ros \
        -v $PWD/data:/home/docker/data \
        --add-host=host.docker.internal:host-gateway \
        --env-file .env.macos \
        -it \
        --privileged \
        -p 5001:5000 \
        -e DISPLAY=$DISPLAY \
        --rm \
        $IMAGE_NAME
fi