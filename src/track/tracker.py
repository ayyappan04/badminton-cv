import logging
import cv2
import numpy as np
from typing import List, Dict, Optional, Any
from ultralytics import YOLO
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.track")

class BadmintonTracker:
    def __init__(self, config: Optional[Dict] = None, model: Optional[YOLO] = None):
        """
        Initialize the BadmintonTracker.
        
        Args:
            config: Configuration dictionary.
            model: Optional existing YOLO model instance. If None, loads based on config.
        """
        self._config_config = config if config else get_config()
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        self.tracker_type = self.config.get('tracking.tracker_type', 'botsort')
        self.conf_threshold = self.config.get('detection.conf_threshold', 0.25)
        self.classes = self.config.get('detection.classes', [0])
        self.persist = True # vital for tracking
        
        if model:
            self.model = model
            logger.info("Using provided YOLO model for tracking.")
        else:
            model_path = self.config.get('detection.model_path', 'yolov8s.pt')
            logger.info(f"Loading YOLOv8 model for tracking from {model_path}...")
            self.model = YOLO(model_path)

        # Configure tracker arguments
        # Only supported trackers: 'botsort' or 'bytetrack'
        # We can pass a yaml file or just the name. 
        # Ultralytics looks for {tracker_type}.yaml in its config dir.
        if self.tracker_type not in ['botsort', 'bytetrack']:
            logger.warning(f"Unknown tracker type {self.tracker_type}. Defaulting to botsort.")
            self.tracker_type = 'botsort'
            
        logger.info(f"Initialized BadmintonTracker with {self.tracker_type}")

    def update(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run tracking on a single frame.
        
        Args:
            frame: BGR image.
            
        Returns:
            List of track dicts with 'track_id', 'box', 'score', 'class_id'.
        """
        results = self.model.track(
            source=frame,
            persist=self.persist,
            tracker=f"{self.tracker_type}.yaml",
            conf=self.conf_threshold,
            classes=self.classes,
            verbose=False
        )
        
        return self._parse_results(results[0])

    def update_batch(self, frames: List[np.ndarray]) -> List[List[Dict[str, Any]]]:
        """
        Run tracking on a batch of frames.
        Note: Batch tracking with 'persist=True' must be sequential.
        """
        if not frames:
            return []
            
        results = self.model.track(
            source=frames,
            persist=self.persist,
            tracker=f"{self.tracker_type}.yaml",
            conf=self.conf_threshold,
            classes=self.classes,
            verbose=False,
            stream=False
        )
        
        batch_tracks = []
        for result in results:
            batch_tracks.append(self._parse_results(result))
            
        return batch_tracks

    def _parse_results(self, result) -> List[Dict[str, Any]]:
        tracks = []
        if not result.boxes:
            return tracks
            
        boxes = result.boxes
        
        # Check if we have track IDs (if tracking failed, id might be None)
        if boxes.id is None:
            return tracks

        for i, box in enumerate(boxes):
            # Extract track ID
            try:
                track_id = int(boxes.id[i])
            except TypeError:
                continue # No ID assigned
                
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            score = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.model.names[cls_id]
            
            tracks.append({
                'track_id': track_id,
                'box': [x1, y1, x2, y2],
                'score': score,
                'class_id': cls_id,
                'class_name': cls_name
            })
            
        return tracks
