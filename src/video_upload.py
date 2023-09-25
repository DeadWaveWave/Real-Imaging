from video_process import *

def upload_video_path(video_path):
    start_list = get_video_features(video_path,1,0.85,4)
    return "success"