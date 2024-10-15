#!/bin/bash

# example 1: capture live video from device 0
# --video_device 0 is usually the built-in camera of your laptop
# for other devices, you can use --video_device 1, --video_device 2, etc.
# python ./capture.py \
#     --capture_live_video \
#     --video_device 0 \
#     --self_ip 127.0.0.1 \
#     --self_port 60511 \
#     --robot_ip 127.0.0.1 \
#     --robot_port 60522 \
#     --video_origin_x 512 \
#     --video_origin_y 145

# example 2: replay video from a file
python ./capture.py \
    --video_file recording/video.mp4 \
    --self_ip 127.0.0.1 \
    --self_port 60511 \
    --robot_ip 127.0.0.1 \
    --robot_port 60522 \
    --video_origin_x 512 \
    --video_origin_y 145