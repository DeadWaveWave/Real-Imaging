# -*- coding: utf-8 -*-  

# 导入相应的包  
import numpy as np  
from pymilvus import CollectionSchema, FieldSchema, DataType, Collection,connections,utility
import os
import pandas as pd
import torch
from image_process import image_generator
from model import *
from PIL import Image
from text_process import text_embedding

# 初始化一个Milvus类，以后所有的操作都是通过milvus来的  
connections.connect(
  alias="default", 
  host='localhost', 
  port='19530'
)
collection = Collection("img")

def create_img():
  img_id = FieldSchema(name="img_id",dtype=DataType.INT64,is_primary=True)
  img_path = FieldSchema(name="img_path",dtype=DataType.VARCHAR,max_length=200)
  img_vec = FieldSchema(name="img_vec",dtype=DataType.FLOAT_VECTOR,dim=1024)

  schema = CollectionSchema(
      fields=[img_id,img_path,img_vec],
  )

  Collection(
      name = "img",
      schema=schema,
  )

def insert_img(img_id,img_path,img_vec):
  data = [
      [img_id],
      [img_path],
      img_vec
  ]
  collection.insert(data)
  data = []


def create_index():
  index_params = {
    "metric_type":"L2",
    "index_type":"IVF_FLAT",
    "params":{"nlist":1024}
  }
  collection = Collection("img")
  collection.create_index(
    field_name="img_vec", 
    index_params=index_params,
    index_name="vec_index"
  )

def search_img(search_vec): 
  search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
  collection = Collection("img")
  collection.load()
  res = collection.search(data=[search_vec],anns_field="img_vec",limit=9,param=search_params,output_fields=["img_id","img_path"])
  return res

def drop_img():
  utility.drop_collection("img")

def load_img():
  id = 0
  for root, dirs, files in os.walk("../data"):
    for file in files:
        id = id + 1
        if not file.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
            continue
        file_path = os.path.join(root, file)
        with torch.no_grad():
          image = preprocess(Image.open(file_path)).unsqueeze(0)
          img_vec = model.encode_image(image.to(device))
        img_vec /= img_vec.norm(dim=-1, keepdim=True)
        img_vec = img_vec.cpu().detach().numpy()
        insert_img(id,file_path,img_vec)
        print(id)

def milvus_search_text(text):
    data = {
        'text': [text],
    }
    df = pd.DataFrame(data)
    text_vectors = text_embedding(df).tolist()
    for i in range(0, len(text_vectors)):
       text_vectors[i] = text_vectors[i]
    res = search_img(text_vectors[0])
    img_path = []
    for hit in res[0]:
        print(hit.entity.get("img_path"))
        img_path.append(hit.entity.get("img_path"))
    return img_path

if __name__ == "__main__":
    # drop_img()
    # create_img()
    # create_index()
    # load_img()
    milvus_search_text("wave")