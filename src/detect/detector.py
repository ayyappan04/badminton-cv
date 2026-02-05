import logging
import cv2
import numpy as np
from typing import List, Dict, Optional, Any, Union
from ultralytics import YOLO
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.detect")

class BadmintonDetector:
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the BadmintonDetector with YOLOv8.
        """
        self._config_config = config if config else get_config()
        # Handle both ConfigLoader object and direct dict
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        # Load model parameters
        self.model_path = self.config.get('detection.model_path', 'yolov8s.pt')
        self.conf_threshold = self.config.get('detection.conf_threshold', 0.25)
        self.classes = self.config.get('detection.classes', [0]) # Default to person(0)
        
        logger.info(f"Loading YOLOv8 model from {self.model_path}...")
        try:
            self.model = YOLO(self.model_path)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def detect_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run detection on a single frame.
        
        Args:
            frame: BGR image array.
            
        Returns:
            List of dictionaries with keys: 'box', 'score', 'class_id', 'class_name'
        """
        # Run inference
        results = self.model.predict(
            source=frame, 
            conf=self.conf_threshold, 
            classes=self.classes,
            verbose=False
        )
        
        return self._parse_results(results[0])

    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Dict[str, Any]]]:
        """
        Run detection on a batch of frames.
        
        Args:
            frames: List of BGR image arrays.
            
        Returns:
            List of lists of detection dictionaries.
        """
        if not frames:
            return []
            
        # Ultralytics supports list of images
        results = self.model.predict(
            source=frames, 
            conf=self.conf_threshold, 
            classes=self.classes,
            verbose=False,
            stream=False 
        )
        
        batch_detections = []
        for result in results:
            batch_detections.append(self._parse_results(result))
            
        return batch_detections

    def _parse_results(self, result) -> List[Dict[str, Any]]:
        """Parse YOLO result object into structured list."""
        detections = []
        boxes = result.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            score = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.model.names[cls_id]
            
            detections.append({
                'box': [x1, y1, x2, y2],
                'score': score,
                'class_id': cls_id,
                'class_name': cls_name
            })
            
        return detections
