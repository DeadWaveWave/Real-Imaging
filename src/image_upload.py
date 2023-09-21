import os
import csv
import datetime
import zipfile
import shutil
import torch
import numpy as np
from image_process import *
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def img_path_process(folder_path):
    # 遍历./img/upload 文件夹下附属文件夹内的图片，将图片路径进行收集后写入upload_img_path.csv中

    temp_path = '../data/temp'
    file_paths = []

    for root, dirs, files in os.walk(temp_path):
        for i, file in enumerate(files):
            ## 判断是否为图片文件，如果不是则删除
            if not file.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
                os.remove(os.path.join(root, file))
                continue
            # 为图片以序号重命名
            file_name, file_ext = os.path.splitext(file)  # 获取文件名和后缀
            image_name = f"{i+1}{file_ext}"  # 使用序号和原始后缀作为新文件名
            os.rename(os.path.join(root, file), os.path.join(root, image_name))
            # 转换为PIL图像对象
            file_path = os.path.join(root, image_name)
            img = Image.open(file_path)
            img = np.array(img)  # 将图像文件转换为数组
            # img = preprocess(img).unsqueeze(0).to(device)
            pil_image = Image.fromarray(img)
            # 保存图片到指定路径
            image_path = os.path.join(folder_path, image_name)
            pil_image.save(image_path)
            file_paths.append(image_path)
            os.remove(os.path.join(root, image_name))

    with open('temp_img_path.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['file_name'])
        for path in file_paths:
            writer.writerow([path])

    with open('upload_img_path.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for path in file_paths:
            writer.writerow([path])

    with open('all_img_path.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for path in file_paths:
            writer.writerow([path])

def upload_file(file):
    model_name = "RN50"
    pth = "img_vectors_output_" + model_name + ".pth"
    # 在这里执行文件保存操作
    filename = os.path.basename(file.name)
    dst_path = os.path.join("../data", "temp", filename)
    shutil.move(file.name, dst_path)
    print("File saved successfully.")

    # 读取图片，判断是压缩包还是单张图片
    ## 先创建一个以时间戳命名的文件夹，将图片复制到该文件夹下
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y%m%d%H%M%S")  # 将时间格式化为字符串
    os.mkdir(os.path.join("../data", "upload", timestamp))
    ## 如果是压缩包，先解压到指定文件夹
    if filename.endswith('.zip'):
        zip_path = os.path.join("../data", "temp", filename)
        zip_file = zipfile.ZipFile(zip_path)
        zip_file.extractall(os.path.join("../data", "temp"))
        zip_file.close()
        # 删除压缩包
        os.remove(zip_path)

    # 调用img_path_process函数处理图片路径，保存到temp_img_path.csv中
    img_path_process(os.path.join("../data", "upload", timestamp))

    # 将图片向量化，添加到img_vectors中
    df = process_image_data('temp_img_path.csv', model_name) # ViT-B-16, RN50
    new_img_vectors = torch.tensor(df['vec'].tolist())
    # print(new_img_vectors)
    # 将新的图片向量拼接到img_vectors中
    img_vectors = torch.load(pth)
    img_vectors = torch.cat((img_vectors, new_img_vectors), 0)
    # 将拼接后的img_vectors保存到info_output.pth中
    torch.save(img_vectors.to(torch.device('cpu')), pth)
    
    return "success"