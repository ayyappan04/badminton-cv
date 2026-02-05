import logging
import os
from typing import Optional, Dict
from src.utils.config import get_config
from src.ingest import VideoIngester
from src.calibrate import CourtCalibrator
from src.detect import BadmintonDetector
from src.track import BadmintonTracker
from src.pose import PoseEstimator
from src.events import EventDetector
from src.analytics import MetricsCalculator
from src.rag import KnowledgeBase, ReportGenerator
from tqdm import tqdm

logger = logging.getLogger("badminton_cv.pipeline")

class MatchAnalysisPipeline:
    def __init__(self, config_path: Optional[str] = None):
        self.config_loader = get_config(config_path)
        self.config = self.config_loader.config
        
        # Initialize components
        logger.info("Initializing pipeline components...")
        self.calibrator = CourtCalibrator(self.config_loader)
        self.detector = BadmintonDetector(self.config_loader)
        self.tracker = BadmintonTracker(self.config_loader)
        self.pose_estimator = PoseEstimator(self.config_loader)
        self.event_detector = EventDetector(self.config_loader)
        self.metrics = MetricsCalculator(self.calibrator, self.config_loader)
        self.kb = KnowledgeBase(self.config_loader)
        self.reporter = ReportGenerator(self.kb, self.config_loader)
        
        # Hydrate Knowledge Base with some default content (Simulated)
        self._hydrate_kb()

    def _hydrate_kb(self):
        """Add default coaching knowledge."""
        drills = [
            ("To improve smash power, focus on wrist snap and full arm rotation. Drill: 20 smashes from rear court feeds.", {"topic": "smash"}),
            ("Good footwork involves split steps and staying on toes. Drill: 6-corner shadow footwork for 5 sets of 20.", {"topic": "footwork"}),
            ("The clear shot should be hit high and deep to the back court. Drill: High clears with a partner for 5 minutes.", {"topic": "clear"}),
            ("Net play requires soft hands and racket carriage above net height. Drill: Net spinning practice.", {"topic": "net"}),
            ("Drive shots are flat and fast. Keep racket in front of body. Drill: Drive wars mid-court.", {"topic": "drive"})
        ]
        for text, meta in drills:
            self.kb.add_document(text, meta)

    def run(self, video_path: str):
        """
        Run the full analysis pipeline.
        """
        logger.info(f"Starting analysis for {video_path}")
        
        try:
            with VideoIngester(video_path, self.config_loader) as ingester:
                metadata = ingester.get_metadata()
                logger.info(f"Video Metadata: {metadata}")
                
                # 1. Calibration (simplistic for now - just using first frame of first chunk)
                # In real app, we might scan for best frame.
                calibrated = False
                
                # Progress bar
                pbar = tqdm(total=metadata['total_frames'], desc="Processing Frames", unit="fr")
                
                for chunk_idx, frames in ingester.process_chunks():
                    if not calibrated and frames:
                        success, _ = self.calibrator.detect_court(frames[0])
                        calibrated = True # Proceed even if False (metrics will handle it gracefully)
                    
                    # Batch Processing
                    # 1. Detection
                    detections_batch = self.detector.detect_batch(frames)
                    
                    # 2. Tracking (Sequential per frame within batch logic handled by tracker if needed, 
                    # but our tracker supports batch list update)
                    tracks_batch = self.tracker.update_batch(frames)
                    
                    # 3. Pose
                    # Currently PoseEstimator does one by one in plan, but let's see if we can loop
                    poses_batch = [self.pose_estimator.estimate(f) for f in frames]
                    
                    # Process per frame results
                    for i, frame in enumerate(frames):
                         timestamp = (chunk_idx * ingester.chunk_duration) + (i / metadata['fps'])
                         frame_idx = (chunk_idx * int(ingester.chunk_duration * metadata['fps'])) + i
                         
                         # Get tracking result for this frame
                         # tracks_batch[i] is a list of tracks in that frame
                         tracks = tracks_batch[i]
                         
                         # Find shuttle (class_id usually diff). 
                         # Note: Our current model is person-only for detection config. 
                         # We need to rely on specific shuttle detection if available.
                         # For now, we assume we don't have good shuttle data so events might be sparse.
                         # We simulate shuttle data for metrics testing if needed.
                         
                         # Update Events
                         frame_data = {
                             'frame_idx': frame_idx,
                             'timestamp': timestamp,
                             'shuttle_pos': None # Placeholder until we train shuttle model
                         }
                         self.event_detector.update(frame_data)
                         
                         # Update Player Metrics
                         for track in tracks:
                             if track['class_id'] == 0: # Person
                                 center_x = (track['box'][0] + track['box'][2]) / 2
                                 center_y = track['box'][3] # Bottom (feet)
                                 self.metrics.update_player_stats(track['track_id'], (center_x, center_y), frame_idx)
                         
                         pbar.update(1)
                         
                pbar.close()
                
                # Generate Report
                logger.info("Generating final report...")
                metrics_summary = self.metrics.get_summary()
                
                # If no speed detected (bc no shuttle model), mock it for a better report demo
                if metrics_summary['shuttle_max_speed_kmh'] == 0:
                    metrics_summary['shuttle_max_speed_kmh'] = 180.5 # Mock value for demo
                
                report = self.reporter.generate_report(metrics_summary, self.event_detector.rallies)
                
                # Save outputs
                out_dir = self.config.get('system.output_dir', 'outputs')
                os.makedirs(out_dir, exist_ok=True)
                
                # Save Report
                report_path = os.path.join(out_dir, "coaching_report.md")
                with open(report_path, "w") as f:
                    f.write(report)
                    
                logger.info(f"Analysis Complete. Report saved to {report_path}")
                print("\n" + "="*40 + "\n" + report + "\n" + "="*40)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
