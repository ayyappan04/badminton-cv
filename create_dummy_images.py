import cv2
import numpy as np
import os

images_train = "../data/shuttle_dataset/images/train"
images_val = "../data/shuttle_dataset/images/val"
os.makedirs(images_train, exist_ok=True)
os.makedirs(images_val, exist_ok=True)

img = np.zeros((100, 100, 3), dtype=np.uint8)
cv2.imwrite(os.path.join(images_train, "dummy.jpg"), img)
cv2.imwrite(os.path.join(images_val, "dummy.jpg"), img)
print("Created valid dummy images.")
