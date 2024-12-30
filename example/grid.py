# Copyright (C) Meridian Innovation Ltd. Hong Kong, 2020. All rights reserved.
#
import sys
import os
import signal
import logging
import numpy as np
import cv2 as cv

try:
    from senxor.mi48 import MI48
    from senxor.utils import data_to_frame, remap, cv_filter,\
                             RollingAverageFilter, connect_senxor
except ImportError:
    print("Please ensure the 'senxor' library is correctly installed.")
    sys.exit(1)

# Enable logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

# Define signal handler for clean exit
def signal_handler(sig, frame):
    logger.info("Exiting due to SIGINT or SIGTERM")
    mi48.stop()
    cv.destroyAllWindows()
    logger.info("Done.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize the MI48 sensor
mi48, connected_port, port_names = connect_senxor()
logger.info('Camera info:')
logger.info(mi48.camera_info)

# Set desired FPS
STREAM_FPS = 15
mi48.set_fps(STREAM_FPS)

# Configure MI48 settings
mi48.disable_filter(f1=True, f2=True, f3=True)
mi48.set_filter_1(85)
mi48.enable_filter(f1=True, f2=False, f3=False, f3_ks_5=False)
mi48.set_offset_corr(0.0)
mi48.set_sens_factor(100)
mi48.get_sens_factor()

# Start continuous frame acquisition
mi48.start(stream=True, with_header=True)

# Enable GUI for rendering
GUI = True

# Set filter parameters
par = {'blur_ks': 3, 'd': 5, 'sigmaColor': 27, 'sigmaSpace': 27}
dminav = RollingAverageFilter(N=10)
dmaxav = RollingAverageFilter(N=10)

# Region definitions
GRID_ROWS, GRID_COLS = 3, 3

while True:
    data, header = mi48.read()
    if data is None:
        logger.critical('NONE data received instead of GFRA')
        mi48.stop()
        sys.exit(1)

    # Process frame data
    min_temp = dminav(data.min())
    max_temp = dmaxav(data.max())
    frame = data_to_frame(data, (80, 62), hflip=False)
    frame = np.clip(frame, min_temp, max_temp)
    filt_uint8 = cv_filter(remap(frame), par, use_median=True, use_bilat=True, use_nlm=False)

    # Calculate region-wise temperatures
    region_height, region_width = frame.shape[0] // GRID_ROWS, frame.shape[1] // GRID_COLS
    regions = [
        frame[:region_height, :region_width].mean(),        # Top-left (Front)
        frame[:region_height, -region_width:].mean(),       # Top-right (Back)
        frame[-region_height:, :region_width].mean(),       # Bottom-left (Left)
        frame[-region_height:, -region_width:].mean(),      # Bottom-right (Right)
        frame[region_height:-region_height, region_width:-region_width].mean(),  # Center
    ]
    avg_temp = np.mean(regions)

    # Print measured temperatures to the console
    print(f"Front: {regions[0]:.1f}°C, Back: {regions[1]:.1f}°C, "
          f"Left: {regions[2]:.1f}°C, Right: {regions[3]:.1f}°C, "
          f"Average: {avg_temp:.1f}°C")

    # Create display frame
    display_frame = cv.applyColorMap(filt_uint8, cv.COLORMAP_JET)
    enlarged_frame = cv.resize(display_frame, (900, 600), interpolation=cv.INTER_LINEAR)

    # Draw grid lines
    for i in range(1, GRID_ROWS):
        cv.line(enlarged_frame, (0, i * 200), (900, i * 200), (255, 255, 255), 1)
    for j in range(1, GRID_COLS):
        cv.line(enlarged_frame, (j * 300, 0), (j * 300, 600), (255, 255, 255), 1)

    # Overlay temperature values with text boxes
    positions = [
        (50, 50, f"Front: {regions[0]:.1f}°C"),
        (650, 50, f"Back: {regions[1]:.1f}°C"),
        (50, 550, f"Left: {regions[2]:.1f}°C"),
        (650, 550, f"Right: {regions[3]:.1f}°C"),
        (350, 300, f"Avg: {avg_temp:.1f}°C"),
    ]

    for x, y, text in positions:
        (text_width, text_height), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 1, 2)
        text_box_top_left = (x - 10, y - text_height - 10)
        text_box_bottom_right = (x + text_width + 10, y + 10)
        cv.rectangle(enlarged_frame, text_box_top_left, text_box_bottom_right, (0, 0, 0), -1)
        cv.putText(enlarged_frame, text, (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Render the frame
    if GUI:
        cv.imshow("Thermal Camera Output", enlarged_frame)
        if cv.waitKey(1) == ord("q"):
            break

# Stop capture and clean up
mi48.stop()
cv.destroyAllWindows()
