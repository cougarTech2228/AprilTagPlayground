# AprilTagPlayground

The purpose of this repo is to do some experimenting with AprilTag detection running on the Raspberry Pi. The upcoming 2023 FIRST Robotics FRC season will start migrating away from reflective tape in favor of AprilTags. Currently, the plan is to use the 16h5 family of AprilTags.

This Raspberry Pi image will use the TinkerTwins library for AprilTag detection. More information on this library can be found here: https://github.com/Tinker-Twins/AprilTag

In addition to using the TinkerTwins AprilTag library, we need to communicate the tag detection across the robot's network using NetworkTables. The following library is used to pass the tag detections across the network: https://github.com/robotpy/pynetworktables

## SD Card Setup
- Imaged Ubuntu 22.04 LTS Server using Raspberry Pi imager
- Login credentials for the Pi are setup as follows. Username: ubuntu, Password: cougartech

## Additional Install Requirements

The following commands must be run to install everything needed to get the AprilTag detection up and running

- $sudo apt install net-tools
- $git clone https://github.com/Tinker-Twins/AprilTag.git
- $cd AprilTag
- $chmod u+x *.sh
- $sudo apt install cmake
- $sudo apt-get install build-essentials
- $./install.sh
- $sudo apt-get update
- $sudo apt-get upgrade
- $sudo reboot now

After the reboot has completed, login and ...

- $sudo apt install python3-pip
- $pip install opencv-python
- $sudo apt-get install libgl1

## Executing the AprilTag detection script manually

- $cd AprilTag
- $cd scripts
- $python3 apriltag_video.py

Note: If no tags are detected, a "No Results" message will be printed to the screen.

## File Modifications

- apriltag.py: changed default family tag to 16h5
- apriltag_video.py: changed to use USB camera by default, printing detection results and added AprilTag network table processing. Currently the 16h5 family tags generate a lot of false positives. Only printing debug and creating network table entries for those detections that have a "Hamming Error" equal to 0. There are a number of configurable parameters that we'll need to investigate. More information on these parameters can be found in this header file: https://github.com/Tinker-Twins/AprilTag/blob/main/src/apriltag.h

## Notes on OutlineViewer application

- Setup OutlineViewer in "Client Mode" with Team/IP = 2228
- Should see an AprilTag table with status values for tag id, pitch, tx, tz

## Get the Pi to wait for a network connection before completing boot

- In the /etc/netplan/...yaml file make sure that "optional" under eth0 is set to false

## Don't try to use NetworkTables until the network is available

- See more information here: https://robotpy.readthedocs.io/en/stable/guide/nt.html

## Need to execute the apriltag_video.py python scripts at startup

- Followed this tutorial: https://www.dexterindustries.com/howto/auto-run-python-programs-on-the-raspberry-pi/

