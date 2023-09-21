import pandas as pd
import torch
import time
from text_process import *

def search_function(input_text):
    print(input_text)
    # 计算查询时间
    start_time = time.time()

    data = {
        'text': [input_text],
    }
    df = pd.DataFrame(data)
    text_vectors = text_embedding(df)
    img_vectors = torch.load(pth)

    probs = get_sim_probs(img_vectors, text_vectors)
    # print("Label probs:", probs)  # [[1.268734e-03 5.436878e-02 6.795761e-04 9.436829e-01]]

    index = probs[0].argsort()[-9:][::-1]
    filepos = list()
    for j in index:
        df = pd.read_csv('all_img_path.csv')
        filepos.append(df.loc[j].file_name)
    
    print(filepos)

    # 计算查询时间
    end_time = time.time()
    print("Time cost: ", end_time - start_time, "s")
    print("init successfully")
    return filepos