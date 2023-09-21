import cn_clip.clip as clip

device = "cpu"
model_name = "RN50" # "RN50" "ViT-B-16"
pth = "img_vectors_output_" + model_name + ".pth"
model, preprocess = clip.load_from_name(model_name, device=device, download_root='../model')
model.eval()