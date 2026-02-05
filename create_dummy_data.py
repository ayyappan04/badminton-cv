import cv2
import numpy as np
import os

def create_dummy_video(output_path: str, duration_sec: int = 5, fps: int = 30):
    """Create a dummy moving ball video."""
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frames = duration_sec * fps
    x, y = 100, 360
    dx, dy = 5, 2
    
    for i in range(frames):
        # Create black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw "court" (rectangle)
        cv2.rectangle(frame, (100, 100), (1180, 620), (0, 255, 0), 2)
        
        # Draw "ball"
        cv2.circle(frame, (x, y), 10, (255, 255, 255), -1)
        
        # Update ball position
        x += dx
        y += dy
        
        if x <= 100 or x >= 1180: dx = -dx
        if y <= 100 or y >= 620: dy = -dy
        
        # Add frame count text
        cv2.putText(frame, f"Frame: {i}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
        
    out.release()
    print(f"Created dummy video at {output_path}")

if __name__ == "__main__":
    create_dummy_video("data/test/dummy_match.mp4")
