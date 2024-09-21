# User guide
If the script is successfully launched, you will see a window displaying the video and a log in the terminal.

![interface](interface.png)

## Video recording
Keeping the video window in focus, press the keyboard ```s``` key to start/stop video recording. By default, the recorded video is saved in the ```recording``` folder, and the video file name is the time you started recording. The following log in the terminal indicates successful recording:
```
Start recording at 2024-09-20_17:42:20
Recording stopped
End recording at 2024-09-20_17:42:24
Recording saved at recording/2024-09-20_17_42_20.mp4
```

## Calibration mode
Keeping the video window in focus, press the keyboard ```c``` key to enter/exit calibration mode. In this mode, your mouse will turn into a green crosshair. 

![calibration](calibration.png)

Click on the video window and select two points with a known vertical distance of 10 mm. The script will calculate the pixel distance between these two points and then calculate the pixel-to-millimeter ratio.

![pixel-to-mm](pixel-to-mm.png)

After calibration, there will be yellow dots and line segments marking the ultrasound frame origin and the pixel-to-millimeter ratio.

You can recalibrate by exiting and re-entering the calibration mode.

## Target selection mode
**Attention! Target selection mode can only be toggled after you done calibration.**

Keeping the video window in focus, press the keyboard ```t``` key to enter/exit target selection mode. In this mode, your mouse will turn into a cyan crosshair.

![target](target.png)

You can select or deselect targets by left/right clicking on the video window. The selected targets will be marked with red dots.
You can send selected targets to the robot via UDP by middle mouse click or ctrl+left click. Sent targets are marked with green dots. Targets are described by millimeter coordinates, which are calculated based on the manually calibrated pixel-to-millimeter ratio. 

You can clear all marker points in the current window by exiting and re-entering the target selection mode.

## UDP communication test
You can test the UDP communication using the provided ```udp_recv_test.py``` script. This script receives targets sent over UDP and print them on the terminal.

If the UDP communication is correctly set up, you will see the following logs in the terminal:

**The sender**
```
[2024-09-21 17:28:27] Sent target to robot ('127.0.0.1', 60522): (x = 8.838383838383837 mm, y = 3.686868686868687 mm)
[2024-09-21 17:28:27] Sent target to robot ('127.0.0.1', 60522): (x = 5.959595959595959 mm, y = 3.9393939393939394 mm)
[2024-09-21 17:28:27] Sent target to robot ('127.0.0.1', 60522): (x = 1.4646464646464645 mm, y = 3.4343434343434343 mm)
[2024-09-21 17:28:27] Sent target to robot ('127.0.0.1', 60522): (x = 0.5050505050505051 mm, y = 6.363636363636363 mm)
[2024-09-21 17:28:27] Sent target to robot ('127.0.0.1', 60522): (x = -3.5858585858585856 mm, y = 3.4343434343434343 mm)
[2024-09-21 17:28:27] Sent target to robot ('127.0.0.1', 60522): (x = -5.101010101010101 mm, y = 6.717171717171717 mm)
[2024-09-21 17:28:28] Sent target to robot ('127.0.0.1', 60522): (x = -8.484848484848484 mm, y = 3.282828282828283 mm)
[2024-09-21 17:28:28] Sent target to robot ('127.0.0.1', 60522): (x = -7.474747474747475 mm, y = 8.484848484848484 mm)
[2024-09-21 17:28:28] Sent target to robot ('127.0.0.1', 60522): (x = -1.4141414141414141 mm, y = 8.535353535353535 mm)
[2024-09-21 17:28:28] Sent target to robot ('127.0.0.1', 60522): (x = 2.727272727272727 mm, y = 12.02020202020202 mm)
[2024-09-21 17:28:28] Sent target to robot ('127.0.0.1', 60522): (x = 6.96969696969697 mm, y = 6.919191919191919 mm)
[2024-09-21 17:28:29] Sent target to robot ('127.0.0.1', 60522): (x = 4.494949494949495 mm, y = 14.646464646464647 mm)
[2024-09-21 17:28:29] Sent target to robot ('127.0.0.1', 60522): (x = -1.7171717171717171 mm, y = 12.070707070707071 mm)
[2024-09-21 17:28:29] Sent target to robot ('127.0.0.1', 60522): (x = -2.929292929292929 mm, y = 14.898989898989898 mm)
[2024-09-21 17:28:29] Sent target to robot ('127.0.0.1', 60522): (x = 3.080808080808081 mm, y = 17.727272727272727 mm)
[2024-09-21 17:28:29] Sent target to robot ('127.0.0.1', 60522): (x = 8.737373737373737 mm, y = 15.404040404040403 mm)
[2024-09-21 17:28:29] Sent target to robot ('127.0.0.1', 60522): (x = 8.98989898989899 mm, y = 18.383838383838384 mm)
[2024-09-21 17:28:30] Sent target to robot ('127.0.0.1', 60522): (x = 7.828282828282828 mm, y = 12.727272727272727 mm)
[2024-09-21 17:28:30] Sent target to robot ('127.0.0.1', 60522): (x = 0.0 mm, y = 18.535353535353536 mm)
[2024-09-21 17:28:30] Sent target to robot ('127.0.0.1', 60522): (x = -5.6060606060606055 mm, y = 19.09090909090909 mm)
```

