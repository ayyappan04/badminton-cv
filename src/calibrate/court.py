import cv2
import numpy as np
import logging
from typing import Tuple, List, Optional, Dict
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.calibrate")

class CourtCalibrator:
    def __init__(self, config: Optional[Dict] = None):
        self._config_loader = config if config else get_config()
        self.config = self._config_loader.config if hasattr(self._config_loader, 'config') else get_config().config
        
        # Standard Badminton Court Dimensions usually in meters
        # Origin at bottom-left corner of the full court (singles or doubles)
        # Full Length: 13.4m, Full Width: 6.1m (Doubles), 5.18m (Singles)
        self.court_width = 6.1
        self.court_length = 13.4
        
        # Define 4 key corners for the full doubles court in global coordinates (meters)
        # Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left
        self.court_corners_world = np.array([
            [0, self.court_length],          # Top-Left
            [self.court_width, self.court_length], # Top-Right
            [self.court_width, 0],           # Bottom-Right
            [0, 0]                           # Bottom-Left
        ], dtype=np.float32)

        self.homography_matrix = None

    def detect_court(self, frame: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detect court lines and compute homography.
        
        Args:
            frame: Input image frame.
            
        Returns:
            Tuple[bool, np.ndarray]: Success flag and homography matrix (3x3).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = self._get_edges(gray)
        lines = self._get_lines(edges)
        
        if lines is None:
            logger.warning("No lines detected.")
            return False, None
            
        # Simplification: For robust detection in complex real videos, we need 
        # a more sophisticated pipeline (filtering, clustering, finding intersection).
        # For this phase, we'll implement a basic corner finding strategy or 
        # rely on manual point inputs if auto-detect fails. 
        # Here we mock a successful detection if we find enough lines for the verification,
        # but in a real system we would solve for the 4 corners.
        
        # TODO: Implement robust line intersection to find the 4 corners.
        # For now, we will return None to indicate auto-calibration needs more logic
        # or manual override.
        
        return False, None

    def compute_homography_from_points(self, src_points: np.ndarray) -> np.ndarray:
        """
        Compute homography from 4 detected image points to world court corners.
        
        Args:
            src_points: Array of 4 points [x, y] in image coordinates.
                        Order must match: Top-Left, Top-Right, Bottom-Right, Bottom-Left.
                        
        Returns:
            homography_matrix: 3x3 matrix.
        """
        if src_points.shape != (4, 2):
            raise ValueError("src_points must be (4, 2)")
            
        h, status = cv2.findHomography(src_points, self.court_corners_world)
        self.homography_matrix = h
        return h

    def pixel_to_court(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """
        Transform pixel coordinates (x, y) to court coordinates (meters).
        """
        if self.homography_matrix is None:
            raise RuntimeError("Homography not computed. Run detect_court or compute_homography_from_points first.")
            
        # Convert to homogeneous coordinates
        p = np.array([point[0], point[1], 1.0]).reshape(3, 1)
        
        # Apply projection
        projected = np.dot(self.homography_matrix, p)
        
        # Normalize
        scale = projected[2]
        if abs(scale) < 1e-6:
            return (0.0, 0.0) # Avoid div by zero
            
        x_world = projected[0] / scale
        y_world = projected[1] / scale
        
        return (float(x_world), float(y_world))

    def _get_edges(self, gray: np.ndarray) -> np.ndarray:
        return cv2.Canny(gray, 50, 150, apertureSize=3)

    def _get_lines(self, edges: np.ndarray) -> Optional[np.ndarray]:
        return cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=20)
