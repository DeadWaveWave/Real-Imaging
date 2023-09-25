import pandas as pd
import torch
import time
from text_process import *

index = list()

def search_function(input_text):
    global index
    print(input_text)
    # 计算查询时间
    start_time = time.time()

    data = {
        'text': [input_text],
    }
    df = pd.DataFrame(data)
    text_vectors = text_embedding(df)
    img_vectors = torch.load(pth)

    probs, index = get_sim_probs(img_vectors, text_vectors)
    # print("Label probs:", probs)  # [[1.268734e-03 5.436878e-02 6.795761e-04 9.436829e-01]]

    # 对probs进行排序，然后将可能性高于85%的标签取出
    # index = probs[0].argsort()[-9:][::-1]
    # for i in range(len(probs[0])):
    #     if probs[0][i] > 0.85:
    #         index.append(i)

    # 取出前9个index对应的图片路径
    # imgs_index_list = index[:9]
    # df = pd.read_csv('all_img_path.csv')
    # filepos = list()
    # for j in imgs_index_list:
    #     filepos.append(df.loc[j].file_name)
    filepos = imgs_page(1)
    
    # 计算查询时间
    end_time = time.time()
    print("Time cost: ", end_time - start_time, "s")
    print("init successfully")
    return filepos


def imgs_page(page_id):
    global index
    imgs_index_list = index[12*(page_id-1):12*page_id]
    # df = pd.read_csv('all_img_path.csv')
    filepos = list()
    df = pd.read_csv('all_img_path.csv')
    for j in imgs_index_list:
        filepos.append(df.loc[j].file_name)

    print(filepos)
    return filepos