import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from utils import get_config, setup_logger

def main():
    logger = setup_logger("setup_verification")
    logger.info("Starting setup verification...")
    
    # Check config
    try:
        config = get_config()
        logger.info(f"Config loaded successfully. Target resolution: {config.get('video.target_resolution')}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # Check torch (if available in environment, though we haven't installed it yet)
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        logger.warning("PyTorch not installed yet (expected if requirements not installed).")

    logger.info("Verification complete.")

if __name__ == "__main__":
    main()
