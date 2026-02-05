import os
import shutil
import cv2
import numpy as np
import pytest
from src.train.prepare_data import extract_frames, convert_cvat_to_yolo, split_dataset
from src.train.train_model import train_model

TEST_DIR = "tests/test_data_train"

@pytest.fixture
def setup_test_data():
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # Create dummy video
    video_path = os.path.join(TEST_DIR, "dummy.mp4")
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (100, 100))
    for i in range(10):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    # Create dummy annotation XML (minimal CVAT style)
    xml_content = """
    <annotations>
        <image id="0" name="frame_000000.jpg" width="100" height="100">
            <box label="shuttlecock" xtl="10" ytl="10" xbr="20" ybr="20" occluded="0" z_order="0">
            </box>
        </image>
    </annotations>
    """
    xml_path = os.path.join(TEST_DIR, "annotations.xml")
    with open(xml_path, "w") as f:
        f.write(xml_content)
        
    yield video_path, xml_path
    
    # Cleanup
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_extract_frames(setup_test_data):
    video_path, _ = setup_test_data
    out_dir = os.path.join(TEST_DIR, "frames")
    extract_frames(video_path, out_dir, interval=1)
    
    assert os.path.exists(os.path.join(out_dir, "frame_000000.jpg"))
    assert len(os.listdir(out_dir)) == 10

def test_convert_annotations(setup_test_data):
    _, xml_path = setup_test_data
    out_dir = os.path.join(TEST_DIR, "labels")
    convert_cvat_to_yolo(xml_path, "", out_dir)
    
    txt_path = os.path.join(out_dir, "frame_000000.txt")
    assert os.path.exists(txt_path)
    
    with open(txt_path, "r") as f:
        content = f.read().strip()
        # 0 x y w h -> 0 0.15 0.15 0.1 0.1
        parts = content.split()
        assert parts[0] == "0" # class id
        assert float(parts[1]) == pytest.approx(0.15)
