# A simple python script for live ultrasound video capture
# author: Zixing Jiang (zxjiang@surgery.cuhk.edu.hk)

import cv2         # for video frame processing
import datetime    # for timestamp
import os          # for file operations
import math        # for closest point calculation
import socket      # for UDP communication
import struct      # for packing data
import argparse    # for command line arguments
import platform    # for OS detection
import numpy as np # for array operations

class Capture():

    def __init__(self, args):
        self.own_address = (args.self_ip, args.self_port)
        self.robot_address = (args.robot_ip, args.robot_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(self.own_address)
        self.udp_sent_points = []

        self.capture_live_video = args.capture_live_video

        if platform.system() == 'Windows':
            self.video_device = args.video_device
        elif platform.system() == 'Linux':
            self.video_device = '/dev/video' + str(args.video_device)
        else:
            raise EnvironmentError("Unsupported OS")
        
        self.video_file_path = args.video_file_path
        self.video_width = args.video_width
        self.video_height = args.video_height
        self.video_save_fps = args.video_save_fps

        self.video_origin = (args.video_origin_x, args.video_origin_y)
        self.pixel_to_mm_ratio = 0.0

        self.capture = None
        self.replay_fps = None

        self.flag_recording = False
        self.video_writer = None
        self.recording_dir = args.video_save_dir
                
        self.flag_calibrated = False
        self.calibration_points = []

        self.state = None
        self.NORMAL = 0
        self.CALIBRATION = 1
        self.TARGET_SELECTION = 2

        self.current_mouse_position = None
        self.mouse_clicked_points = []
    
    def start_capture(self):

        YELLOW = (0, 255, 255)
        RED = (0, 0, 255)
        GREEN = (0, 255, 0)
        CYAN = (255, 255, 0)

        self.state = self.NORMAL

        if self.capture_live_video:
            if platform.system() == 'Windows':
                self.capture = cv2.VideoCapture(self.video_device, cv2.CAP_DSHOW)
            elif platform.system() == 'Linux':
                self.capture = cv2.VideoCapture(self.video_device, cv2.CAP_V4L2)
            else:
                raise EnvironmentError("Unsupported OS")
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
            print(f"Video source: video device {self.video_device}")
        else:
            self.capture = cv2.VideoCapture(self.video_file_path)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
            self.replay_fps = self.capture.get(cv2.CAP_PROP_FPS)
            print(f"Video source: video file {self.video_file_path}")

        # check video source
        if not self.capture.isOpened():
            print("Error: Unable to open video source, please check the video device index or video file path")
            return
        
        cv2.namedWindow('Ultrasound Video Capture', cv2.WINDOW_GUI_NORMAL)
        cv2.setMouseCallback('Ultrasound Video Capture', self.mouse_callback)

        print("Starting ultrasound video capture")
        print("Press 's' to start/stop recording, 'c' to toggle calibration mode, 't' to toggle target selection mode, 'q' to quit")
        print("Recording will be saved in the 'recording' folder")
        print("--------------------")

        while not self.capture_live_video or self.capture.isOpened():
            ret, frame = self.capture.read()

            # this is for pass current frame to self.find_nearest_white_pixel
            # which is used in self.mouse_callback （calibration mode）
            # it may be replaced with a better parameter passing method in the future
            self.current_frame = frame

            # if the video reaches the end, replay the video
            if not ret and not self.capture_live_video:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            '''Draw UI and display video frames'''

            # draw calibration line and origin
            if self.flag_calibrated:
                x1, y1 = self.calibration_points[0]
                _, y2 = self.calibration_points[1]
                cv2.line(frame, (x1, y1), (x1, y2), YELLOW, 2)
                cv2.putText(frame, f"10mm = {abs(y2 - y1)} pixels", (x1 + 10, (y1 + y2) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 1)
                cv2.circle(frame, self.video_origin, 5, YELLOW, -1)
                cv2.putText(frame, "Origin", (self.video_origin[0] + 10, self.video_origin[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 1)

            # UI for calibration point selection
            if self.state == self.CALIBRATION:
                cv2.putText(frame, "Calibration mode: please mark 10mm depth on the display", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 1)
                if self.current_mouse_position:
                    x, y = self.current_mouse_position
                    cv2.line(frame, (x, 0), (x, frame.shape[0]), GREEN, 1)
                    cv2.line(frame, (0, y), (frame.shape[1], y), GREEN, 1)
                    cv2.putText(frame, f"({x}, {y})", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 1)
                for point in self.mouse_clicked_points:
                    cv2.circle(frame, point, 5, RED, -1) 

            # UI for target selection
            if self.state == self.TARGET_SELECTION:
                cv2.putText(frame, "Target selection mode: please select targets for biopsy", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CYAN, 1)
                cv2.putText(frame, "Left click to select a target, right click to remove a target", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CYAN, 1)
                cv2.putText(frame, "Click the middle mouse button (or press ctrl + left click) to send the target to the robot", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CYAN, 1)
                if self.current_mouse_position:
                    x, y = self.current_mouse_position
                    x_mm = (x - self.video_origin[0]) * self.pixel_to_mm_ratio
                    y_mm = (y - self.video_origin[1]) * self.pixel_to_mm_ratio
                    cv2.line(frame, (x, 0), (x, frame.shape[0]), CYAN, 1)
                    cv2.line(frame, (0, y), (frame.shape[1], y), CYAN, 1)
                    cv2.putText(frame, f"({x_mm:.3f} mm, {y_mm:.3f} mm)", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CYAN, 1)
                for point in self.mouse_clicked_points:
                    cv2.circle(frame, point, 5, RED, -1)
                for point in self.udp_sent_points:
                    cv2.circle(frame, point, 5, GREEN, -1)
            
            cv2.imshow('Ultrasound Video Capture', frame)

            '''Handle keyboard inputs'''
            
            if not self.capture_live_video:
                key = cv2.waitKey(int(1000 / self.replay_fps)) & 0xFF
            else:
                key = cv2.waitKey(1) & 0xFF

            # press 's' to start/stop recording
            if key == ord('s' or 'S'):
                if not self.flag_recording:
                    self.flag_recording = True
                    start_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                    print(f"Start recording at {start_time}")
                    frame_height, frame_width = frame.shape[:2]
                    if not os.path.exists(self.recording_dir):
                        os.makedirs(self.recording_dir)
                    start_time_str = start_time.replace(":", "_")
                    filename = f"{self.recording_dir}/{start_time_str}.mp4" 
                    self.video_writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), self.video_save_fps, (frame_width, frame_height))
                else:
                    print("Recording stopped")
                    self.flag_recording = False
                    end_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                    print(f"End recording at {end_time}")
                    self.video_writer.release()
                    self.video_writer = None
                    print(f"Recording saved at {filename}")
                    print("--------------------")

            # press 'c' to toggle calibration mode
            elif key == ord('c' or 'C'):
                if self.state == self.NORMAL:
                    self.state = self.CALIBRATION
                    self.flag_calibrated = False
                    self.mouse_clicked_points = []
                    print(f"Calibration mode on")
                elif self.state == self.CALIBRATION:
                    self.state = self.NORMAL
                    if len(self.calibration_points) == 2:
                        self.flag_calibrated = True
                    print(f"Calibration mode off")
                else:
                    print("Cannot toggle calibration mode when in other modes")

            # press 't' to toggle target selection mode
            elif key == ord('t' or 'T'):
                if self.flag_calibrated:
                    if self.state == self.NORMAL:
                        self.state = self.TARGET_SELECTION
                        self.mouse_clicked_points = []
                        self.udp_sent_points = []
                        print(f"Target selection mode on")
                    elif self.state == self.TARGET_SELECTION:
                        self.state = self.NORMAL
                        print(f"Target selection mode off")
                    else:
                        print("Cannot toggle target selection mode when in other modes")
                else:
                    print("Cannot toggle target selection mode without calibration! Please calibrate first")

            # press 'q' to quit
            elif key == ord('q' or 'Q'):
                print("Quitting ultrasound video capture")
                break

            # save frame if recording is on
            if self.flag_recording and self.video_writer is not None:
                self.video_writer.write(frame)

        # Release everything if job is finished
        self.capture.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
        self.udp_socket.close()

    def mouse_callback(self, event, x, y, flags, param):
        self.current_mouse_position = (x, y)

        if event == cv2.EVENT_LBUTTONDOWN and self.state == self.CALIBRATION:
            nearest_x, nearest_y = self.find_nearest_white_pixel(x, y)
            self.mouse_clicked_points.append((nearest_x, nearest_y))
            print(f"Calibration point clicked at: ({nearest_x}, {nearest_y})")
            if len(self.mouse_clicked_points) == 2:
                self.pixel_to_mm_ratio = 10 / abs(self.mouse_clicked_points[1][1] - self.mouse_clicked_points[0][1])
                self.calibration_points = self.mouse_clicked_points.copy()
                self.mouse_clicked_points = []
                self.flag_calibrated = True
                _, y1 = self.calibration_points[0]
                _, y2 = self.calibration_points[1]
                self.pixel_to_mm_ratio = float(10 / abs(y2 - y1))
                print(f"Calibrated. Pixel to mm ratio: {self.pixel_to_mm_ratio}")
        
        elif event == cv2.EVENT_LBUTTONDOWN and not (flags & cv2.EVENT_FLAG_CTRLKEY) and self.state == self.TARGET_SELECTION:
            self.mouse_clicked_points.append((x,y))
            x_mm = (x - self.video_origin[0]) * self.pixel_to_mm_ratio
            y_mm = (y - self.video_origin[1]) * self.pixel_to_mm_ratio
            print(f"Selected target: (x = {x_mm} mm, y = {y_mm} mm)")

        elif event == cv2.EVENT_RBUTTONDOWN and self.state == self.TARGET_SELECTION:
            if self.mouse_clicked_points:
                point_to_remove = self.find_closest_point((x, y)) 
                self.mouse_clicked_points.remove(point_to_remove)
                x_mm = (x - self.video_origin[0]) * self.pixel_to_mm_ratio
                y_mm = (y - self.video_origin[1]) * self.pixel_to_mm_ratio
                print(f"Removed target: (x = {x_mm} mm, y = {y_mm} mm)")

        elif (event == cv2.EVENT_MBUTTONDOWN or (event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY))) and self.state == self.TARGET_SELECTION:
            if self.mouse_clicked_points:
                point_to_send = self.find_closest_point((x, y))               
                self.mouse_clicked_points.remove(point_to_send)
                self.udp_sent_points.append(point_to_send)
                x_mm = (point_to_send[0] - self.video_origin[0]) * self.pixel_to_mm_ratio
                y_mm = (point_to_send[1] - self.video_origin[1]) * self.pixel_to_mm_ratio
                self.udp_send((x_mm, y_mm))

    def find_nearest_white_pixel(self, x, y, search_radius=100):
        image = self.current_frame
        height, width = image.shape[:2]
        min_dist = float('inf')
        nearest_pixel = (x, y)
    
        for i in range(max(0, y - search_radius), min(height, y + search_radius)):
            for j in range(max(0, x - search_radius), min(width, x + search_radius)):
                if np.all(image[i, j] == 255):  # Check if the pixel is white
                    dist = (i - y) ** 2 + (j - x) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        nearest_pixel = (j, i)
    
        return nearest_pixel

    def find_closest_point(self, mouse_position):
        x, y = mouse_position
        return min(self.mouse_clicked_points, key=lambda point: math.hypot(point[0] - x, point[1] - y))

    def udp_send(self, point_mm):
        x, y = point_mm
        udp_packet = struct.pack('>2d', x, y)
        self.udp_socket.sendto(udp_packet, self.robot_address)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent target to robot {self.robot_address}: (x = {x} mm, y = {y} mm)")

if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='A simple python script for ultrasound video capture')
    parser.add_argument('--capture_live_video', action=argparse.BooleanOptionalAction, help='Capture live video from the capture device. Otherwise, replay video from the video file')
    parser.add_argument('--video_device', type=int, default=0, help='Capture device index')
    parser.add_argument('--video_file_path', type=str, default='recording/video.mp4', help='Path to the video file that will be replayed')
    parser.add_argument('--video_save_dir', type=str, default='recording', help='Directory to save the recording')
    parser.add_argument('--video_save_fps', type=int, default=60, help='Frame per second of the saved video')
    parser.add_argument('--video_width', type=int, default=1024, help='Width of the video in pixel')
    parser.add_argument('--video_height', type=int, default=768, help='Height of the video in pixel')
    parser.add_argument('--video_origin_x', type=int, default=512, help='X coordinate of the video origin in pixel')
    parser.add_argument('--video_origin_y', type=int, default=145, help='Y coordinate of the video origin in pixel')
    parser.add_argument('--self_ip', type=str, default='127.0.0.1', help='Own IP address used to send UDP packets')
    parser.add_argument('--self_port', type=int, default=60511, help='Own port number used to send UDP packets')
    parser.add_argument('--robot_ip', type=str, default='127.0.0.1', help='Robot IP address to receive UDP packets')
    parser.add_argument('--robot_port', type=int, default=60522, help='Robot port number to receive UDP packets')

    # Start the ultrasound video capture
    us_video_capture = Capture(parser.parse_args())
    us_video_capture.start_capture()
