# A Python script for live ultrasound video capture

Almost all clinical ultrasound devices do not provide proprietary APIs for external programs to access the live ultrasound video stream. For devices that offer video signal outputs to external displays, a workaround for acquiring live video is to grab the output signal using a video capture card. This repository provides a single-script Python implementation of this approach: [`capture.py`](capture.py)

_This repository is a functional module for ultrasound robot projects from the [Advanced Bio-Medical Robotics Lab](https://research.surgery.cuhk.edu.hk/lizhengrobotics/) at the Chinese University of Hong Kong, released for educational purposes._

## Features
In addition to basic capture and display functionality, the Python script provides the following features:
- Record video to disk with a timestamped filename
- Replay the recorded video
- Manual calibration of frame origin and pixel-to-mm ratio
- Select targets on the image and send them to other programs via UDP

## Quick Start
The quickest way to get started is with a trial!
1. **Install [Python3](https://www.python.org/downloads/)**. Recommended version: 3.11
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3. **Run the script** (with [default parameters](#default-parameters))
   ```bash
   python capture.py
   ```
4. **Enjoy your first trail!** Follow the instructions in the terminal and on the screen to try out the features.

## Parameters
You can customize your video capture settings. To do so, write your YAML configuration file with referenced to [`parameters.yaml`](parameters.yaml) and pass it as an argument to the script:
```bash
# replace <your-yaml-file> with your configuration file
python capture.py <your-yaml-file>.yaml
```
If no configuration file is provided, or some parameters are not specified in the configuration file, the script will use their default values.

### Default Parameters
| Parameter | Default Value |
| --- | --- |
| `video_capture/source` | recordings/bk5000.mp4 |
| `video_capture/width` | 1024 |
| `video_capture/height` | 768 |
| `video_recording/directory` | recordings |
| `video_recording/fps` | 60 |
| `udp_communication/sender_ip` | 127.0.0.1 |
| `udp_communication/sender_port` | 60511 |
| `udp_communication/receiver_ip` | 127.0.0.1 |
| `udp_communication/sender_ip` | 60522 |
| `udp_communication/format` | 2d |

## Keyboard and Mouse Events
The script uses the following keyboard and mouse events:
### Keyboard Events
- `q` or `Q` - quit the program
- `r` or `R` - start/stop recording
- `c` or `C` - toggle calibration mode
- `t` or `T` - toggle targeting mode
- `h` or `H` - hide/show the annotation (not available in calibration and targeting modes)

### Mouse Events
**Normal mode**
 - no action
  
**Calibration mode**
- `left click` - select point for calibrate pixel-to-mm ratio
- `right click` - set the origin of the frame
- `middle click` or `ctrl + left click` - lazy frame origin selection (assume the origin is located in the horizontal center of the screen)

**Targeting mode**
- `left click` - select a target
- `right click` - remove a target
- `middle click` or `ctrl + left click` - send a target to the receiver 
  
## UDP Receiver
You may use [`udp_sample_receiver.py`](udp_sample_receiver.py) as a reference to unpack the UDP message sent by the script. 

## License
This repository falls under the [MIT License](LICENSE). 