import os
import csv
import codecs
import pandas as pd
import torch
from model import *

def get_img_database_name(user_name):
    # 从user_paths.csv中获取用户图库名称
    database_path = os.path.join('../data', user_name, 'img_database_paths.csv')
    img_database_name = []
    # 以字符串形式读取 csv 文件并返回用户图库名称
    if os.path.exists(database_path):
        df = pd.read_csv(database_path, dtype=str)
        img_database_name = df['database_name'].tolist()
        print("img_database_name: ", img_database_name)
    else:
        print("文件不存在：", database_path)
    return img_database_name

def create_img_database(user_name, new_img_database_name):
    # 在用户目录下创建新的图库
    folder_path = os.path.join('../data', user_name, new_img_database_name)
    database_csv_path = os.path.join('../data', user_name, 'img_database_paths.csv')
    img_csv_path = os.path.join('../data', user_name, new_img_database_name, 'img_paths.csv')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        # 在用户目录下的img_database_paths.csv中添加新的图库名称
        with codecs.open(database_csv_path, 'a', 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([new_img_database_name])
        # 在新的图库目录下创建 img_paths.csv
        with codecs.open(img_csv_path, 'w', 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['file_name'])
        # 在新的图库目录下创建空 pth 文件
        img_vectors = torch.tensor([])
        new_pth_path = os.path.join(folder_path, "img_vectors_output_" + model_name + ".pth")
        torch.save(img_vectors.to(torch.device('cpu')), new_pth_path)
        return True
    else:
        return False