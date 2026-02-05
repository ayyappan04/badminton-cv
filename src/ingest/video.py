import av
import cv2
import numpy as np
import os
import logging
from typing import Dict, Generator, Tuple, Optional, List
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.ingest")

class VideoIngester:
    def __init__(self, video_path: str, config: Optional[Dict] = None):
        """
        Initialize the VideoIngester.
        
        Args:
            video_path: Absolute path to the video file.
            config: Optional configuration dictionary. If None, loads default.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.video_path = video_path
        self._config_loader = config if config else get_config()
        self.config = self._config_loader.config if hasattr(self._config_loader, 'config') else get_config().config
        
        self.container = av.open(video_path)
        self.video_stream = self.container.streams.video[0]
        self.video_stream.thread_type = 'AUTO'  # Enable multi-threading
        
        # Extract metadata
        self.fps = float(self.video_stream.average_rate)
        self.total_frames = self.video_stream.frames
        if self.total_frames == 0:
            # Estimate if not available in header
            self.total_frames = int(self.video_stream.duration * self.video_stream.time_base * self.fps)
            
        self.width = self.video_stream.codec_context.width
        self.height = self.video_stream.codec_context.height
        self.duration = float(self.video_stream.duration * self.video_stream.time_base)
        
        self.target_resolution = self.config.get('video', {}).get('target_resolution', [1280, 720])
        self.chunk_duration = self.config.get('video', {}).get('chunk_duration', 60)
        
        logger.info(f"Initialized VideoIngester for {video_path}")
        logger.info(f"Metadata: {self.width}x{self.height} @ {self.fps:.2f}fps, {self.duration:.2f}s")

    def get_metadata(self) -> Dict:
        """Return video metadata."""
        return {
            "path": self.video_path,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "codec": self.video_stream.codec_context.name
        }

    def process_chunks(self) -> Generator[Tuple[int, List[np.ndarray]], None, None]:
        """
        Yield chunks of frames.
        
        Yields:
             Tuple[int, List[np.ndarray]]: (chunk_index, list_of_frames)
        """
        chunk_size_frames = int(self.chunk_duration * self.fps)
        current_chunk = []
        chunk_index = 0
        
        logger.info(f"Processing video in chunks of {chunk_size_frames} frames ({self.chunk_duration}s)")
        
        for frame in self.container.decode(video=0):
            # Convert to numpy (RGB) then BGR for OpenCV
            img = frame.to_ndarray(format='bgr24')
            
            # Resize if needed
            if (img.shape[1], img.shape[0]) != tuple(self.target_resolution):
                img = cv2.resize(img, tuple(self.target_resolution))
                
            current_chunk.append(img)
            
            if len(current_chunk) >= chunk_size_frames:
                yield chunk_index, current_chunk
                chunk_index += 1
                current_chunk = []
        
        # Yield remaining frames
        if current_chunk:
            yield chunk_index, current_chunk

    def close(self):
        """Close the video container."""
        if self.container:
            self.container.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
