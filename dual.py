import sys
import cv2
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer

class DualCameraDemo(QDialog):
    def __init__(self):
        super().__init__()

        # Load the UI
        loadUi('camera_1.ui', self)

        # Set window title
        self.setWindowTitle("Camera View")

        # Initialize video capture (single webcam)
        self.camera = cv2.VideoCapture(0)

        # Set up a timer to update frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)  # Update every 30ms

    def update_frames(self):
        # Capture a frame from the camera
        ret, frame = self.camera.read()
        if ret:
            # Normal camera feed
            normal_frame = frame

            # Simulate thermal effect using a colormap
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            thermal_frame = cv2.applyColorMap(gray_frame, cv2.COLORMAP_JET)

            # Display the frames on the QLabel widgets
            self.display_frame(normal_frame, self.Live)  # QLabel for normal feed
            self.display_frame(thermal_frame, self.the)  # QLabel for thermal feed

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
        # Release video capture on close
        self.camera.release()
        cv2.destroyAllWindows()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DualCameraDemo()
    window.show()
    sys.exit(app.exec_())
