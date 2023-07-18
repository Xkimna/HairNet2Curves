import argparse
import os.path

import cv2
import torch
import numpy as np
# import matplotlib.pyplot as plt

from PIL import Image
from torchvision import transforms
from MobileNetV2_unet import MobileNetV2_unet


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=str)
    parser.add_argument("--image_path", type=str)
    return parser.parse_args()


def load_model(workspace):
    model = MobileNetV2_unet(pre_trained=os.path.join(workspace,"hair_detection/model/mobilenet_v2.pth.tar"))
    state_dict = torch.load(os.path.join(workspace, "hair_detection/model/model.pt"), map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    return model


if __name__ == "__main__":
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )
    workspace = get_args().workspace
    model = load_model(workspace)

    imagePath = get_args().image_path
    image = cv2.imread(imagePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 图片修正为正方形
    height, width = image.shape[:2]
    square_size = max(height, width)
    if(height > width):
        square_img = cv2.copyMakeBorder(image, 0, 0, 0, height-width, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    else:
        square_img = cv2.copyMakeBorder(image, 0, height - width, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    cv2.imwrite(os.path.join(workspace, "temp/img/input_preprocessed.jpg"), cv2.cvtColor(square_img, cv2.COLOR_RGB2BGR))
    print("hair_detection:1.Crop the image to a square")
    pil_img = Image.fromarray(square_img)
    torch_img = transform(pil_img)
    torch_img = torch_img.unsqueeze(0)

    logits = model(torch_img)

    temp_logits = logits.squeeze().detach().numpy()

    mask = np.argmax(logits.data.cpu().numpy(), axis=1)
    mask = mask.squeeze()

    face_mask = np.zeros((224, 224, 3))
    hair_mask = np.zeros((224, 224, 3))

    for i in range(len(mask)):
        for j in range(len(mask[i])):
            if mask[i][j] == 1:  # Face
                face_mask[i][j] = [255, 255, 255]
                continue
            if mask[i][j] == 2:  # Hair
                hair_mask[i][j] = [255, 255, 255]
                continue
            if mask[i][j] == 0:  # Background
                face_mask[i][j] = [0, 0, 0]
                hair_mask[i][j] = [0, 0, 0]
                continue

    face_mask_output = face_mask.astype(np.uint8)
    hair_mask_output = hair_mask.astype(np.uint8)
    face_mask_output = cv2.resize(
        face_mask.astype(np.uint8), (square_size, square_size), interpolation=cv2.INTER_LINEAR
    )
    hair_mask_output = cv2.resize(
        hair_mask.astype(np.uint8), (square_size, square_size), interpolation=cv2.INTER_LINEAR
    )
    face_mask_output_path = os.path.join(workspace, "temp/body_img/input_preprocessed.png")
    hair_mask_output_path = os.path.join(workspace, "temp/seg/input_preprocessed.png")
    cv2.imwrite(face_mask_output_path, face_mask_output)
    cv2.imwrite(hair_mask_output_path, hair_mask_output)
    print("hair_detection:2.Saved face_mask & hair_mask")


    # ax = plt.subplot(131)
    # ax.axis("off")
    # ax.imshow(square_img.squeeze())
    #
    # ax = plt.subplot(132)
    # ax.axis("off")
    # ax.imshow(face_mask_output)
    #
    # ax = plt.subplot(133)
    # ax.axis("off")
    # ax.imshow(hair_mask_output)

    # plt.show()