**The receiver**
```
python udp_recv_test.py
Server listening on ('127.0.0.1', 60522)...
[2024-09-21 17:28:27] Received target from ('127.0.0.1', 60511): (x = 8.838383838383837 mm, y = 3.686868686868687 mm)
[2024-09-21 17:28:27] Received target from ('127.0.0.1', 60511): (x = 5.959595959595959 mm, y = 3.9393939393939394 mm)
[2024-09-21 17:28:27] Received target from ('127.0.0.1', 60511): (x = 1.4646464646464645 mm, y = 3.4343434343434343 mm)
[2024-09-21 17:28:27] Received target from ('127.0.0.1', 60511): (x = 0.5050505050505051 mm, y = 6.363636363636363 mm)
[2024-09-21 17:28:27] Received target from ('127.0.0.1', 60511): (x = -3.5858585858585856 mm, y = 3.4343434343434343 mm)
[2024-09-21 17:28:28] Received target from ('127.0.0.1', 60511): (x = -5.101010101010101 mm, y = 6.717171717171717 mm)
[2024-09-21 17:28:28] Received target from ('127.0.0.1', 60511): (x = -8.484848484848484 mm, y = 3.282828282828283 mm)
[2024-09-21 17:28:28] Received target from ('127.0.0.1', 60511): (x = -7.474747474747475 mm, y = 8.484848484848484 mm)
[2024-09-21 17:28:28] Received target from ('127.0.0.1', 60511): (x = -1.4141414141414141 mm, y = 8.535353535353535 mm)
[2024-09-21 17:28:28] Received target from ('127.0.0.1', 60511): (x = 2.727272727272727 mm, y = 12.02020202020202 mm)
[2024-09-21 17:28:28] Received target from ('127.0.0.1', 60511): (x = 6.96969696969697 mm, y = 6.919191919191919 mm)
[2024-09-21 17:28:29] Received target from ('127.0.0.1', 60511): (x = 4.494949494949495 mm, y = 14.646464646464647 mm)
[2024-09-21 17:28:29] Received target from ('127.0.0.1', 60511): (x = -1.7171717171717171 mm, y = 12.070707070707071 mm)
[2024-09-21 17:28:29] Received target from ('127.0.0.1', 60511): (x = -2.929292929292929 mm, y = 14.898989898989898 mm)
[2024-09-21 17:28:29] Received target from ('127.0.0.1', 60511): (x = 3.080808080808081 mm, y = 17.727272727272727 mm)
[2024-09-21 17:28:29] Received target from ('127.0.0.1', 60511): (x = 8.737373737373737 mm, y = 15.404040404040403 mm)
[2024-09-21 17:28:29] Received target from ('127.0.0.1', 60511): (x = 8.98989898989899 mm, y = 18.383838383838384 mm)
[2024-09-21 17:28:30] Received target from ('127.0.0.1', 60511): (x = 7.828282828282828 mm, y = 12.727272727272727 mm)
[2024-09-21 17:28:30] Received target from ('127.0.0.1', 60511): (x = 0.0 mm, y = 18.535353535353536 mm)
[2024-09-21 17:28:30] Received target from ('127.0.0.1', 60511): (x = -5.6060606060606055 mm, y = 19.09090909090909 mm)
```