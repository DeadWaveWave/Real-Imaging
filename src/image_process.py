import pandas as pd
import numpy as np
import torch
import cn_clip.clip as clip
import time
from model import *
from PIL import Image

# 加载模型和预处理函数
# device = "cpu"
# model_name = "RN50" # "RN50" "ViT-B-16"
# pth = "img_vectors_output_" + model_name + ".pth"
# model, preprocess = clip.load_from_name(model_name, device=device, download_root='../model/')
# model.eval()

def image_generator(file_names, preprocess, batch_size=32):
    for i in range(0, len(file_names), batch_size):
        batch = file_names[i:i+batch_size]
        img_list = [preprocess(Image.open(file_name)).unsqueeze(0) for file_name in batch]
        img_tensor = torch.cat(img_list, dim=0)
        yield img_tensor

def process_image_data(csv_file, model_name, batch_size=32):
    # 计算处理时间
    start_time = time.time()

    # 读取CSV文件并加载图像
    img_data = pd.read_csv(csv_file)

    # 逐个处理图像
    vec_list = []
    with torch.no_grad():
        for img_batch in image_generator(img_data['file_name'], preprocess, batch_size=batch_size):
            image_features = model.encode_image(img_batch.to(device))
            image_features /= image_features.norm(dim=-1, keepdim=True)
            vec_list.append(image_features.cpu().numpy())

    # 将向量拼接成一个数组
    vec_array = np.concatenate(vec_list, axis=0)

    # 将向量存储在DataFrame中
    img_data['vec'] = [vec_array[i] for i in range(len(img_data))]

    # 计算处理时间
    end_time = time.time()
    print("Time cost: ", end_time - start_time, "s")

    return img_data[['file_name', 'vec']]