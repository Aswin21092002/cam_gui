import sys
import cv2
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer

class VideoApp(QDialog):
    def __init__(self):
        super().__init__()

        # Load the UI
        loadUi('camera_1.ui', self)

        # Set window title
        self.setWindowTitle("Thermal and Live Camera")

        # Initialize video capture for live and thermal cameras
        self.live_camera = cv2.VideoCapture(1)  # Replace with your live camera index or path
        self.thermal_camera = cv2.VideoCapture(0)  # Replace with your thermal camera index or path

        # Set up timers for periodic frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)  # Update every 30ms

    def update_frames(self):
        # Capture frame for live camera
        ret_live, frame_live = self.live_camera.read()
        if ret_live:
            self.display_frame(frame_live, self.Live)

        # Capture frame for thermal camera
        ret_thermal, frame_thermal = self.thermal_camera.read()
        if ret_thermal:
            # Process and display the thermal frame
            self.display_frame(frame_thermal, self.the)

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
        self.live_camera.release()
        self.thermal_camera.release()
        cv2.destroyAllWindows()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
