
import sys
import cv2
import os
from model import *
from PIL import Image
import torch
import time
base_folder = '../video_imgs'

def get_vec(frame):
    with torch.no_grad():
        image = preprocess(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))).unsqueeze(0)
        vec = model.encode_image(image.to(device))
    vec /=vec.norm(dim=-1, keepdim=True)
    return torch.tensor(vec.cpu().detach().numpy())

# 获取场景的特征图片
def get_scene_features(cap,l,r,fps,video_filename,dis,output_folder):
    mid = (l + r)/2
    # 如果该场景长度较长，多获取几张图片,设定为取距离中间长度为dis秒的倍数的图片,如当dis为4时，对于10秒的场景，会取5秒中间的图片，再取1秒和9秒的图片
    num = 0
    print(l,r,fps)
    while mid - dis*fps >= l:
        mid -= dis*fps
        print(mid)
    while mid < r:
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        if not ret:
            break
        output_filename = os.path.join(output_folder, f'{video_filename}_{(l/fps)//60:.0f}m{(l/fps)%60}s_{str(num)}.jpg')
        cv2.imwrite(output_filename, frame)
        num = num + 1
        mid += dis*fps
        print(num)

# interval:采样的时间间隔1表示1s
# stand_pro:判断的标准概率，小于该概率视为不同
# dis：影响每个场景采取的特征图片数量
def get_video_features(video_path,interval,stand_pro,dis):


    video_filename = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(base_folder, video_filename)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频，请检查视频路径或视频文件")
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
        st = time.time()
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_time)
        print(time.time()-st)
        ret, frame = cap.read()
        if not ret:
            break

        # 获取当前图片的矩阵
        current_vec = get_vec(frame)

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
                get_scene_features(cap,l,r,fps,video_filename,dis,output_folder)
                

        flag_vec = current_vec
        flag_time = current_time
        current_time += fps * interval
        print(current_time)

    l = start_list[-1]
    r = total_frames
    get_scene_features(cap,l,r,fps,video_filename,dis,output_folder)
    for i in range(0,len(start_list)):
        start_list[i] = start_list[i] / fps
    cap.release()
    cv2.destroyAllWindows()
    print(start_list)
    return start_list

if __name__ == "__main__":
    # python video_process.py {video_name}
    # 如果没有输入视频名称，则退出
    if(len(sys.argv) < 2):
        print("执行格式为 python video_process.py $video_path$")
        print("请输入视频名称")
        exit()
    video_path = sys.argv[1]
    start_list = get_video_features(video_path,1,0.85,4)
    
    
