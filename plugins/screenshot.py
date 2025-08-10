import pyautogui
import os
import time

def take_screenshot():
    """Take a screenshot and return file path."""
    timestamp = int(time.time())
    file_path = f"screenshot_{timestamp}.png"
    pyautogui.screenshot().save(file_path)
    return file_path

# New camera snapshot function

def take_camera_snapshot():
    try:
        import cv2
    except ImportError:
        return None, "OpenCV (cv2) is not installed."
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return None, "No camera detected."
    ret, frame = cam.read()
    if not ret:
        cam.release()
        return None, "Failed to capture image from camera."
    filename = "camera_snapshot.png"
    cv2.imwrite(filename, frame)
    cam.release()
    return filename, None

# New video clip functions

def record_camera_clip(duration=10):
    try:
        import cv2
    except ImportError:
        return None, "OpenCV (cv2) is not installed."
    duration = min(max(duration, 1), 30)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return None, "No camera detected."
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = "camera_clip.avi"
    fps = 20.0
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    import time
    start = time.time()
    while time.time() - start < duration:
        ret, frame = cam.read()
        if not ret:
            break
        out.write(frame)
    cam.release()
    out.release()
    if os.path.exists(filename):
        return filename, None
    else:
        return None, "Failed to record camera clip."

def record_screen_clip(duration=10):
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None, "OpenCV (cv2) and numpy are required."
    duration = min(max(duration, 1), 30)
    import time
    screen = pyautogui.screenshot()
    width, height = screen.size
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = "screen_clip.avi"
    fps = 10.0
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    start = time.time()
    while time.time() - start < duration:
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
    out.release()
    if os.path.exists(filename):
        return filename, None
    else:
        return None, "Failed to record screen clip."