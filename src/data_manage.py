import os
import pandas as pd

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