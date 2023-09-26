import gradio as gr
from readme import introduction
from init import init
from search import *
from image_upload import *
from video_upload import upload_video_path
from data_manage import *

examples = [
    ["国庆"],
    ["星空中的浪花"],
    ["最美逆行者"],
    ["考生在进入考点时与母亲拥抱。"],
    ["日本福岛第一核电站和核污水储水罐"],
    ["下午，我穿着最喜欢的蓝色衣服，用自己的相机在那迷人的深圳湾记录着它的美丽。"],
    ["考试期间，还将启用无线信号监测设备，对考点周边可疑信号进行巡回监测，严防各类高科技舞弊。"],
    ["方阵如山，气贯长虹。女兵方队、院校科研方队、预备役部队方队、民兵方队、文职人员方队阔步前行，展现了人民军队威武之师、文明之师、和平之师的良好形象。"],
    ["备受关注的东风-41核导弹方队通过天安门时，不少人流下激动的泪水。作为我国战略核力量的中流砥柱，它以凛然的气势和庞大的体形，在世界面前首次亮相。"]
]

login_status = False
img_database_name = []

def login(user_name):
    global login_status
    global img_database_name
    login_status = True
    img_database_name = get_img_database_name(user_name)
    if img_database_name == []:
        output_info="当前用户为："+user_name+"，但该用户没有图库！"
    else:
        output_info="当前用户为："+user_name
    return gr.Dropdown.update(choices=img_database_name, value=[], info=output_info, interactive=True)

def search(text_input, user_name, img_database_selector):
    global login_status
    if login_status == False or len(img_database_selector) == 0:
        return []
    filepos = search_function(text_input, user_name, img_database_selector)
    return filepos

page_id = 1

def pre_page():
    global page_id
    if page_id > 1:
        page_id -= 1
    filepos = imgs_page(page_id)
    return filepos

def next_page():
    global page_id
    page_id += 1
    filepos = imgs_page(page_id)
    if len(filepos) == 0:
        page_id -= 1
        filepos = imgs_page(page_id)
    return filepos

with gr.Blocks() as image_search:
    gr.Markdown("<h1 align='center'> 述图（Real Imaging） </h1>")
    gr.Markdown("述图（Real Imaging）是一款致力于成为图片视频检索领域的 Everything 检索工具，为用户提供了便捷的方式来查找与描述性文本相匹配的图片和视频段。")
    gr.Markdown("此为述图的demo版本，仅提供了演示使用的部分图库图片。")
    with gr.Row():
        with gr.Column(scale=1):
            # 登录
            user_name = gr.Textbox(value="wave", label="用户名")
            login_btn = gr.Button("登录")
            # 图库选择（多选）
            img_database_selector = gr.Dropdown(choices=img_database_name, multiselect=True, every=True ,label="用户图库", info="未登录", interactive=False)
            # 搜索
            text = gr.Textbox(value="星空中的浪花", label="输入一段图片描述文字，搜索图库中与其最匹配的图片")
            search_btn = gr.Button("搜索")
            pre_page_btn = gr.Button("上一页")
            next_page_btn = gr.Button("下一页")
            text_input = text
            gr.Examples(examples, inputs=text_input)
        with gr.Column(scale=4):
            img_searching_result = gr.Gallery(label="检索结果为：").style(grid=4, height=750)
    # 登录后更新图库选项
    login_btn.click(login, inputs=user_name, outputs=img_database_selector)

    search_btn.click(search, inputs=[text_input, user_name, img_database_selector], outputs=img_searching_result)
    pre_page_btn.click(pre_page, outputs=img_searching_result)
    next_page_btn.click(next_page, outputs=img_searching_result)

with gr.Blocks() as file_upload:
    with gr.Row():
        with gr.Column(scale = 2):
            gr.Markdown("# 图片上传")
            gr.Markdown("## 图片或图片压缩包上传")
            img_file = gr.File(type="file", label="上传图片或图片压缩包", height=100)
            upload_img_file_btn = gr.Button("图片文件上传")
            img_process_resultA = gr.Label()
            gr.Markdown("## 新增本地图片图库数据")
            new_picture_folder_name = gr.Textbox(value="D:\\Pictures\\", label="新图所在文件夹路径")
            update_img_folder_path_btn = gr.Button("更新图库数据") 
            img_process_resultB = gr.Label()
        with gr.Column(scale = 2):
            gr.Markdown("# 视频上传")
            # video_file = gr.File(type="file", label="上传图片或图片压缩包", height=100)
            # upload_video_file_btn = gr.Button("视频文件上传")
            # video_process_resultA = gr.Label()
            gr.Markdown("## 新增本地视频数据")
            new_video_path_name = gr.Textbox(value="../videos/", label="新图所在文件夹路径")
            update_video_path_btn = gr.Button("增加视频数据")
            img_process_resultB = gr.Label()
    upload_img_file_btn.click(upload_img_file, inputs=[img_file], outputs=img_process_resultA)
    inputs_new_picture_folder_path = new_picture_folder_name
    update_img_folder_path_btn.click(upload_img_folder_path, inputs=inputs_new_picture_folder_path ,outputs=img_process_resultB)
    # upload_video_file_btn.click(upload_video_file, inputs=[video_file], outputs=video_process_result)
    inputs_new_video_path = new_video_path_name
    update_video_path_btn.click(upload_video_path, inputs=inputs_new_video_path ,outputs=img_process_resultB)

with gr.Blocks() as introduce:
    gr.Markdown(introduction)
    gr.Markdown("## 初始化")
    gr.Markdown("首次运行时，需执行 init.py 或点击“初始化”按钮以初始化图库。")
    init_btn = gr.Button("初始化")
    outputs = gr.outputs.Label()
    init_btn.click(init, outputs=outputs)


if __name__ == "__main__":
    gr.close_all()
    with gr.TabbedInterface(
        [image_search, file_upload, introduce],
        ["图库检索", "文件上传", "应用介绍"],
    ) as interface:
        interface.launch(inline=True, share=False)