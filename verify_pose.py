import sys
import os
import cv2
import requests
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'src'))

from pose import PoseEstimator
from utils import setup_logger

logger = setup_logger("verify_pose")

def verify_pose():
    logger.info("Starting pose verification...")
    
    estimator = PoseEstimator()
    
    # Reuse the test image from Phase 3 or download if missing
    image_path = "data/test/test_image.jpg"
    if not os.path.exists(image_path):
        url = "https://ultralytics.com/images/zidane.jpg"
        try:
            resp = requests.get(url, timeout=10)
            with open(image_path, 'wb') as f:
                f.write(resp.content)
        except:
             logger.warning("Could not download image. Creating synthetic.")
             img = np.zeros((720, 1280, 3), dtype=np.uint8)
             cv2.rectangle(img, (500, 200), (600, 500), (255, 255, 255), -1) # Box
             cv2.imwrite(image_path, img)

    frame = cv2.imread(image_path)
    
    # Run inference
    poses = estimator.estimate(frame)
    logger.info(f"Detected {len(poses)} poses.")
    
    for i, pose in enumerate(poses):
        kps = pose['keypoints']
        # Count high-conf keypoints
        valid_kps = np.sum(kps[:, 2] > 0.5)
        logger.info(f"Pose {i}: {valid_kps}/17 keypoints detected. Score: {pose['score']:.2f}")

    # Visualize
    vis_frame = estimator.visualize(frame, poses)
    
    out_path = "outputs/verify_pose_result.jpg"
    os.makedirs("outputs", exist_ok=True)
    cv2.imwrite(out_path, vis_frame)
    logger.info(f"Saved annotated image to {out_path}")

if __name__ == "__main__":
    verify_pose()
