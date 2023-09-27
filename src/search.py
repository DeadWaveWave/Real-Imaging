import sys
import pandas as pd
import torch
import time
import os
from text_process import *
from video_process import video_imgs_folder_path

index = list()

def search_function(input_text, user_name, img_database_name):
    global index
    print("input_text: ", input_text)
    print("user_name: ", user_name)
    print("img_database_name: ", img_database_name)
    # 计算查询时间
    start_time = time.time()

    data = {
        'text': [input_text],
    }
    text_df = pd.DataFrame(data)

    # 将文本向量化
    text_vectors = text_embedding(text_df)

    # 将图片信息拼接在一起
    img_vectors = torch.empty((0, 1024))
    df = pd.DataFrame()
    for i in range(len(img_database_name)):
        # 拼接向量
        pth = os.path.join("../data", user_name, img_database_name[i], "img_vectors_output_" + model_name + ".pth")
        new_img_vectors = torch.load(pth)
        img_vectors = torch.cat((img_vectors, new_img_vectors), 0)
        # 拼接地址
        csv_path = os.path.join("../data", user_name, img_database_name[i], "img_paths.csv")
        new_df = pd.read_csv(csv_path)
        df = pd.concat([df, new_df], axis=0, ignore_index=True)
    # 保存 csv 文件
    df.to_csv("all_img_path.csv", index=False)

    probs, index = get_sim_probs(img_vectors, text_vectors)
    # print("Label probs:", probs)  # [[1.268734e-03 5.436878e-02 6.795761e-04 9.436829e-01]]

    # 取出前9个index对应的图片路径
    filepos = imgs_page(1)
    
    # 计算查询时间
    end_time = time.time()
    print("Time cost: ", end_time - start_time, "s")
    print("init successfully")
    return filepos


def search_video(input_text):
    global video_imgs_folder_path,index

    data = {
        'text': [input_text],
    }
    text_df = pd.DataFrame(data)

    # 将文本向量化
    text_vectors = text_embedding(text_df)

    csv_path = os.path.join(video_imgs_folder_path[0], "img_paths.csv")
    video_imgs_pth = os.path.join(video_imgs_folder_path[0], "img_vectors_output_" + model_name + ".pth")
    img_vectors = torch.load(video_imgs_pth)

    probs, index = get_sim_probs(img_vectors, text_vectors)

    filepos = imgs_page(1,csv_path)
    first = filepos[0]
    print(first)
    basename = str(os.path.splitext(os.path.basename(first))[0])
    print(basename)
    num = basename.split("_")[2]
    print(num)
    video_path = os.path.join(video_imgs_folder_path[0]+'_videos',num+'.mp4')
    print(video_path)
    return video_path


def imgs_page(page_id, csv_path='all_img_path.csv'):
    global index
    imgs_index_list = index[12*(page_id-1):12*page_id]
    filepos = list()
    df = pd.read_csv(csv_path)
    for j in imgs_index_list:
        filepos.append(df.loc[j].file_name)

    print(filepos)
    return filepos


if __name__ == "__main__":
    # python search.py {text} {user_name} {img_database_name}
    # 如果没有输入文本，则退出
    if(len(sys.argv) < 4):
        print("执行格式为 python search.py \"text\" \"user_name\" \"img_database_name\"")
        print("请输入文本")
        exit()
    # text = sys.argv[1]
    start_list = search_function(sys.argv[1], [sys.argv[2]], [sys.argv[3]])