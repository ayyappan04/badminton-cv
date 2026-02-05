import os
import sys
import click
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.utils import setup_logger
from src.pipeline import MatchAnalysisPipeline

@click.group()
def cli():
    """Badminton CV Analysis System CLI"""
    pass

@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--config', '-c', default=None, help='Path to config YAML')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def analyze(video_path, config, verbose):
    """Analyze a badminton match video."""
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger("badminton_cv", log_level=log_level)
    
    logger = logging.getLogger("badminton_cv.main")
    logger.info(f"Starting analysis for: {video_path}")
    
    try:
        pipeline = MatchAnalysisPipeline(config)
        pipeline.run(video_path)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)

@cli.command()
def test_setup():
    """Verify system setup and dependencies."""
    setup_logger("badminton_cv_test")
    logger = logging.getLogger("badminton_cv.test")
    logger.info("Verifying setup...")
    
    try:
        import torch
        logger.info(f"PyTorch: {torch.__version__} (CUDA: {torch.cuda.is_available()})")
        import ultralytics
        logger.info(f"Ultralytics: {ultralytics.__version__}")
        import cv2
        logger.info(f"OpenCV: {cv2.__version__}")
        logger.info("Setup looks good!")
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
