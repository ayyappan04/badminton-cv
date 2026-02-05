import sys
import os
import logging

sys.path.append(os.path.join(os.getcwd(), 'src'))

from events import EventDetector
from utils import setup_logger

logger = setup_logger("verify_events")

def verify_events():
    logger.info("Starting event detection verification...")
    
    detector = EventDetector()
    
    # 1. Verify Shot Classification
    test_shots = [
        {'name': 'Test Smash', 'features': {'max_speed': 250.0, 'angle': 45.0, 'max_height': 2.5}, 'expected': 'Smash'},
        {'name': 'Test Clear', 'features': {'max_speed': 120.0, 'angle': 60.0, 'max_height': 6.0}, 'expected': 'Clear'},
        {'name': 'Test Drive', 'features': {'max_speed': 150.0, 'angle': 5.0,  'max_height': 1.6}, 'expected': 'Drive'},
    ]
    
    for shot in test_shots:
        result = detector.classify_shot(shot['features'])
        status = "PASS" if result == shot['expected'] else f"FAIL (Got {result})"
        logger.info(f"Shot: {shot['name']} -> {status}")
        
    # 2. Verify Rally Detection
    logger.info("Simulating rally...")
    # Simulate 5 seconds (150 frames @ 30fps) of detected shuttle
    for i in range(150):
        frame_data = {
            'frame_idx': i,
            'timestamp': i / 30.0,
            'shuttle_pos': (100, 100) # Dummy pos
        }
        detector.update(frame_data)
        
    # Simulate gap (rally ends)
    detector.update({'frame_idx': 150, 'timestamp': 150/30.0, 'shuttle_pos': None})
    
    if len(detector.rallies) == 1:
        r = detector.rallies[0]
        logger.info(f"Correctly detected rally. Duration: {r['duration']:.2f}s")
    else:
        logger.warning(f"Failed to detect rally. Count: {len(detector.rallies)}")

if __name__ == "__main__":
    verify_events()
