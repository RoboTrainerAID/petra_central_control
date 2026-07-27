#!/bin/sh

IMAGE_NAME="petra_central_control_dev/ros:humble"

echo "Building development image..."
docker build -f Dockerfile.dev -t $IMAGE_NAME .