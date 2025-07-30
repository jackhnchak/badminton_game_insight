import os
import cv2
import csv
import numpy as np
from ultralytics import YOLO
from .court_segmentation_detector import detect_court_mask


def intersect_lines(line1, line2):
    """
    Compute intersection point of two lines given as (x1,y1,x2,y2).
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    # Line1: A1 x + B1 y = C1
    A1 = y2 - y1
    B1 = x1 - x2
    C1 = A1 * x1 + B1 * y1
    # Line2: A2 x + B2 y = C2
    A2 = y4 - y3
    B2 = x3 - x4
    C2 = A2 * x3 + B2 * y3
    det = A1 * B2 - A2 * B1
    if abs(det) < 1e-6:
        return None  # parallel or nearly
    x = (B2 * C1 - B1 * C2) / det
    y = (A1 * C2 - A2 * C1) / det
    return [x, y]


def process_video(
    video_path: str,
    out_folder: str,
    model_path: str = "yolov8n.pt"
) -> str:
    """
    Full pipeline:
    1) Segment court lines on first frame.
    2) Hough-lines on mask, separate horizontals/verticals.
    3) Pick extreme lines and intersect to get corners.
    4) Compute homography.
    5) YOLOv8 detection+tracking, map centers via homography.
    6) Save CSV of (frame, track_id, x_meters, y_meters).
    """
    # Load YOLOv8 model
    model = YOLO(model_path)

    # Open video and read first frame
    cap = cv2.VideoCapture(video_path)
    ret0, frame0 = cap.read()
    if not ret0:
        cap.release()
        raise RuntimeError(f"Cannot read first frame from {video_path}")

    # 1. Predict court line mask
    mask = detect_court_mask(frame0)
    # 2. Edge detection on mask
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi/180, threshold=80,
        minLineLength=100, maxLineGap=5
    )
    if lines is None or len(lines) < 4:
        cap.release()
        raise RuntimeError("Unable to detect enough court lines for homography")

    # 3. Separate horizontal and vertical lines
    horiz_lines = []
    vert_lines = []
    for ln in lines[:, 0]:
        x1, y1, x2, y2 = ln
        angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        if angle < 20 or angle > 160:
            horiz_lines.append(ln.tolist())
        elif 70 < angle < 110:
            vert_lines.append(ln.tolist())

    # Require at least two of each
    if len(horiz_lines) < 2 or len(vert_lines) < 2:
        cap.release()
        raise RuntimeError("Not enough horizontal or vertical lines found")

    # Cluster by line midpoint to pick extremes
    ys = [((y1 + y2) / 2, ln) for ln in horiz_lines]
    xs = [((x1 + x2) / 2, ln) for ln in vert_lines]
    top_line = min(ys, key=lambda v: v[0])[1]
    bot_line = max(ys, key=lambda v: v[0])[1]
    left_line = min(xs, key=lambda v: v[0])[1]
    right_line = max(xs, key=lambda v: v[0])[1]

    # 4. Compute corner intersections
    tl = intersect_lines(top_line, left_line)
    tr = intersect_lines(top_line, right_line)
    br = intersect_lines(bot_line, right_line)
    bl = intersect_lines(bot_line, left_line)
    src_pts = np.array([tl, tr, br, bl], dtype=np.float32)
    dst_pts = np.array([[0, 0], [13.4, 0], [13.4, 6.1], [0, 6.1]], dtype=np.float32)

    # Homography
    H, _ = cv2.findHomography(src_pts, dst_pts)

    # Reset video
    cap.release()
    cap = cv2.VideoCapture(video_path)

    # 5. Process all frames with YOLO tracking
    results = []
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        tracked = model.track(source=frame, conf=0.3, verbose=False)[0]
        for box in tracked.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            track_id = int(box.id[0])
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            world_pt = cv2.perspectiveTransform(
                np.array([[[cx, cy]]], dtype=np.float32), H
            )[0][0]
            results.append((frame_idx, track_id, float(world_pt[0]), float(world_pt[1])))

    cap.release()

    # 6. Save to CSV
    os.makedirs(out_folder, exist_ok=True)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    out_csv = os.path.join(out_folder, f"{video_name}_tracks.csv")
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frame', 'track_id', 'x_meters', 'y_meters'])
        writer.writerows(results)

    return out_csv