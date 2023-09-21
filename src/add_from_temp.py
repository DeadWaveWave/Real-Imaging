import torch
import pandas as pd
import numpy as np
import os
import datetime
import image_process

model_name = "RN50"
pth = "img_vectors_output_" + model_name + ".pth"
# 从temp新增数据
## 先创建一个以时间戳命名的文件夹，将图片复制到该文件夹下
current_time = datetime.datetime.now()
timestamp = current_time.strftime("%Y%m%d%H%M%S")  # 将时间格式化为字符串
os.mkdir(os.path.join("img", "upload", timestamp))

# 调用img_path_process函数处理图片路径，保存到temp_img_path.csv中
img_path_process(os.path.join("img", "upload", timestamp))

# 将图片向量化，添加到img_vectors中
df = process_image_data('temp_img_path.csv', model_name) # ViT-B-16, RN50
new_img_vectors = torch.tensor(df['vec'].tolist())
print(new_img_vectors)
# 将新的图片向量拼接到img_vectors中
img_vectors = torch.load(pth)
img_vectors = torch.cat((img_vectors, new_img_vectors), 0)
# 将拼接后的img_vectors保存到info_output.pth中
torch.save(img_vectors.to(torch.device('cpu')), pth)