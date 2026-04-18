import cv2
import numpy as np
from pyorbbecsdk import OBFormat


def frame_to_bgr_image(frame):
    """Convert a color VideoFrame to a BGR uint8 numpy image."""
    try:
        width = frame.get_width()
        height = frame.get_height()
        fmt = frame.get_format()
        data = np.asanyarray(frame.get_data())
        if fmt == OBFormat.RGB:
            img = np.resize(data, (height, width, 3))
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif fmt == OBFormat.BGR:
            return np.resize(data, (height, width, 3))
        elif fmt == OBFormat.YUYV:
            img = np.resize(data, (height, width, 2))
            return cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUYV)
        elif fmt == OBFormat.UYVY:
            img = np.resize(data, (height, width, 2))
            return cv2.cvtColor(img, cv2.COLOR_YUV2BGR_UYVY)
        elif fmt == OBFormat.MJPG:
            return cv2.imdecode(data, cv2.IMREAD_COLOR)
        elif fmt == OBFormat.NV12:
            yuv = np.resize(data, (int(height * 1.5), width))
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
        elif fmt == OBFormat.NV21:
            yuv = np.resize(data, (int(height * 1.5), width))
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)
        else:
            print(f"[camera_utils] Unsupported color format: {fmt}")
            return None
    except Exception as e:
        print(f"[camera_utils] frame_to_bgr_image error: {e}")
        return None


def process_depth_frame(depth_frame, min_depth=20, max_depth=10000):
    """
    Convert depth frame to (colormap BGR, depth_data float32 mm).
    depth_data values are in millimetres; 0 means invalid/no-return.
    """
    if depth_frame is None:
        return None, None
    try:
        # Cast to DepthFrame to access depth-specific methods
        df = depth_frame.as_depth_frame() if hasattr(depth_frame, 'as_depth_frame') else depth_frame
        
        width = df.get_width()
        height = df.get_height()
        scale = df.get_depth_scale()

        depth_data = np.frombuffer(df.get_data(), dtype=np.uint16).reshape((height, width))
        depth_data = depth_data.astype(np.float32) * scale

        depth_data = np.where(
            (depth_data > min_depth) & (depth_data < max_depth),
            depth_data,
            0.0
        ).astype(np.float32)

        vis = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        depth_colormap = cv2.applyColorMap(vis, cv2.COLORMAP_JET)

        return depth_colormap, depth_data
    except Exception as e:
        print(f"[camera_utils] process_depth_frame error: {e}")
        return None, None


def process_ir_frame(ir_frame):
    """
    Convert an IR frame (Y8, Y16, MJPG …) to a BGR uint8 image.
    Must call as_video_frame() first to access width/height/format.
    Output is always uint8 BGR — compatible with MediaPipe and OpenCV.
    """
    if ir_frame is None:
        return None
    try:
        ir_frame = ir_frame.as_video_frame()
        width = ir_frame.get_width()
        height = ir_frame.get_height()
        ir_format = ir_frame.get_format()
        raw = ir_frame.get_data()

        if ir_format == OBFormat.Y8:
            gray = np.frombuffer(raw, dtype=np.uint8).reshape((height, width))
        elif ir_format == OBFormat.MJPG:
            decoded = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
            if decoded is None:
                return None
            gray = decoded
        else:
            gray_16 = np.frombuffer(raw, dtype=np.uint16).reshape((height, width))
            gray = cv2.normalize(gray_16, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    except Exception as e:
        print(f"[camera_utils] process_ir_frame error: {e}")
        return None


def process_color_frame(color_frame):
    """
    Convert Orbbec color VideoFrame to BGR uint8 image for MediaPipe.
    Handles RGB, BGR, MJPG formats from the Gemini 335 color sensor.
    """
    if color_frame is None:
        return None
    try:
        vf   = color_frame.as_video_frame()
        w, h = vf.get_width(), vf.get_height()
        fmt  = vf.get_format()
        raw  = np.frombuffer(vf.get_data(), dtype=np.uint8)

        if fmt == OBFormat.RGB:
            img = raw.reshape((h, w, 3))
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif fmt == OBFormat.BGR:
            return raw.reshape((h, w, 3))
        elif fmt == OBFormat.MJPG:
            return cv2.imdecode(raw, cv2.IMREAD_COLOR)
        elif fmt == OBFormat.YUYV:
            img = raw.reshape((h, w, 2))
            return cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUYV)
        else:
            return None
    except Exception as e:
        print(f"[camera_utils] process_color_frame error: {e}")
        return None


def get_depth_at_point(depth_data, x, y):
    """Return depth in mm at pixel (x, y). Returns 0.0 for out-of-bounds or invalid."""
    if depth_data is None:
        return 0.0
    h, w = depth_data.shape
    x, y = int(x), int(y)
    if 0 <= x < w and 0 <= y < h:
        return float(depth_data[y, x])
    return 0.0
