import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from src.utils.config import get_config
from src.calibrate import CourtCalibrator

logger = logging.getLogger("badminton_cv.analytics")

class MetricsCalculator:
    def __init__(self, calibrator: CourtCalibrator, config: Optional[Dict] = None):
        """
        Initialize the MetricsCalculator.
        
        Args:
            calibrator: Instance of CourtCalibrator.
            config: Config dict.
        """
        self.calibrator = calibrator
        self._config_config = config if config else get_config()
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        self.fps = self.config.get('video.processing_fps', 30.0)
        
        # Player stats: {player_id: {'distance': 0.0, 'speed_samples': [], 'positions': []}}
        self.player_stats = {}
        self.shuttle_max_speed = 0.0

    def compute_shuttle_speed(self, p1_px: Tuple[float, float], p2_px: Tuple[float, float], time_delta: float) -> float:
        """
        Compute speed in km/h between two pixel points.
        
        Args:
            p1_px: Point 1 (x, y) pixels.
            p2_px: Point 2 (x, y) pixels.
            time_delta: Time in seconds.
            
        Returns:
            float: Speed in km/h.
        """
        if time_delta <= 0:
            return 0.0
            
        try:
            p1_m = self.calibrator.pixel_to_court(p1_px)
            p2_m = self.calibrator.pixel_to_court(p2_px)
        except RuntimeError:
             # Calibration not ready
             return 0.0
             
        dist_m = np.sqrt((p1_m[0] - p2_m[0])**2 + (p1_m[1] - p2_m[1])**2)
        speed_mps = dist_m / time_delta
        speed_kmh = speed_mps * 3.6
        
        if speed_kmh > self.shuttle_max_speed:
            self.shuttle_max_speed = speed_kmh
            
        return speed_kmh

    def update_player_stats(self, player_id: int, position_px: Tuple[float, float], frame_idx: int):
        """
        Update distance and coverage stats for a player.
        """
        if player_id not in self.player_stats:
            self.player_stats[player_id] = {
                'distance': 0.0,
                'positions': [], # Store court positions (x_m, y_m)
                'last_pos_px': None,
                'last_frame': None
            }
            
        stats = self.player_stats[player_id]
        
        # Convert to meters
        try:
            pos_m = self.calibrator.pixel_to_court(position_px)
        except RuntimeError:
            pos_m = (0.0, 0.0) # Fallback
            
        stats['positions'].append(pos_m)
        
        # Basic distance accumulation
        if stats['last_pos_px'] is not None:
            # We use meter distance for stats
            last_pos_m = self.calibrator.pixel_to_court(stats['last_pos_px'])
            dist = np.sqrt((pos_m[0] - last_pos_m[0])**2 + (pos_m[1] - last_pos_m[1])**2)
            
            # Simple noise filter: if moving > 10m in 1 frame (impossible), ignore
            if dist < 10.0:
                 stats['distance'] += dist
                 
        stats['last_pos_px'] = position_px
        stats['last_frame'] = frame_idx

    def get_summary(self) -> Dict[str, Any]:
        """Return match summary."""
        summary = {
            'shuttle_max_speed_kmh': self.shuttle_max_speed,
            'players': {}
        }
        
        for pid, stats in self.player_stats.items():
            summary['players'][pid] = {
                'total_distance_m': stats['distance'],
                'coverage_points': len(stats['positions'])
            }
            
        return summary
