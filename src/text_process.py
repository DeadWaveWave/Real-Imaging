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
        probs = logits_per_text.softmax(dim=-1).cpu().numpy()
    return probs