# A simple python script for capturing live ultrasound video 

This repository contains a simple python script, [capture.py](https://github.com/zixingjiang/py-us-video-capture/blob/main/capture.py), for capturing live ultrasound video from clinical ultrasound equipment using a [video capture card](https://www.amazon.com/UGREEN-Recording-Streaming-Teaching-Conference/dp/B0BGMYPBF4/ref=asc_df_B0BGMYPBF4/?tag=hkgoshpadde-20&linkCode=df0&hvadid=680049709844&hvpos=&hvnetw=g&hvrand=2027351292518295012&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9191495&hvtargid=pla-1943464770846&psc=1&language=en_US&mcid=6c4da96552333c2cb6d45d0a261ab674). It is part of the code for robot-assisted ultrasound projects at the [Advanced Bio-Medical Robotics Lab](https://research.surgery.cuhk.edu.hk/lizhengrobotics/), The Chinese University of Hong Kong.

 

**Features**: This script provides the following features:
- Capture live ultrasound video
- Ultrasound video recording and replay (low recording quality issue notified)
- Manual calibration of the pixel-to-millimeter ratio based on image scales  
- Select targets and send them to the robot via UDP for further processing

**Compatibility**: This script is tested with [Wisonic Clover](https://www.wisonic.com/en/list_26/189.html) and [bk5000](https://www.bkmedical.com/systems/bk5000/). Theoretically, it can be used with any ultrasound machine or other device with video export function.

**Supported OS**: Tested on [Windows 11](https://www.microsoft.com/en-us/software-download/windows11) and [Ubuntu 24.04](https://ubuntu.com/download/desktop).

## Getting started 
1. Install [Python3](https://www.python.org/downloads/). Recommended version: 3.11. 
2. Clone this repository to your workspace
```
cd /path/to/your/workspace
git clone https://github.com/zixingjiang/py-us-video-capture.git
```
3. Install required packages:
```
pip install -r requirements.txt
```
1. Run the script. The following command launches the script with [default arguments](#default-values). For more command line arguments, see the [Command line arguments](#command-line-arguments) section. For more information on keyboard and mouse interaction with the script, please refer to the [user guide](https://github.com/zixingjiang/py-us-video-capture/blob/main/doc/user_guide.md).
```
python capture.py
```
## Command line arguments
All command line arguments are shown below
```
python capture.py -h
usage: capture.py [-h] [--capture_live_video | --no-capture_live_video] [--video_device VIDEO_DEVICE] [--video_file_path VIDEO_FILE_PATH] [--video_save_dir VIDEO_SAVE_DIR] [--video_save_fps VIDEO_SAVE_FPS]
                  [--video_width VIDEO_WIDTH] [--video_height VIDEO_HEIGHT] [--video_origin_x VIDEO_ORIGIN_X] [--video_origin_y VIDEO_ORIGIN_Y] [--self_ip SELF_IP] [--self_port SELF_PORT]
                  [--robot_ip ROBOT_IP] [--robot_port ROBOT_PORT]

A simple python script for ultrasound video capture

options:
  -h, --help            show this help message and exit
  --capture_live_video, --no-capture_live_video
                        Capture live video from the capture device. Otherwise, replay video from the video file
  --video_device VIDEO_DEVICE
                        Capture device index
  --video_file_path VIDEO_FILE_PATH
                        Path to the video file that will be replayed
  --video_save_dir VIDEO_SAVE_DIR
                        Directory to save the recording
  --video_save_fps VIDEO_SAVE_FPS
                        Frame per second of the saved video
  --video_width VIDEO_WIDTH
                        Width of the video in pixel
  --video_height VIDEO_HEIGHT
                        Height of the video in pixel
  --video_origin_x VIDEO_ORIGIN_X
                        X coordinate of the video origin in pixel
  --video_origin_y VIDEO_ORIGIN_Y
                        Y coordinate of the video origin in pixel
  --self_ip SELF_IP     Own IP address used to send UDP packets
  --self_port SELF_PORT
                        Own port number used to send UDP packets
  --robot_ip ROBOT_IP   Robot IP address to receive UDP packets
  --robot_port ROBOT_PORT
                        Robot port number to receive UDP packets
```

### Video source
- Set ```--capture_live_video``` to capture live video from the capture device. Otherwise, the script will replay video from the video file specified by ```--video_file_path```.
- Specify the capture device by ```--video_device```. On Windows OS, this script uses the [DirectShow](https://learn.microsoft.com/en-us/windows/win32/directshow/directshow) backend to capture video, which accepts a digit device index, such as 0, 1, 2, etc (usually 0 is the laptop's built-in camera). On Linux OS, this script uses the [V4L2](https://en.wikipedia.org/wiki/Video4Linux) backend to capture video, which accepts a device path, such as /dev/video0, /dev/video1, etc. **To be consistent with the Windows case, [this script already includes the device path prefix](https://github.com/zixingjiang/py-us-video-capture/blob/main/capture.py#L27), so you can directly use the device index, such as 0, 1, 2, here.**


### Frame origin
If you need to use the calibration and target selection functions, you need to specify the origin of the ultrasonic video frame. The origin may be different for different ultrasound devices. It is recommended that you capture a video first, then measure the pixel coordinates of the origin in the video and pass them to this script via ```--video_origin_x``` and ```--video_origin_y``` arguments.

### UDP communication
If you need to use UDP communication with the robot for target selection, you need to set the IP and port of the local machine (the device running the script) and the robot.
- ```--self_ip``` and ```--self_port``` specify the IP address and port number of the local machine.
- ```--robot_ip``` and ```--robot_port``` specify the IP address and port number of the robot.

### Default values
If you do not specify any command line arguments, the script will use the following default values:
| Argument | Default value |
| --- | --- |
| ```--capture_live_video``` |```--no-capture_live_video```|
| ```--video_device``` | 0 |
| ```--video_file_path``` | recording/video.mp4 |
| ```--video_save_dir``` | recording |
| ```--video_save_fps``` | 60 |
| ```--video_width``` | 1024 |
| ```--video_height``` | 768 |
| ```--video_origin_x``` | 512 |
| ```--video_origin_y``` | 145 |
| ```--self_ip``` | 127.0.0.1 |
| ```--self_port``` | 60511 |
| ```--robot_ip``` | 127.0.0.1 |
| ```--robot_port``` | 60522 |


### Quick launch
To avoid typing a long command line every time, you can create a shell script to launch the script with your preferred arguments. See [quick_launch.ps1](https://github.com/zixingjiang/py-us-video-capture/blob/main/quick_launch.ps1) for Windows Powershell and [quick_launch.bash](https://github.com/zixingjiang/py-us-video-capture/blob/main/quick_launch.bash) for Bash.


## Known issues
- The quality of the recorded video is lower than the original video stream.