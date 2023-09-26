# 遍历../data文件夹下的图片，将图片路径进行收集后写入all_img_path.csv
# 预处理../data文件夹下的图片，将图片向量化后写入img_vectors_output.pth
import sys
import os
import csv
import torch
from image_process import *
from model import *

def init(folder_path = '../data'):
    root_paths = []
    for root, dirs, files in os.walk(folder_path):
        # 在每个文件夹下
        file_paths = []
        for file in files:
            # 只记录图片文件
            if not file.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
                continue
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
        # 图库
        if dirs == [] and files != []:
            root_paths.append(root)
            csv_path = os.path.join(root, 'img_paths.csv')
            with open(csv_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['file_name'])
                for path in file_paths:
                    writer.writerow([path])
            # 将图片向量化，添加到img_vectors中
            df = process_image_data(csv_path, model_name) # ViT-B-16, RN50
            img_vectors = torch.tensor(df['vec'].tolist())
            # 将 img_vectors 保存到 pth 中
            pth_name = "img_vectors_output_" + model_name + ".pth"
            pth_path = os.path.join(root, pth_name)
            torch.save(img_vectors.to(torch.device('cpu')), pth_path)
        # 写入用户目录路径信息
        if 'temp' in dirs:
            # 删去dirs中的temp
            dirs.remove('temp')
            csv_path = os.path.join(root, 'user_paths.csv')
            with open(csv_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['user_name'])
                for user_name in dirs:
                    # user_folder_path = os.path.join(root, dir)
                    writer.writerow([user_name])
        elif dirs != []:
            img_database_paths = os.path.join(root, 'img_database_paths.csv')
            with open(img_database_paths, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['database_name'])
                for database_name in dirs:
                    # database_folder_path = os.path.join(root, dir)
                    writer.writerow([database_name])

    print("init successfully")
    return "初始化完成！"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        init(folder_path)
    else:
        init()