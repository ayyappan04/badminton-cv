import logging
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.events")

class EventDetector:
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the EventDetector.
        """
        self._config_config = config if config else get_config()
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        self.min_rally_duration = self.config.get('events.min_rally_duration', 3.0)
        self.smash_thresh = self.config.get('events.smash_speed_threshold', 150.0)
        
        self.current_rally = []
        self.rallies = []
        
    def update(self, frame_data: Dict[str, Any]):
        """
        Process a single frame's data to detect events.
        
        Args:
            frame_data: Dict containing 'frame_idx', 'timestamp', 'shuttle_pos', 'shuttle_speed' (if avail)
        """
        # Simplistic rally detection: 
        # If shuttle is detected/moving, we are in a rally.
        # If no shuttle for N frames, rally ends.
        
        has_shuttle = frame_data.get('shuttle_pos') is not None
        
        if has_shuttle:
            self.current_rally.append(frame_data)
        else:
            if len(self.current_rally) > 0:
                # Rally might have ended. Check duration.
                start_time = self.current_rally[0]['timestamp']
                end_time = self.current_rally[-1]['timestamp']
                duration = end_time - start_time
                
                if duration >= self.min_rally_duration:
                    self.rallies.append({
                        'start_frame': self.current_rally[0]['frame_idx'],
                        'end_frame': self.current_rally[-1]['frame_idx'],
                        'duration': duration,
                        'shot_count': 0 # To be computed
                    })
                    logger.info(f"Rally detected: {duration:.2f}s")
                
                self.current_rally = []

    def classify_shot(self, shot_features: Dict[str, float]) -> str:
        """
        Classify a single shot based on features.
        
        Args:
            shot_features: Dict with 'max_speed', 'height', 'angle'.
        
        Returns:
            str: Shot type (Smash, Clear, Drop, Net, Serve, Drive)
        """
        speed = shot_features.get('max_speed', 0.0)
        height = shot_features.get('max_height', 0.0)
        angle = shot_features.get('angle', 0.0) # Angle of descent. +90 is vertical down.
        
        # Heuristics
        if speed > self.smash_thresh and angle > 10:
            return "Smash"
        elif height > 4.0: # High arc
            return "Clear" # or Lift
        elif speed < 80.0 and angle > 30:
            return "Drop"
        elif speed > 100.0 and abs(angle) < 10:
             return "Drive"
        else:
            return "Unclassified" # Net shot, etc.

