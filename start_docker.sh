#!/bin/sh

source start_db.sh

echo "Run Container"
xhost + local:root
docker run --name petra_central_control \
    -v $PWD:/home/ros2_ws/src/petra_central_control \
    --env-file .env \
    -it \
    --privileged \
    --net host \
    -e DISPLAY=$DISPLAY \
    --rm \
    petra_central_control/ros:foxy
