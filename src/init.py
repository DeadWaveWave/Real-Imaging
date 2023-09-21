# 遍历../data文件夹下的图片，将图片路径进行收集后写入all_img_path.csv
# 预处理../data文件夹下的图片，将图片向量化后写入img_vectors_output.pth
import os
import csv
import torch
from image_process import *
from model import *

# device = "cpu"
# model_name = "RN50" # "RN50" "ViT-B-16"
# model, preprocess = clip.load_from_name(model_name, device=device, download_root='../model')
# model.eval()

def init():
    folder_path = '../data'
    file_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if not file.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
                continue
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    with open('all_img_path.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['file_name'])
        for path in file_paths:
            writer.writerow([path])

    df = process_image_data('all_img_path.csv', model_name) # ViT-B-16, RN50
    img_vectors = torch.tensor(df['vec'].tolist())

    pth = "img_vectors_output_" + model_name + ".pth"
    torch.save(img_vectors.to(torch.device('cpu')), pth)
    
    print("init successfully")
    return "初始化完成！"

if __name__ == "__main__":
    init()