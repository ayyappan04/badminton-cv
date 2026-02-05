import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'src'))

from calibrate import CourtCalibrator
from utils import setup_logger

logger = setup_logger("verify_calibrate")

def verify_calibration():
    logger.info("Starting calibration verification...")
    
    calibrator = CourtCalibrator()
    
    # simulate a simple perspective (identity-like for simplicity, or 
    # slightly warped to test robustness).
    # Let's say our image is 1280x720. 
    # We'll map the court to a central region.
    
    # Define "detected" pixel corners for a court centered in the image
    # Top-Left, Top-Right, Bottom-Right, Bottom-Left
    # Image coords: (x, y) with y=0 at top
    img_corners = np.array([
        [400, 200],   # TL (far away)
        [880, 200],   # TR (far away)
        [1000, 600],  # BR (close)
        [280, 600]    # BL (close)
    ], dtype=np.float32)
    
    logger.info(f"Simulated Image Corners: \n{img_corners}")
    
    # Compute Homography
    h_matrix = calibrator.compute_homography_from_points(img_corners)
    logger.info(f"Computed Homography Matrix: \n{h_matrix}")
    
    # Test valid points
    test_points = [
        (400, 200),  # Should map to (0, 13.4) - Top-Left
        (1000, 600), # Should map to (6.1, 0) - Bottom-Right
        (640, 400)   # Center-ish
    ]
    
    for pt in test_points:
        world_pt = calibrator.pixel_to_court(pt)
        logger.info(f"Pixel {pt} -> World {world_pt}")
        
    # Validation check
    tl_world = calibrator.pixel_to_court((400, 200))
    # Expect approx (0, 13.4)
    if abs(tl_world[0] - 0) < 0.1 and abs(tl_world[1] - 13.4) < 0.1:
         logger.info("SUCCESS: Top-Left mapped correctly.")
    else:
         logger.error(f"FAILURE: Top-Left mapping incorrect. Got {tl_world}")

if __name__ == "__main__":
    verify_calibration()
