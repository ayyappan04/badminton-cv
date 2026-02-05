import sys
import os
import cv2
import requests
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'src'))

from track import BadmintonTracker
from utils import setup_logger

logger = setup_logger("verify_track")

def verify_tracking():
    logger.info("Starting tracking verification...")
    
    # 1. Download a short sample video (e.g., typical people walking sample or badminton if available)
    # We will fallback to creating a synthetic video with moving shapes if download fails or for speed.
    video_path = "data/test/tracking_test.mp4"
    if not os.path.exists(video_path):
        logger.info("Creating synthetic video for tracking...")
        create_moving_shapes_video(video_path)
        
    tracker = BadmintonTracker()
    
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    out_path = "outputs/verify_track_result.mp4"
    os.makedirs("outputs", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        tracks = tracker.update(frame)
        
        # Visualize
        for track in tracks:
            tid = track['track_id']
            box = track['box']
            cls_name = track['class_name']
            
            x1, y1, x2, y2 = map(int, box)
            
            # Color based on ID
            np.random.seed(tid)
            color = np.random.randint(0, 255, size=3).tolist()
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID: {tid} {cls_name}", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        cv2.putText(frame, f"Frame: {frame_count}", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                   
        out.write(frame)
        frame_count += 1
        
        if frame_count % 30 == 0:
            logger.info(f"Processed {frame_count} frames...")
            
    cap.release()
    out.release()
    logger.info(f"Tracking verification complete. Video saved to {out_path}")

def create_moving_shapes_video(path):
    """Creates a video with a moving 'person' (rectangle) that YOLO might not detect,
    so we should actually try to use a real image sequence or accept that for this test,
    YOLO might not detect anything if we don't put a real person.
    
    Wait, YOLO is trained on COCO. If I put a photo of a person moving across a background, it should work.
    """
    # Better approach: Download a known sample video.
    url = "https://github.com/intel-iot-devkit/sample-videos/raw/master/people-detection.mp4"
    try:
        logger.info(f"Downloading sample video from {url}...")
        resp = requests.get(url, stream=True, timeout=30)
        with open(path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024*1024):
                if chunk: f.write(chunk)
        logger.info("Download complete.")
    except Exception as e:
        logger.warning(f"Download failed: {e}. Falling back to dummy video (which might not trigger detections).")
        # Dummy fallback logic...
        # Just copy the dummy match we made earlier if it exists
        dummy_match = "data/test/dummy_match.mp4"
        if os.path.exists(dummy_match):
            import shutil
            shutil.copy(dummy_match, path)

if __name__ == "__main__":
    verify_tracking()
