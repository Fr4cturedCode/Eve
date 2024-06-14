import cv2
import time
import mss
import numpy as np


def video_capture(pathandname, screen, scale=0.5, duration=10):
    if screen == 'laptop':
        top, left, width, height = 0, 0, 2559, 1599
    if screen == 'monitor':
        top, left, width, height = 0, 0, 2559, 1599

    frame_width = round(width * scale)
    frame_height = round(height * scale)
    fps = 20.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vidwriter = cv2.VideoWriter(f'{pathandname}.avi', fourcc, fps, (frame_width, frame_height))

    start_time = time.time()
    with mss.mss() as sct:
        # Part of the screen to capture
        monitor = {"top": top, "left": left, "width": width, "height": height}

        while time.time() - start_time < duration:
            last_time = time.time()

            img = np.array(sct.grab(monitor))
            img = cv2.resize(img, (frame_width, frame_height))
            frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.putText(frame, "FPS: %f" % (1.0 / (time.time() - last_time)),
                        (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            vidwriter.write(frame)
    vidwriter.release()
    cv2.destroyAllWindows()
# video_capture('Alerts/Newsig', 'laptop', duration=2)