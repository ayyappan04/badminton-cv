import sys
import os
import numpy as np
import logging

sys.path.append(os.path.join(os.getcwd(), 'src'))

from analytics import MetricsCalculator
from calibrate import CourtCalibrator
from utils import setup_logger

logger = setup_logger("verify_metrics")

# Mock Calibrator that implements simple scaling (10px = 1m)
class MockCalibrator(CourtCalibrator):
    def __init__(self):
        super().__init__()
        # Override to ensure it doesn't try to load config or fail
        self.homography_matrix = np.eye(3) 
    
    def pixel_to_court(self, point):
        # Mock transformation: just scale down by 10
        return (point[0] / 10.0, point[1] / 10.0)

def verify_metrics():
    logger.info("Starting metrics verification...")
    
    calibrator = MockCalibrator()
    metrics = MetricsCalculator(calibrator)
    
    # 1. Verify Speed Calculation
    # P1 (0, 0) -> P2 (100, 0) is 10 meters distance in our mock
    # Delta time 0.5s -> 20 m/s -> 72 km/h
    p1 = (0, 0)
    p2 = (100, 0)
    dt = 0.5
    
    speed = metrics.compute_shuttle_speed(p1, p2, dt)
    logger.info(f"Computed Speed: {speed:.2f} km/h (Expected ~72.00)")
    
    if abs(speed - 72.0) < 0.1:
         logger.info("SUCCESS: Speed calculation correct.")
    else:
         logger.error("FAILURE: Speed calculation incorrect.")

    # 2. Verify Player Distance
    # Move player 0: (0,0) -> (10,0) -> (10,10)
    # (0,0) to (10,0) (px) = 1m
    # (10,0) to (10,10) (px) = 1m
    # Total distance = 2m
    metrics.update_player_stats(0, (0, 0), 0)
    metrics.update_player_stats(0, (10, 0), 1)
    metrics.update_player_stats(0, (10, 10), 2)
    
    summary = metrics.get_summary()
    dist = summary['players'][0]['total_distance_m']
    logger.info(f"Player 0 Total Distance: {dist:.2f}m (Expected ~2.00)")

    if abs(dist - 2.0) < 0.1:
         logger.info("SUCCESS: Distance calculation correct.")
    else:
         logger.error("FAILURE: Distance calculation incorrect.")

if __name__ == "__main__":
    verify_metrics()
