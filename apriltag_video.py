#!/usr/bin/env python

from argparse import ArgumentParser
import os
import cv2
import apriltag
import numpy as np
import math
import time
from networktables import NetworkTables
from networktables.util import ntproperty
import logging

################################################################################

def apriltag_video(input_streams=[0], # '../media/input/single_tag.mp4', '../media/input/multiple_tags.mp4'], # For default cam use -> [0]
                   output_stream=False,
                   display_stream=False,
                   detection_window_name='AprilTag',
                  ):

    '''
    Detect AprilTags from video stream.

    Args:   input_streams [list(int/str)]: Camera index or movie name to run detection algorithm on
            output_stream [bool]: Boolean flag to save/not stream annotated with detections
            display_stream [bool]: Boolean flag to display/not stream annotated with detections
            detection_window_name [str]: Title of displayed (output) tag detection window
    '''

    parser = ArgumentParser(description='Detect AprilTags from video stream.')
    apriltag.add_arguments(parser)
    options = parser.parse_args()

    '''
    Set up a reasonable search path for the apriltag DLL.
    Either install the DLL in the appropriate system-wide
    location, or specify your own search paths as needed.
    '''

    detector = apriltag.Detector(options, searchpath=apriltag._get_dll_path())

    logging.basicConfig(level=logging.DEBUG)

    NetworkTables.initialize(server="10.22.28.2")

    at_table = NetworkTables.getTable("AprilTag")

    missed_detections = 0

    for stream in input_streams:

        video = cv2.VideoCapture(stream)

        while(video.isOpened()):

            success, frame = video.read()
            if not success:
                break

            # From ROS2 Camera Calibration Tool
            # | fx  0 cx
            # |  0 fy cy
            # |  0  0  1

            # MS HD 3000 Webcam in blue electrical box
            # 622.27892, 622.97536, 333.70651, 211.43233
            # MS HD 3000 Webcam in black mount with white LED ring
            # 734.626748, 726.761294, 411.819409, 263.823832
            # Note: The calibration values from the blue box work better with the 
            # camera so we'll use those for now..

            result, overlay = apriltag.detect_tags(frame,
                                                   detector,
                                                   camera_params=(622.27892, 622.97536, 333.70651, 211.43233),
                                                   tag_size=0.1397,
                                                   vizualization=0,
                                                   verbose=0,
                                                   annotation=False
                                                  )

            if result:

                hamming_error = result[0].hamming
                decision_margin = result[0].decision_margin

                # See this link for tuning results and where the magic numbers below came from:
                # https://docs.photonvision.org/en/latest/docs/getting-started/pipeline-tuning/apriltag-tuning.html

                if ((hamming_error == 0) and (decision_margin > 30)):

                    missed_detections = 0

                    print('Tag ID: {}'.format(result[0].tag_id))
                    at_table.putNumber("Tag ID", result[0].tag_id)
                    tag_id_property = result[0].tag_id

                    r11 = result[1][0][0]
                    r21 = result[1][1][0]
                    r31 = result[1][2][0]
                    r32 = result[1][2][1]
                    r33 = result[1][2][2]

                    yaw = "{:.2f}".format(np.degrees(np.arctan2(r21, r11)))
                    pitch = "{:.2f}".format(np.degrees(np.arctan2(-r31, math.sqrt(r32**2 + r33**2))))
                    roll = "{:.2f}".format(np.degrees(np.arctan2(r32, r33)))

                    #at_table.putNumber("Yaw", yaw)
                    at_table.putNumber("Pitch", pitch)
                    #at_table.putNumber("Roll", roll)

                    tx = "{:.4f}".format(result[1][0][3])
                    ty = "{:.4f}".format(result[1][1][3])
                    tz = "{:.4f}".format(result[1][2][3])

                    at_table.putNumber("TX", tx)
                    #at_table.putNumber("TY", ty)
                    at_table.putNumber("TZ", tz)

                    #print(result[0].tostring())

                    #print(f'TX: {tx} TY: {ty} TZ: {tz}')
                    #print(f'Yaw: {yaw} Pitch: {pitch} Roll: {roll}')
                    print(f'TZ: {tz} TX: {tx} Pitch: {pitch}')
                    print("============================================")

                #else:
                #    at_table.putNumber("Tag ID", 2228)

            else:
                at_table.putNumber("Tag ID", 2228)
                print("!!!!!!!!!!!!!!!No result returned !!!!!!!!!!!!!!!!!")

            if display_stream:
                cv2.imshow(detection_window_name, overlay)
                if cv2.waitKey(1) & 0xFF == ord(' '): # Press space bar to terminate
                    break

################################################################################

if __name__ == '__main__':
    apriltag_video()
