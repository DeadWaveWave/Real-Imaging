

import cv2
import os
import torch
import time
from datetime import datetime, timedelta
from text_process import get_sim_probs
from model import *
from PIL import Image


def get_vec(frame):
    with torch.no_grad():
        image = preprocess(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))).unsqueeze(0)
        vec = model.encode_image(image.to(device))
    vec /=vec.norm(dim=-1, keepdim=True)
    return torch.tensor(vec.cpu().detach().numpy())

# 计算处理时间
start_time = time.time()

times = 0

interval = 1            # 读取的时间间隔，1为间隔1秒读取一次
stand_pro = 0.85        # 判断的标准概率，低于此概率视为不同


# 打开视频
video_path = '../videos/秋枝_雨天_孤独_失落.mp4'
video_filename = os.path.splitext(os.path.basename(video_path))[0]
output_folder = '../video_imgs'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("无法打开视频文件")
    exit()

# 获取视频的帧率
fps = int(cap.get(cv2.CAP_PROP_FPS))
ret,frame = cap.read()
flag_vec = get_vec(frame)       # 上一次采集的图片的矩阵
flag_time = 0                   # 上一次采集的帧的的位置
current_time = fps * interval   # 当前采集的帧的位置
start_list = [0]                # 保存每次转场的起始帧
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))      # 总帧数

while current_time <= total_frames:

    # 读取当前帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_time)
    ret, frame = cap.read()
    if not ret:
        break

    # 获取当前图片的矩阵
    current_vec = get_vec(frame)
    times += 1

    # 计算两个上一次矩阵和当前矩阵的相似度
    pro = torch.nn.functional.cosine_similarity(current_vec, flag_vec, dim=-1)
    print(pro)

    # 如果相似度小于标准概率就进行二分
    if pro < stand_pro:
        l = flag_time + 1
        r = current_time

        while (l < r and r - l > fps / 3):
            # 获得中间帧的图片的向量，并计算与当前向量的相似度
            mid = int((l + r)/2)
            cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
            ret, frame = cap.read()
            mid_vec = get_vec(frame)
            pro = torch.nn.functional.cosine_similarity(current_vec, mid_vec, dim=-1)
            if pro < stand_pro:
                l = mid + 1
            else: 
                r = mid
                current_vec = mid_vec
            print("{}, {}".format(l,r))


        current_time = r
        if current_time - fps/2 > start_list[-1]:
            start_list.append(r)
            # 获取上一次场景及其末尾之间中间的帧位置，作为该场景的代表图片
            r = l
            l = start_list[-2]
            mid = (l + r)/2
            # 如果该场景长度较长，多获取几张图片,设定为取距离中间长度为dis秒的倍数的图片,如当dis为4时，对于10秒的场景，会取5秒中间的图片，再取1秒和9秒的图片
            dis = 4
            num = 0
            while mid - num*dis*fps >= l:
                mid1 = mid - num*dis*fps
                mid2 = mid + num*dis*fps
                cap.set(cv2.CAP_PROP_POS_FRAMES, mid2)
                ret, frame = cap.read()
                output_filename = os.path.join(output_folder, f'{video_filename}_{str(start_list[-2]/fps)}_{str(num*2)}.jpg')
                cv2.imwrite(output_filename, frame)
                if num:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, mid1)
                    ret, frame = cap.read()
                    output_filename = os.path.join(output_folder, f'{video_filename}_{str(start_list[-2]/fps)}_{str(num*2-1)}.jpg')
                    cv2.imwrite(output_filename, frame)
                num = num + 1

    flag_vec = current_vec
    flag_time = current_time
    current_time += fps * interval
    print(current_time)


mid = (total_frames + start_list[-1])/2
cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
ret, frame = cap.read()
output_filename = os.path.join(output_folder, f'{video_filename}_{str(start_list[-1]/fps)}.jpg')
cv2.imwrite(output_filename, frame)

# 计算处理时间
end_time = time.time()
print("Time cost: ", end_time - start_time, "s")

# 输出转场时间
for i in start_list:
    print(i / fps)
cap.release()
cv2.destroyAllWindows()

# 模型调用次数
print("模型调用次数: ", times)