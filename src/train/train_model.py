import argparse
import logging
from ultralytics import YOLO
from src.utils import setup_logger

logger = setup_logger("badminton_cv.train")

def train_model(config_path: str, model_type: str = 'yolov8n.pt', epochs: int = 50, img_size: int = 640):
    """
    Train a YOLOv8 model.
    """
    logger.info(f"Starting training with model {model_type}...")
    
    # Load model
    model = YOLO(model_type)
    
    # Train
    results = model.train(
        data=config_path,
        epochs=epochs,
        imgsz=img_size,
        plots=True,
        save=True,
        device='0' if is_cuda_available() else 'cpu'
    )
    
    logger.info(f"Training complete. Results saved at {model.trainer.save_dir}")

def is_cuda_available():
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='Path to data.yaml')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Pretrained model')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--smoke-test', action='store_true', help='Run short training for testing')
    
    args = parser.parse_args()
    
    epochs = 1 if args.smoke_test else args.epochs
    
    train_model(args.config, args.model, epochs)
