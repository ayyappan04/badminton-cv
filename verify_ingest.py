import sys
import os
import time

sys.path.append(os.path.join(os.getcwd(), 'src'))

from ingest import VideoIngester
from utils import setup_logger

logger = setup_logger("test_ingest")

def test_ingestion():
    video_path = "data/test/dummy_match.mp4"
    if not os.path.exists(video_path):
        logger.error(f"Video not found at {video_path}. Run create_dummy_data.py first.")
        return

    logger.info(f"Testing ingestion with {video_path}")
    
    start_time = time.time()
    try:
        with VideoIngester(video_path) as ingester:
            metadata = ingester.get_metadata()
            logger.info(f"Metadata extracted: {metadata}")
            
            chunk_count = 0
            total_frames_processed = 0
            
            # Temporarily reduce chunk duration to test chunking on a small video
            ingester.chunk_duration = 2 # 2 seconds chunks
            
            for chunk_idx, frames in ingester.process_chunks():
                chunk_count += 1
                frame_count = len(frames)
                total_frames_processed += frame_count
                logger.info(f"Processed Chunk {chunk_idx}: {frame_count} frames. Shape: {frames[0].shape}")
                
            logger.info(f"Total Chunks: {chunk_count}")
            logger.info(f"Total Frames: {total_frames_processed}")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        
    duration = time.time() - start_time
    logger.info(f"Test completed in {duration:.2f} seconds")

if __name__ == "__main__":
    test_ingestion()
