import sys
import cv2
import socket
import pickle
import struct
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer

import socket
import pickle
import struct
from threading import Thread

class VideoApp(QDialog):
    def __init__(self):
        super().__init__()

        # Load the UI
        loadUi('camera_1.ui', self)

        # Set window title
        self.setWindowTitle("Thermal and Live Camera")

        # Initialize live camera
        self.live_camera = cv2.VideoCapture(0)  # Replace with your live camera index or path

        # Thermal camera socket setup
        self.thermal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thermal_socket.connect(('172.28.42.196', 12345))  # Replace with the Linux server IP and port

        # Start a thread for receiving thermal frames
        self.thermal_thread = Thread(target=self.receive_thermal_frames, daemon=True)
        self.thermal_thread.start()

        # Set up a timer for live camera updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_frame)
        self.timer.start(30)  # Update every 30ms

    def update_live_frame(self):
        # Capture frame for the live camera
        ret_live, frame_live = self.live_camera.read()
        if ret_live:
            self.display_frame(frame_live, self.Live)

    def receive_thermal_frames(self):
        data = b""
        payload_size = struct.calcsize(">L")

        while True:
            # Receive frame size
            while len(data) < payload_size:
                data += self.thermal_socket.recv(4096)

            packed_size = data[:payload_size]
            data = data[payload_size:]
            frame_size = struct.unpack(">L", packed_size)[0]

            # Receive frame data
            while len(data) < frame_size:
                data += self.thermal_socket.recv(4096)

            frame_data = data[:frame_size]
            data = data[frame_size:]

            # Deserialize the frame
            frame = pickle.loads(frame_data)
            self.display_frame(frame, self.the)

    def display_frame(self, frame, label):
        # Convert frame from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to QImage
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Set the QLabel's pixmap
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap)
        label.setScaledContents(True)  # Ensure the video fits within the QLabel

    def closeEvent(self, event):
        # Release resources
        self.live_camera.release()
        self.thermal_socket.close()
        cv2.destroyAllWindows()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())



# class VideoApp(QDialog):
#     def __init__(self):
#         super().__init__()

#         # Load the UI
#         loadUi('camera_1.ui', self)

#         # Set window title
#         self.setWindowTitle("Thermal and Live Camera")

#         # Initialize socket for receiving video frames
#         self.server_ip = '172.28.42.196'  # Replace with your server's IP
#         self.server_port = 12345
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#         try:
#             self.client_socket.connect((self.server_ip, self.server_port))
#             print(f"Connected to server {self.server_ip}:{self.server_port}")
#         except ConnectionError as e:
#             print(f"Could not connect to server: {e}")
#             sys.exit()

#         # Set up timer for periodic frame updates
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.receive_and_display_frames)
#         self.timer.start(30)  # Update every 30ms

#     def receive_and_display_frames(self):
#         try:
#             # Receive frame size
#             data = b""
#             payload_size = struct.calcsize("Q")  # Size of packed frame size
#             while len(data) < payload_size:
#                 packet = self.client_socket.recv(4 * 1024)  # Receive in chunks
#                 if not packet:
#                     return
#                 data += packet

#             packed_msg_size = data[:payload_size]
#             data = data[payload_size:]
#             msg_size = struct.unpack("Q", packed_msg_size)[0]

#             # Receive the actual frame
#             while len(data) < msg_size:
#                 data += self.client_socket.recv(4 * 1024)

#             frame_data = data[:msg_size]
#             data = data[msg_size:]

#             # Deserialize frame
#             frame = pickle.loads(frame_data)

#             # Display frame in QLabel
#             self.display_frame(frame, self.Live)

#         except Exception as e:
#             print(f"Error receiving frame: {e}")
#             self.client_socket.close()
#             sys.exit()

#     def display_frame(self, frame, label):
#         # Convert frame from BGR to RGB
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Convert to QImage
#         h, w, ch = frame_rgb.shape
#         bytes_per_line = ch * w
#         qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

#         # Set the QLabel's pixmap
#         pixmap = QPixmap.fromImage(qimage)
#         label.setPixmap(pixmap)
#         label.setScaledContents(True)  # Ensure the video fits within the QLabel

#     def closeEvent(self, event):
#         # Close socket connection on close
#         self.client_socket.close()
#         super().closeEvent(event)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = VideoApp()
#     window.show()
#     sys.exit(app.exec_())
