import pandas as pd
import numpy as np
import torch
import cn_clip.clip as clip
from model import *

# 加载模型和预处理函数
# device = "cpu"
# model_name = "RN50" # "RN50" "ViT-B-16"
# pth = "img_vectors_output_" + model_name + ".pth"
# model, preprocess = clip.load_from_name(model_name, device=device, download_root='../model')
# model.eval()

def embed_text(row):
    text = row['text']
    input = clip.tokenize([text]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(input)
        text_features /= text_features.norm(dim=-1, keepdim=True) 
    return text_features.squeeze().numpy()

def text_embedding(df):
    df['vec'] = df.apply(embed_text, axis=1)
    text_vectors = torch.tensor(df['vec'].tolist())
    return text_vectors

def get_sim(image_features, text_features):
    with torch.no_grad():
        logit_scale = model.logit_scale.exp()
        logits_per_image = logit_scale * image_features @ text_features.t()
        logits_per_text = logits_per_image.t()

    return logits_per_image, logits_per_text

def get_sim_probs(img_vectors, text_vectors):
    with torch.no_grad():
        logits_per_image, logits_per_text = get_sim(img_vectors, text_vectors)
        # print(logits_per_text) # tensor([[38.7685, 43.4451, 41.1568,  ..., 49.4177, 46.4309, 48.0733]])

        # 返回logits_per_text中值大于50的排好序的probs和index
        # 从大到小排序
        index = logits_per_text[0].argsort(descending=True)
        # 取出大于50的index
        index = index[logits_per_text[0][index] > 40]
        # print(index)
        # 取出对应的probs
        probs = logits_per_text[0][index]
        # 将probs_t转换为numpy
        probs = probs.cpu().numpy()
        # print(probs)

        index = index.tolist()

        # probs = logits_per_text.softmax(dim=-1).cpu().numpy()
    return probs, index