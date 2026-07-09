##############################################################################
##                                 Base Image                               ##
##############################################################################
ARG ROS_DISTRO=foxy
FROM ros:$ROS_DISTRO-ros-base
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

##############################################################################
##                                 Global Dependecies                       ##
##############################################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    wget \
    ros-$ROS_DISTRO-navigation2 \
    ros-$ROS_DISTRO-tf-transformations \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install -U pip setuptools transforms3d

#############################################################################
##                                 Create User                             ##
#############################################################################
ARG USER=docker
ARG PASSWORD=docker
ARG UID=1000
ARG GID=1000
ENV UID=$UID
ENV GID=$GID
ENV USER=$USER
RUN groupadd -g "$GID" "$USER"  && \
    useradd -m -u "$UID" -g "$GID" --shell $(which bash) "$USER" -G sudo && \
    echo "$USER:$PASSWORD" | chpasswd && \
    echo "%sudo ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/sudogrp
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /etc/bash.bashrc

COPY ros/config/dds_profile.xml /home/$USER
RUN chown $USER:$USER /home/$USER/dds_profile.xml
ENV FASTRTPS_DEFAULT_PROFILES_FILE=/home/$USER/dds_profile.xml

USER root
RUN mkdir -p /home/$USER/ros2_ws/src

##############################################################################
# Wait for database to be available
##############################################################################

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

##############################################################################
##                                 User Dependecies                         ##
##############################################################################
WORKDIR /home/$USER/ros2_ws/src
RUN git config --global advice.detachedHead false
RUN git clone --depth 1 -b v1.3.1 https://project_55_bot:glpat-DjsyN_ixYnq-duDb_Sip@www.w.hs-karlsruhe.de/gitlab/iras/research-projects/petra/petra_interfaces.git

COPY ./requirements.txt ./petra_central_control/
RUN pip3 install -r petra_central_control/requirements.txt

ENV FLASK_APP=src/petra_central_control/flask_webserver/app.py
ENV FLASK_ENV=development
COPY ./ros ./petra_central_control/ros
COPY ./flask_webserver ./petra_central_control/flask_webserver
COPY ./split_url.sh .
RUN chmod +x split_url.sh 

##############################################################################
##                           Build ROS and run                              ##
##############################################################################
WORKDIR /home/$USER/ros2_ws
RUN . /opt/ros/$ROS_DISTRO/setup.sh && colcon build --symlink-install
RUN echo "source /home/$USER/ros2_ws/install/setup.bash" >> /home/$USER/.bashrc

RUN sudo sed --in-place --expression \
    '$i/wait' \
    /ros_entrypoint.sh

RUN sudo sed --in-place --expression \
    '$isource ./src/split_url.sh $FLASK_BACKEND_URL' \
    /ros_entrypoint.sh

RUN sudo sed --in-place --expression \
    '$iflask run -h $SPLIT_HOST -p $SPLIT_PORT &' \
    /ros_entrypoint.sh

RUN sudo sed --in-place --expression \
    '$isource ./install/setup.bash' \
    /ros_entrypoint.sh

RUN sudo sed --in-place --expression \
    '$ipython3 ./src/petra_central_control/flask_webserver/common/create_example_data.py' \
    /ros_entrypoint.sh

CMD ["ros2", "launch", "petra_central_control", "job_manager.launch.py"]
# CMD /bin/bash


