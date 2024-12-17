# MIT License

# Copyright (c) 2024 Zixing Jiang

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#################################################################################
#                                                                               #
#   ===========================================================                 #
#   This script is used to capture live ultrasound video frames                 #
#   ===========================================================                 #
#                                                                               #
#   Usage: see README.md for instructions                                       #
#                                                                               #
#   Author: Zixing Jiang (zixingjiang@outlook.com)                              #
#                                                                               #
#   Remarks:                                                                    #
#   Use YAML configuration files to customize the video capture settings.       #
#   You should avoid modifying this script unless you know what you are doing.  #
#                                                                               #
#################################################################################

import argparse
import yaml
import os
from datetime import datetime
import ipaddress
import struct
import platform
import cv2
import socket
import numpy as np


# This class is used to log messages with different levels of severity.
class Logger:

    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    def __init__(self) -> None:
        return None

    def error(self, message: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{self.RED}[{current_time}] [Error]\t{message}{self.RESET}")
        return None

    def warn(self, message: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{self.YELLOW}[{current_time}] [Warn]\t{message}{self.RESET}")
        return None

    def info(self, message: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{self.CYAN}[{current_time}] [Info]\t{message}{self.RESET}")
        return None

    def log(self, message: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] [Log]\t{message}")
        return None


# This class is used to parse parameters from a YAML configuration file.
class ParameterParser:

    default_config = {
        "video_capture": {
            "source": "recordings/bk5000.mp4",
            "width": 1024,
            "height": 768,
        },
        "video_recording": {"directory": "recordings", "fps": 60},
        "udp_communication": {
            "sender_ip": "127.0.0.1",
            "sender_port": 60511,
            "receiver_ip": "127.0.0.1",
            "receiver_port": 60522,
            "format": "2d",
        },
    }

    def __init__(self) -> None:
        self.logger = Logger()
        self.config = {}
        return None

    def parse(self, file_path) -> dict:
        self.config = self.__load_yaml(file_path)

        # Use default values if not specified in the YAML file
        for category, parameters in self.default_config.items():
            if category not in self.config:
                self.config[category] = {}
            for parameter, value in parameters.items():
                if self.config[category].get(parameter) is None:
                    self.config[category][parameter] = value
                    self.logger.warn(
                        f"Parameter [{category}][{parameter}] not found. Using default value: {value}"
                    )

        if self.__validate_parameters():
            self.logger.log(
                "The following configuration will be used to initialize the video capturer:"
            )
            self.logger.log("=================================================")
            self.__print_configuration(self.config)
            self.logger.log("=================================================")
            return self.config
        else:
            self.logger.log("Found invalid parameters in the configuration file.")
            self.logger.log("Abort.")
            raise ValueError("Invalid parameters in the configuration file.")

    def __load_yaml(self, file_path: str) -> dict:
        """
        Load YAML file from path.
        This private method should not be called externally.
        """
        if not file_path:
            self.logger.warn(
                "No configuration file specified. Using default configuration."
            )
            return {}
        self.logger.info(f"Loading configuration from '{file_path}'...")
        if not file_path.endswith((".yaml", ".yml")):
            self.logger.error(
                f"The file '{file_path}' does not have a valid YAML extension. Using default configuration."
            )
            return {}
        try:
            with open(file_path, "r") as file:
                self.logger.log(f"Configuration loaded successfully.")
                config = yaml.safe_load(file)
                if config is None:
                    self.logger.warn(
                        f"The file '{file_path}' is empty. Using default configuration."
                    )
                    return {}
                else:
                    return config
        except FileNotFoundError:
            self.logger.error(
                f"The file '{file_path}' does not exist. Using default configuration."
            )
            return {}
        except yaml.YAMLError as exc:
            self.logger.error(
                f"The file '{file_path}' is not a valid YAML file. Details: {exc}. Using default configuration."
            )
            return {}

    def __validate_parameters(self) -> bool:
        """
        Validate parameters in self.config.
        This private method should not be called externally.

        Returns:
        bool: True if all parameters are valid, false otherwise.
        """
        self.logger.info("Validating parameters in the configuration...")
        is_valid = True
        is_valid &= self.__is_parameter_int_or_str("video_capture", "source")
        is_valid &= self.__is_parameter_int("video_capture", "width")
        is_valid &= self.__is_parameter_int("video_capture", "height")
        is_valid &= self.__is_parameter_directory("video_recording", "directory")
        is_valid &= self.__is_parameter_int("video_recording", "fps")
        is_valid &= self.__is_parameter_ip("udp_communication", "sender_ip")
        is_valid &= self.__is_parameter_port("udp_communication", "sender_port")
        is_valid &= self.__is_parameter_ip("udp_communication", "receiver_ip")
        is_valid &= self.__is_parameter_port("udp_communication", "receiver_port")
        is_valid &= self.__is_parameter_format("udp_communication", "format")
        if is_valid:
            self.logger.log("All parameters are valid.")
        else:
            self.logger.error(
                "Some parameters are invalid. Please check the log for more information."
            )
        return is_valid

    def __is_parameter_int_or_str(self, category: str, parameter: str) -> bool:
        """
        Check if `self.config[category][parameter]` is an integer or a string.
        This private method should not be called externally.

        Returns:
        bool: True if the parameter is an integer or a string, false otherwise.
        """
        value = self.config[category][parameter]
        flag = isinstance(value, (int, str))
        if not flag:
            self.logger.error(
                f"Parameter [{category}][{parameter}] is invalid! It should be an integer or a string. "
                f"Current value: {value} (type: {type(value).__name__})"
            )
        else:
            self.logger.log(f"Parameter [{category}][{parameter}] is valid: {value}")
        return flag

    def __is_parameter_int(self, category: str, parameter: str) -> bool:
        """
        Check if `self.config[category][parameter]` is an integer.
        This private method should not be called externally.

        Returns:
        bool: True if the parameter is an integer, false otherwise.
        """
        value = self.config[category][parameter]
        flag = isinstance(value, (int, str))
        if not flag:
            self.logger.error(
                f"Parameter [{category}][{parameter}] is invalid! It should be an integer. "
                f"Current value: {value} (type: {type(value).__name__})"
            )
        else:
            self.logger.log(f"Parameter [{category}][{parameter}] is valid: {value}")
        return flag

    def __is_parameter_directory(self, category: str, parameter: str) -> bool:
        """
        Check if `self.config[category][parameter]` is a string representing a valid directory path.
        This private method should not be called externally.

        Returns:
        bool: True if the parameter is a valid folder path, false otherwise.
        """
        value = self.config[category][parameter]
        flag = True
        # Check for invalid characters
        if any(char in value for char in r'<>:"|?*'):
            flag = False
        # Check if the path is valid
        if not os.path.isabs(value) and not os.path.normpath(value):
            flag = False
        if not flag:
            self.logger.error(
                f"Parameter [{category}][{parameter}] is invalid! It should be a legal directory path (no special characters). "
                f"Current value: {value} (type: {type(value).__name__})"
            )
        else:
            self.logger.log(f"Parameter [{category}][{parameter}] is valid: {value}")
        return flag

    def __is_parameter_ip(self, category: str, parameter: str) -> bool:
        """
        Check if `self.config[category][parameter]` is a string representing a valid IPV4 IP.
        This private method should not be called externally.

        Returns:
        bool: True if the parameter is a valid IPV4 IP, false otherwise.
        """
        value = self.config[category][parameter]
        try:
            ipaddress.IPv4Address(value)
            self.logger.log(f"Parameter [{category}][{parameter}] is valid: {value}")
            return True
        except ipaddress.AddressValueError:
            self.logger.error(
                f"Parameter [{category}][{parameter}] is invalid! It should be a legal IPV4 address. "
                f"Current value: {value} (type: {type(value).__name__})"
            )
            return False

    def __is_parameter_port(self, category: str, parameter: str) -> bool:
        """
        Check if `self.config[category][parameter]` is a int representing a valid port.
        This private method should not be called externally.

        Returns:
        bool: True if the parameter is a valid port, false otherwise.
        """
        value = self.config[category][parameter]
        flag = isinstance(value, int) and 0 <= value <= 65535
        if not flag:
            self.logger.error(
                f"Parameter [{category}][{parameter}] is invalid! It should be a legal port number (0-65535). "
                f"Current value: {value} (type: {type(value).__name__})"
            )
        else:
            self.logger.log(f"Parameter [{category}][{parameter}] is valid: {value}")
        return flag

    def __is_parameter_format(self, category: str, parameter: str) -> bool:
        """
        Check if `self.config[category][parameter]` is a string representing a valid struct packing format.
        This private method should not be called externally.

        Returns:
        bool: True if the parameter is a valid struct packing format, false otherwise.
        """
        value = self.config[category][parameter]
        try:
            struct.calcsize(value)
            self.logger.log(f"Parameter [{category}][{parameter}] is valid: {value}")
            return True
        except struct.error:
            self.logger.error(
                f"Parameter [{category}][{parameter}] is invalid! It should be a legal struct packing format. "
                f"Current value: {value} (type: {type(value).__name__}). "
                f"Please refer to Python documentation for more information: https://docs.python.org/3/library/struct.html#format-strings"
            )
            return False

    def __print_configuration(self, config: dict) -> None:
        """
        Print the configuration parameters.
        This private method should not be called externally.

        Parameters:
        config (dict): The configuration dictionary to print.
        """
        for category, parameters in config.items():
            self.logger.info(f"{category}:")
            for parameter, value in parameters.items():
                self.logger.info(f"\t{parameter}: {value}")
        return None


# This class is used to capture video frames from a source and process them.
class VideoCapturer:

    # State constants
    NORMAL = 0
    CALIBRATION = 1
    TARGETING = 2

    # Color constants
    YELLOW = (0, 255, 255)
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    CYAN = (255, 255, 0)
    BLACK = (0, 0, 0)

    # Image direction constants
    TOP_DOWN = 1
    BOTTOM_UP = -1

    def __init__(self, config: dict) -> None:
        self.logger = Logger()

        self.logger.info("Initializing video capturer...")

        # parameters specified in the configuration
        self.video_capture_source = config["video_capture"]["source"]
        self.video_capture_width = config["video_capture"]["width"]
        self.video_capture_height = config["video_capture"]["height"]
        self.video_recording_directory = config["video_recording"]["directory"]
        self.video_recording_fps = config["video_recording"]["fps"]
        self.udp_sender_ip = config["udp_communication"]["sender_ip"]
        self.udp_sender_port = config["udp_communication"]["sender_port"]
        self.udp_receiver_ip = config["udp_communication"]["receiver_ip"]
        self.udp_receiver_port = config["udp_communication"]["receiver_port"]
        self.udp_format = config["udp_communication"]["format"]

        # instance variables for video capturing
        self.using_video_file = (
            True if type(self.video_capture_source) is str else False
        )
        if self.using_video_file:
            self.video_capture = cv2.VideoCapture(self.video_capture_source)
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_capture_width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_capture_height)
            self.video_playback_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.logger.info(f"Opening video file {self.video_capture_source}...")
        else:
            if platform.system() == "Windows":
                self.video_capture = cv2.VideoCapture(
                    self.video_capture_source, cv2.CAP_DSHOW
                )
            elif platform.system() == "Linux":
                video_source = "/dev/video" + str(self.video_capture_source)
                self.video_capture = cv2.VideoCapture(video_source, cv2.CAP_V4L2)
            else:
                self.logger.error("Unsupported platform.")
                raise NotImplementedError("Unsupported platform.")
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_capture_width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_capture_height)
            self.logger.info(f"Opening camera {self.video_capture_source}...")
        self.frame = None

        # instance variables for video recording
        self.is_video_recording = False
        self.video_writer = None

        # instance variables for calibration
        self.is_calibrated = False
        self.points_for_calibration = []
        self.pixel_to_mm_ratio = None
        self.frame_origin = (
            int(0.5 * self.video_capture_width),
            int(0.5 * self.video_capture_height),
        )
        self.image_direction = self.TOP_DOWN

        # instance variables for targeting
        self.targets = []

        # variables for UDP communication
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.udp_sender_ip, self.udp_sender_port))
        self.udp_sent_targets = []  # list of targets sent to the receiver

        # instance variables for state transitions
        self.state = self.NORMAL

        # instance variables for annotations
        self.hide_annotations = False

        # instance variables for mouse events
        self.mouse_position = None

        self.logger.log("Video capturer initialized.")

        return None

    def capture(self) -> None:
        """
        Capture frames from the video source and process them.
        """

        if not self.video_capture.isOpened():
            self.logger.error(
                "Unable to open video source, please check your video capture setup!"
            )
            raise ValueError("Unable to open video source.")

        if platform.system() == "Windows":
            cv2.namedWindow("Live Ultrasound Video Capture")
        else:
            cv2.namedWindow("Live Ultrasound Video Capture", cv2.WINDOW_GUI_NORMAL)
        cv2.setMouseCallback("Live Ultrasound Video Capture", self.__mouse_callback)

        self.logger.log("=================================================")
        self.logger.info("Starting live ultrasound video capture")
        self.logger.info(
            "Press 'r' to start/stop recording, 'c' to toggle calibration mode, 't' to toggle targeting mode"
        )
        self.logger.info(
            "Press 'h' to hide/show annotations (not available in calibration and targeting modes)"
        )
        self.logger.info("Press 'q' to quit")
        self.logger.info(
            f"Recordings will be saved in the '{self.video_recording_directory}' folder"
        )
        self.logger.log("=================================================")

        while True:
            ret, self.frame = self.video_capture.read()
            if not ret:
                if self.using_video_file:
                    self.logger.log("End of video file. Restarting...")
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                self.logger.error("Failed to capture frame.")
                break

            if self.using_video_file and (
                self.frame.shape[1] != self.video_capture_width
                or self.frame.shape[0] != self.video_capture_height
            ):
                self.frame = cv2.resize(
                    self.frame, (self.video_capture_width, self.video_capture_height)
                )

            self.__draw_annotations()
            if self.is_video_recording and self.video_writer is not None:
                self.video_writer.write(self.frame)
                # draw a red circle to indicate recording (this is not saved in the video)
                cv2.circle(
                    self.frame, (self.video_capture_width - 30, 30), 10, self.RED, -1
                )
            cv2.imshow("Live Ultrasound Video Capture", self.frame)

            if self.using_video_file:
                key = (
                    cv2.waitKey(int(1000 / self.video_playback_fps)) & 0xFF
                )  # match video playback speed
            else:
                key = cv2.waitKey(1) & 0xFF
            if self.__handle_key(key):
                pass
            else:
                break

        # Release everything if job is finished
        self.video_capture.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
        self.udp_socket.close()
        return None

    def __mouse_callback(self, event, x, y, flags, param) -> None:
        """
        Handle mouse events.
        This private method should not be called externally.
        """
        self.mouse_position = (x, y)

        # mouse events available in calibration mode:
        # -------------------------------------------
        # 1. Left click: select a point for calibration
        # 2. Right click: select the frame origin
        # 3. Middle click (or ctrl + left click): lazy frame origin selection (assuming the origin is at the center-line of the frame)
        if self.state == self.CALIBRATION:

            # left click: select a point for calibration
            if event == cv2.EVENT_LBUTTONDOWN and not (flags & cv2.EVENT_FLAG_CTRLKEY):
                # clear the previous calibration points and start over
                if len(self.points_for_calibration) == 2:
                    self.points_for_calibration = []
                    self.is_calibrated = False
                    self.logger.log("Cleared previous calibration, starting over.")
                # select a new calibration point
                point = self.__find_nearest_white_pixel(self.mouse_position)
                self.points_for_calibration.append(point)
                self.logger.log(
                    f"Calibration point {len(self.points_for_calibration)} selected at ({point[0]}, {point[1]})"
                )
                # if two points are selected, perform calibration
                if len(self.points_for_calibration) == 2:
                    # calculate the pixel to mm ratio
                    self.pixel_to_mm_ratio = 10 / np.abs(
                        self.points_for_calibration[1][1]
                        - self.points_for_calibration[0][1]
                    )
                    self.logger.log(
                        f"Calculated pixel to mm ratio: {self.pixel_to_mm_ratio}"
                    )
                    # determine the image direction
                    determinant = 0.5 * (
                        self.points_for_calibration[1][1]
                        + self.points_for_calibration[0][1]
                    )
                    if determinant < self.frame_origin[1]:
                        self.image_direction = self.BOTTOM_UP
                        self.logger.log("Determined frame direction: bottom-up")
                    else:
                        self.image_direction = self.TOP_DOWN
                        self.logger.log("Determined frame direction: top-down")
                    self.is_calibrated = True

            # right click: select the frame origin
            if event == cv2.EVENT_RBUTTONDOWN:
                self.frame_origin = self.__find_nearest_white_pixel(self.mouse_position)
                self.logger.log(
                    f"Frame origin selected at ({self.frame_origin[0]}, {self.frame_origin[1]})"
                )
                # reset frame origin leads to recalibration
                self.is_calibrated = False
                self.points_for_calibration = []
                self.logger.log("Needs recalibration due to frame origin change.")

            # middle click: lazy frame origin selection
            if event == cv2.EVENT_MBUTTONDOWN or (
                event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY)
            ):
                self.frame_origin = (
                    int(0.5 * self.video_capture_width),
                    self.__find_nearest_white_pixel(self.mouse_position)[1],
                )
                self.logger.log(
                    f"Frame origin selected at ({self.frame_origin[0]}, {self.frame_origin[1]})"
                )
                # reset frame origin leads to recalibration
                self.is_calibrated = False
                self.points_for_calibration = []
                self.logger.log("Needs recalibration due to frame origin change.")

        # mouse events available in targeting mode:
        # -----------------------------------------
        # 1. Left click: select a target
        # 2. Right click: remove a target
        # 3. Middle click (or ctrl + left click): send a selected target to the receiver
        elif self.state == self.TARGETING:

            # left click: select a target
            if event == cv2.EVENT_LBUTTONDOWN and not (flags & cv2.EVENT_FLAG_CTRLKEY):
                target = self.mouse_position
                self.targets.append(target)
                target_mm = self.__pixel_coordinates_to_mm_coordinates(target)
                self.logger.log(f"Target selected at ({target_mm[0]}, {target_mm[1]})")

            # right click: remove a target
            if event == cv2.EVENT_RBUTTONDOWN:
                if not self.targets:
                    self.logger.warn("No targets to remove.")
                    return None
                target_to_remove = self.__find_closest_target(self.mouse_position)
                self.targets.remove(target_to_remove)
                target_to_remove_mm = self.__pixel_coordinates_to_mm_coordinates(
                    target_to_remove
                )
                self.logger.log(
                    f"Target removed at ({target_to_remove_mm[0]}, {target_to_remove_mm[1]})"
                )

            # middle click: send a selected target to the receiver
            if event == cv2.EVENT_MBUTTONDOWN or (
                event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY)
            ):
                if not self.targets:
                    self.logger.warn("No targets to send.")
                    return None
                target_to_send = self.__find_closest_target(self.mouse_position)
                self.__udp_send_target(target_to_send)
                self.targets.remove(target_to_send)

        # no mouse events available in normal mode
        else:
            pass
        return None

    def __handle_key(self, key) -> bool:
        """
        Handle key presses.
        This private method should not be called externally.

        Returns:
        bool: True if the program should continue, false if it should exit.
        """
        should_continue = True

        # toggle recording
        if key == ord("r" or "R"):
            if not self.is_video_recording:
                self.is_video_recording = True
                start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                if not os.path.exists(self.video_recording_directory):
                    os.makedirs(self.video_recording_directory)
                file_name = (
                    self.video_recording_directory
                    + "/"
                    + start_time.replace(":", "_")
                    + ".mp4"
                )
                self.video_writer = cv2.VideoWriter(
                    file_name,
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    self.video_recording_fps,
                    (self.video_capture_width, self.video_capture_height),
                )
                self.logger.info(f"Recording started. Saving to {file_name}")
            else:
                self.is_video_recording = False
                self.video_writer.release()
                self.video_writer = None
                self.logger.info("Recording stopped.")

        # toggle calibration mode
        elif key == ord("c" or "C"):
            if self.state == self.NORMAL:
                self.state = self.CALIBRATION
                self.logger.info("Entering calibration mode...")
            elif self.state == self.CALIBRATION:
                self.state = self.NORMAL
                self.logger.info("Exiting calibration mode...")
            else:
                self.logger.warn("Cannot enter calibration mode in targeting mode")

        # toggle targeting mode
        elif key == ord("t" or "T"):
            if self.is_calibrated:
                if self.state == self.NORMAL:
                    self.state = self.TARGETING
                    self.logger.info("Entering targeting mode...")
                elif self.state == self.TARGETING:
                    self.state = self.NORMAL
                    self.logger.info("Exiting targeting mode...")
                    # clear targets when exiting targeting mode
                    self.targets = []
                    self.udp_sent_targets = []
                else:
                    self.logger.warn("Cannot enter targeting mode in calibration mode")
            else:
                self.logger.warn("Cannot enter targeting mode without calibration")

        # hide/show annotations
        elif key == ord("h" or "H"):
            if self.state == self.NORMAL:
                if self.is_calibrated:
                    self.hide_annotations = not self.hide_annotations
                    if self.hide_annotations:
                        self.logger.info("Hiding annotations...")
                    else:
                        self.logger.info("Showing annotations...")
                else:
                    self.logger.warn("No annotations to hide/show")
            else:
                self.logger.warn(
                    "Cannot hide/show annotations in calibration and targeting modes"
                )

        # quit
        elif key == ord("q" or "Q"):
            should_continue = False
            self.logger.info("Quitting...")

        # other keys not handled
        else:
            pass
        return should_continue

    def __draw_annotations(self) -> None:
        """
        Draw annotations on the frame according to the current state.
        This private method should not be called externally
        """
        if self.is_calibrated and not self.hide_annotations:
            x1, y1 = self.points_for_calibration[0]
            x2, y2 = self.points_for_calibration[1]
            cv2.line(self.frame, (x1, y1), (x1, y2), self.YELLOW, 2)
            cv2.circle(self.frame, (x1, y1), 5, self.YELLOW, -1)
            cv2.circle(self.frame, (x1, y2), 5, self.YELLOW, -1)
            cv2.rectangle(
                self.frame,
                (self.video_capture_width - 200, 30),
                (self.video_capture_width - 30, 60),
                self.BLACK,
                -1,
            )
            cv2.putText(
                self.frame,
                f"10mm = {np.abs(y2 - y1)} pixels",
                (self.video_capture_width - 200, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.YELLOW,
                1,
            )
            cv2.circle(self.frame, self.frame_origin, 5, self.YELLOW, -1)
            cv2.putText(
                self.frame,
                f"Origin",
                (self.frame_origin[0] + 10, self.frame_origin[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.YELLOW,
                1,
            )

        if self.state == self.CALIBRATION:
            cv2.rectangle(self.frame, (5, 10), (700, 100), self.BLACK, -1)
            cv2.putText(
                self.frame,
                "Calibration mode: please select frame origin first and then two points for calibration",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.GREEN,
                1,
            )
            cv2.putText(
                self.frame,
                "Right click: select frame origin",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.GREEN,
                1,
            )
            cv2.putText(
                self.frame,
                "Left click: select calibration points. Please mark 10mm depth on the image",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.GREEN,
                1,
            )
            if not self.is_calibrated:
                cv2.circle(self.frame, self.frame_origin, 5, self.YELLOW, -1)
                cv2.putText(
                    self.frame,
                    f"Origin",
                    (self.frame_origin[0] + 10, self.frame_origin[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.YELLOW,
                    1,
                )
                cv2.putText(
                    self.frame,
                    f"Calibration not completed",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.YELLOW,
                    1,
                )
                for point in self.points_for_calibration:
                    cv2.circle(self.frame, point, 5, self.RED, -1)
            if self.mouse_position:
                x, y = self.mouse_position
                cv2.line(
                    self.frame, (x, 0), (x, self.video_capture_height), self.GREEN, 1
                )
                cv2.line(
                    self.frame, (0, y), (self.video_capture_width, y), self.GREEN, 1
                )
                cv2.putText(
                    self.frame,
                    f"({x}, {y})",
                    (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.GREEN,
                    1,
                )

        if self.state == self.TARGETING:
            cv2.rectangle(self.frame, (5, 10), (500, 80), self.BLACK, -1)
            cv2.putText(
                self.frame,
                "Targeting mode: please select targets",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.CYAN,
                1,
            )
            cv2.putText(
                self.frame,
                "Left click to select a target, right click to remove a target",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.CYAN,
                1,
            )
            cv2.putText(
                self.frame,
                "Middle click (or ctrl + left click) to send a selected target to the receiver",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.CYAN,
                1,
            )
            if self.mouse_position:
                x, y = self.mouse_position
                cv2.line(
                    self.frame, (x, 0), (x, self.video_capture_height), self.CYAN, 1
                )
                cv2.line(
                    self.frame, (0, y), (self.video_capture_width, y), self.CYAN, 1
                )
                mm_x, mm_y = self.__pixel_coordinates_to_mm_coordinates(
                    self.mouse_position
                )
                cv2.putText(
                    self.frame,
                    f"({mm_x:.3f} mm, {mm_y:.3f} mm)",
                    (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.CYAN,
                    1,
                )
            for target in self.targets:
                cv2.circle(self.frame, target, 5, self.RED, -1)
            for target in self.udp_sent_targets:
                cv2.circle(self.frame, target, 5, self.GREEN, -1)

        return None

    def __pixel_coordinates_to_mm_coordinates(self, pixel_point) -> tuple:
        """
        Convert pixel coordinates to mm coordinates using the calibration parameters.
        This private method should not be called externally.
        """
        pixel_x, pixel_y = pixel_point
        mm_x = (pixel_x - self.frame_origin[0]) * self.pixel_to_mm_ratio
        mm_y = (
            (pixel_y - self.frame_origin[1])
            * self.pixel_to_mm_ratio
            * self.image_direction
        )
        return (mm_x, mm_y)

    def __find_nearest_white_pixel(self, pixel_point) -> tuple:
        """
        Find the nearest white pixel in the frame to the given pixel point.
        If no white pixel is found in the search radius, return the same point.
        This private method should not be called externally.
        """
        search_radius = 50
        min_dist = float("inf")
        nearest_pixel = pixel_point
        for i in range(
            max(0, pixel_point[1] - search_radius),
            min(self.video_capture_height, pixel_point[1] + search_radius),
        ):
            for j in range(
                max(0, pixel_point[0] - search_radius),
                min(self.video_capture_width, pixel_point[0] + search_radius),
            ):
                if np.all(self.frame[i, j] == 255):
                    dist = (i - pixel_point[1]) ** 2 + (j - pixel_point[0]) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        nearest_pixel = (j, i)
        return nearest_pixel

    def __find_closest_target(self, pixel_point) -> tuple:
        """
        Find the closest target in self.targets to the given point (x, y).
        This private method should not be called externally.
        """
        x, y = pixel_point
        return min(
            self.targets, key=lambda target: (target[0] - x) ** 2 + (target[1] - y) ** 2
        )

    def __udp_send_target(self, target_point) -> None:
        """
        Send a selected target to the receiver using UDP.
        This private method should not be called externally.
        """
        mm_x, mm_y = self.__pixel_coordinates_to_mm_coordinates(target_point)
        packet = struct.pack(self.udp_format, mm_x, mm_y)
        self.udp_socket.sendto(packet, (self.udp_receiver_ip, self.udp_receiver_port))
        self.udp_sent_targets.append(target_point)
        self.logger.info(
            f"Target (x = {mm_x} mm, y = {mm_y} mm) sent to {self.udp_receiver_ip}:{self.udp_receiver_port}"
        )
        return None


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="This script captures live ultrasound video frames."
    )
    parser.add_argument(
        "yaml_file_path",
        type=str,
        nargs="?",
        default=None,
        help="Path to the YAML file that configures the video capturer.",
    )
    args = parser.parse_args()

    parameter_parser = ParameterParser()
    config = parameter_parser.parse(args.yaml_file_path)
    video_capturer = VideoCapturer(config)
    video_capturer.capture()
