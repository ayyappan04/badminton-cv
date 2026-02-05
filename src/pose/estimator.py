import logging
import cv2
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from ultralytics import YOLO
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.pose")

class PoseEstimator:
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the PoseEstimator with YOLOv8-pose.
        """
        self._config_config = config if config else get_config()
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        # Load pose model (can be different from detection model)
        # Defaulting to yolov8n-pose.pt for speed
        self.model_path = self.config.get('pose.model_path', 'yolov8n-pose.pt')
        self.conf_threshold = self.config.get('pose.conf_threshold', 0.5)
        
        logger.info(f"Loading YOLOv8-pose model from {self.model_path}...")
        try:
            self.model = YOLO(self.model_path)
            logger.info("Pose model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load pose model: {e}")
            raise

    def estimate(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run pose estimation on a single frame.
        
        Args:
            frame: BGR image.
            
        Returns:
            List of dicts: {'keypoints': np.array, 'box': ..., 'score': ...}
            Keypoints are (17, 3) array: [x, y, conf]
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            verbose=False
        )
        
        return self._parse_results(results[0])

    def _parse_results(self, result) -> List[Dict[str, Any]]:
        poses = []
        if not result.keypoints:
            return poses
            
        keypoints = result.keypoints
        boxes = result.boxes
        
        # Iterate through detected persons
        for i, kps in enumerate(keypoints):
            # kps.xy is (1, 17, 2), kps.conf is (1, 17)
            # data is (1, 17, 3) usually [x, y, conf] if available
            
            # Ultralytics API varies slightly by version, safely extraction:
            pts = kps.data[0].cpu().numpy() # shape (17, 3) -> x, y, conf
            
            box = boxes[i]
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            score = float(box.conf[0])
            
            poses.append({
                'keypoints': pts,
                'box': [x1, y1, x2, y2],
                'score': score
            })
            
        return poses

    def visualize(self, frame: np.ndarray, poses: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw skeletons on the frame.
        """
        vis_frame = frame.copy()
        
        # COCO 17 keypoints connections
        # Keypoint indices:
        # 0: Nose, 1: LEye, 2: REye, 3: LEar, 4: REar
        # 5: LShoulder, 6: RShoulder, 7: LElbow, 8: RElbow
        # 9: LWrist, 10: RWrist, 11: LHip, 12: RHip
        # 13: LKnee, 14: RKnee, 15: LAnkle, 16: RAnkle
        
        skeleton = [
            (5, 7), (7, 9),       # Left Arm
            (6, 8), (8, 10),      # Right Arm
            (5, 6),               # Shoulders
            (5, 11), (6, 12),     # Torso
            (11, 12),             # Hips
            (11, 13), (13, 15),   # Left Leg
            (12, 14), (14, 16)    # Right Leg
        ]
        
        for pose in poses:
            kps = pose['keypoints'] # (17, 3)
            
            # Draw points
            for i, (x, y, conf) in enumerate(kps):
                if conf > 0.5:
                    cv2.circle(vis_frame, (int(x), int(y)), 4, (0, 255, 0), -1)
            
            # Draw lines
            for i, j in skeleton:
                if kps[i][2] > 0.5 and kps[j][2] > 0.5:
                    pt1 = (int(kps[i][0]), int(kps[i][1]))
                    pt2 = (int(kps[j][0]), int(kps[j][1]))
                    cv2.line(vis_frame, pt1, pt2, (255, 0, 0), 2)
                    
        return vis_frame
