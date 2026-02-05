import os
import cv2
import logging
import xml.etree.ElementTree as ET
import shutil
from glob import glob
from tqdm import tqdm
from typing import List, Optional

logger = logging.getLogger("badminton_cv.train.prepare")

def extract_frames(video_path: str, output_dir: str, interval: int = 30):
    """
    Extract frames from a video for labeling.
    
    Args:
        video_path: Path to video.
        output_dir: Directory to save images.
        interval: Extract every Nth frame.
    """
    if not os.path.exists(video_path):
        logger.error(f"Video not found: {video_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    saved_count = 0
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=total_frames, desc="Extracting frames")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % interval == 0:
            frame_name = f"frame_{frame_count:06d}.jpg"
            out_path = os.path.join(output_dir, frame_name)
            cv2.imwrite(out_path, frame)
            saved_count += 1
            
        frame_count += 1
        pbar.update(1)
        
    pbar.close()
    cap.release()
    logger.info(f"Extracted {saved_count} frames to {output_dir}")

def convert_cvat_to_yolo(xml_path: str, image_dir: str, output_dir: str, class_map: dict = {'shuttlecock': 0}):
    """
    Convert CVAT XML annotations to YOLO format.
    
    Args:
        xml_path: Path to annotations.xml
        image_dir: Path where images are stored (to check dimensions if needed or matched).
        output_dir: Path to save .txt label files.
        class_map: Dictionary mapping label names to YOLO class IDs.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    os.makedirs(output_dir, exist_ok=True)
    
    for image in root.findall('image'):
        name = image.get('name')
        width = int(image.get('width'))
        height = int(image.get('height'))
        
        txt_name = os.path.splitext(name)[0] + ".txt"
        txt_path = os.path.join(output_dir, txt_name)
        
        with open(txt_path, 'w') as f:
            for box in image.findall('box'):
                label = box.get('label')
                if label not in class_map:
                    continue
                    
                cls_id = class_map[label]
                xtl = float(box.get('xtl'))
                ytl = float(box.get('ytl'))
                xbr = float(box.get('xbr'))
                ybr = float(box.get('ybr'))
                
                # Convert to center_x, center_y, w, h (normalized)
                w_box = xbr - xtl
                h_box = ybr - ytl
                cx = xtl + w_box / 2
                cy = ytl + h_box / 2
                
                cx /= width
                cy /= height
                w_box /= width
                h_box /= height
                
                f.write(f"{cls_id} {cx:.6f} {cy:.6f} {w_box:.6f} {h_box:.6f}\n")
                
    logger.info(f"Converted annotations to {output_dir}")

def split_dataset(data_dir: str, train_ratio: float = 0.8):
    """
    Split a directory of images and labels into train/val structure for YOLO.
    Expected structure of data_dir:
    - images/
    - labels/
    """
    images = glob(os.path.join(data_dir, "images", "*.jpg"))
    import random
    random.shuffle(images)
    
    split_idx = int(len(images) * train_ratio)
    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]
    
    # Move to new structure
    # datasets/
    #   images/
    #     train/
    #     val/
    #   labels/
    #     train/
    #     val/
    
    base_dir = os.path.dirname(data_dir) # parent
    
    for subdir in ['images/train', 'images/val', 'labels/train', 'labels/val']:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
        
    def move_files(file_list, split_name):
        for img_path in file_list:
            basename = os.path.basename(img_path)
            txt_name = os.path.splitext(basename)[0] + ".txt"
            
            # Source paths
            lbl_path = os.path.join(data_dir, "labels", txt_name)
            
            # Dest paths
            dst_img = os.path.join(base_dir, "images", split_name, basename)
            dst_lbl = os.path.join(base_dir, "labels", split_name, txt_name)
            
            shutil.copy(img_path, dst_img)
            if os.path.exists(lbl_path):
                shutil.copy(lbl_path, dst_lbl)
                
    move_files(train_imgs, 'train')
    move_files(val_imgs, 'val')
    
    logger.info(f"Dataset split completed. Train: {len(train_imgs)}, Val: {len(val_imgs)}")
