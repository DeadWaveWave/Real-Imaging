import os
import csv
import datetime
import zipfile
import rarfile
import py7zr
import shutil
import torch
import codecs
import numpy as np
from image_process import *
from model import *
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def img_info_writer(user_folder_path, file_paths):
    with codecs.open('temp_img_path.csv', 'w', 'utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['file_name'])
        for path in file_paths:
            writer.writerow([path])

    csv_path = os.path.join(user_folder_path, 'img_paths.csv')
    with codecs.open(csv_path, 'a', 'utf-8') as file:
        writer = csv.writer(file)
        for path in file_paths:
            writer.writerow([path])

def img_path_process_local(local_folder_path, user_folder_path):
    # 遍历./img/upload 文件夹下附属文件夹内的图片，将图片路径进行收集后写入upload_img_path.csv中
    file_paths = []

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            if not file.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
                continue
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    img_info_writer(user_folder_path, file_paths)


def upload_from_img_folder_path(local_folder_path, user_name, upload_img_database_name):
    # 调用img_path_process函数处理图片路径，保存到temp_img_path.csv中
    user_folder_path = os.path.join("../data", user_name, upload_img_database_name)
    img_path_process_local(local_folder_path, user_folder_path)

    # 将图片向量化，添加到img_vectors中
    img_data = pd.read_csv('temp_img_path.csv')
    if img_data.empty:
        return "目标文件夹中没有图片文件！"

    df = process_image_data('temp_img_path.csv', model_name) # ViT-B-16, RN50
    new_img_vectors = torch.tensor(df['vec'].tolist())

    # 将新的图片向量拼接到img_vectors中
    user_img_database_pth = os.path.join("../data", user_name, upload_img_database_name, "img_vectors_output_" + model_name + ".pth")
    img_vectors = torch.load(user_img_database_pth)
    img_vectors = torch.cat((img_vectors, new_img_vectors), 0)

    # 将拼接后的img_vectors保存到pth中
    torch.save(img_vectors.to(torch.device('cpu')), user_img_database_pth)
    
    return "success"


def img_path_process_upload(user_folder_path):
    # 遍历 ./img/temp 文件夹下附属文件夹内的图片，将图片路径进行收集后写入对应图库下的 img_paths.csv中
    temp_path = '../data/temp'
    file_paths = []

    for root, dirs, files in os.walk(temp_path):
        for i, file in enumerate(files):
            ## 判断是否为图片文件，如果不是则删除
            if not file.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
                os.remove(os.path.join(root, file))
                continue
            # 为图片以序号重命名
            # file_name, file_ext = os.path.splitext(file)  # 获取文件名和后缀
            # image_name = f"{i+1}{file_ext}"  # 使用序号和原始后缀作为新文件名
            # os.rename(os.path.join(root, file), os.path.join(root, image_name))
            # 转换为PIL图像对象
            file_path = os.path.join(root, file)
            img = Image.open(file_path)
            img = np.array(img)  # 将图像文件转换为数组
            # img = preprocess(img).unsqueeze(0).to(device)
            pil_image = Image.fromarray(img)
            # 保存图片到指定路径
            image_path = os.path.join(user_folder_path, file)
            file_paths.append(image_path)
            pil_image.save(image_path)
            os.remove(os.path.join(root, file))

    img_info_writer(user_folder_path, file_paths)



def upload_img_file(file, user_name, upload_img_database_name):
    # 在这里执行文件保存操作
    filename = os.path.basename(file.name)
    dst_path = os.path.join("../data", "temp", filename)
    shutil.move(file.name, dst_path)
    # print("File saved successfully.")

    # 读取图片，判断是压缩包还是单张图片
    ## 先创建一个以时间戳命名的文件夹，将图片复制到该文件夹下
    # current_time = datetime.datetime.now()
    # timestamp = current_time.strftime("%Y%m%d%H%M%S")  # 将时间格式化为字符串
    # os.mkdir(os.path.join("../data", "upload", timestamp))
    ## 如果是压缩包，先解压到指定文件夹
    # 处理 RAR 格式文件
    if filename.endswith('.rar'):
        rar_path = os.path.join("../data", "temp", filename)
        with rarfile.RarFile(rar_path) as rf:
            rf.extractall(os.path.join("../data", "temp"))
        # 删除压缩包
        os.remove(zip_path)
    # 处理 7Z 格式文件
    elif filename.endswith('.7z'):
        archive_path = os.path.join("../data", "temp", filename)
        with py7zr.SevenZipFile(archive_path, mode='r') as z:
            z.extractall(path=os.path.join("../data", "temp"))
        # 删除压缩包
        os.remove(zip_path)
    # 处理 ZIP 格式文件
    elif filename.endswith('.zip'):
        zip_path = os.path.join("../data", "temp", filename)
        zip_file = zipfile.ZipFile(zip_path)
        zip_file.extractall(os.path.join("../data", "temp"))
        zip_file.close()
        # 删除压缩包
        os.remove(zip_path)

    # 调用img_path_process函数处理图片路径，保存到temp_img_path.csv中
    user_folder_path = os.path.join("../data", user_name, upload_img_database_name)
    img_path_process_upload(user_folder_path)

    # 将图片向量化，添加到img_vectors中
    img_data = pd.read_csv('temp_img_path.csv')
    if img_data.empty:
        return "目标文件夹中没有图片文件！"

    df = process_image_data('temp_img_path.csv', model_name) # ViT-B-16, RN50
    new_img_vectors = torch.tensor(df['vec'].tolist())
    # print(new_img_vectors)
    # 将新的图片向量拼接到img_vectors中
    user_img_database_pth = os.path.join("../data", user_name, upload_img_database_name, "img_vectors_output_" + model_name + ".pth")
    img_vectors = torch.load(user_img_database_pth)
    img_vectors = torch.cat((img_vectors, new_img_vectors), 0)
    # 将拼接后的img_vectors保存到info_output.pth中
    torch.save(img_vectors.to(torch.device('cpu')), user_img_database_pth)
    
    return "success"