import sys
import os
import cv2
import requests
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'src'))

from detect import BadmintonDetector
from utils import setup_logger

logger = setup_logger("verify_detect")

def verify_detection():
    logger.info("Starting detection verification...")
    
    # Initialize detector
    try:
        detector = BadmintonDetector()
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        return

    # Download a sample image (using generic Zidane image often used for YOLO testing)
    # or just create a synthetic one if we want to be offline-safe.
    # Let's try to download first, fallback to synthetic.
    image_path = "data/test/test_image.jpg"
    os.makedirs("data/test", exist_ok=True)
    
    url = "https://ultralytics.com/images/zidane.jpg"
    if not os.path.exists(image_path):
        logger.info(f"Downloading sample image from {url}...")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(resp.content)
            else:
                 logger.warning("Failed to download image. Using synthetic.")
        except Exception as e:
             logger.warning(f"Failed to download image: {e}")

    if os.path.exists(image_path):
        frame = cv2.imread(image_path)
    else:
        # Synthetic image with a white square
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.rectangle(frame, (500, 200), (600, 500), (255, 255, 255), -1)
        logger.info("Using synthetic image.")

    # Run detection
    logger.info("Running detection...")
    detections = detector.detect_frame(frame)
    
    logger.info(f"Found {len(detections)} objects.")
    for det in detections:
        logger.info(f" - {det['class_name']} ({det['score']:.2f}): {det['box']}")
        
        # Draw box
        x1, y1, x2, y2 = map(int, det['box'])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"{det['class_name']} {det['score']:.2f}", (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Save output
    out_path = "outputs/verify_detect_result.jpg"
    os.makedirs("outputs", exist_ok=True)
    cv2.imwrite(out_path, frame)
    logger.info(f"Saved annotated image to {out_path}")

if __name__ == "__main__":
    verify_detection()
