import gradio as gr
from readme import introduction
from init import init
from search import *
from image_upload import upload_file

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
    gr.Markdown("述图（Real Imaging）是一款基于Chinese-CLIP构建的高效的文本-图库检索工具应用，为用户提供了便捷的方式来查找与描述性文本相匹配的图片。")
    gr.Markdown("此为述图的demo版本，仅提供了演示使用的部分图库图片。")
    with gr.Row():
        with gr.Column(scale=2):
            text = gr.Textbox(value="星空中的浪花", label="输入一段图片描述文字，搜索图库中与其最匹配的图片")
            btn = gr.Button("搜索")
            # with gr.Row():
                # with gr.Column(scale=1):
                #     gr.Label(label=str(page_id))
                # page_id = gr.outputs.Number(label="页数")
                # with gr.Column(scale=1):
                # gr.Markdown("当前页数：" + str(page_id))
            pre_page_btn = gr.Button("上一页")
                # with gr.Column(scale=1):
            next_page_btn = gr.Button("下一页")
            inputs = [text]
            gr.Examples(examples, inputs=inputs)
        with gr.Column(scale=60):
            out = gr.Gallery(label="检索结果为：").style(grid=4, height=700)
    btn.click(search_function, inputs=inputs, outputs=out)
    pre_page_btn.click(pre_page, outputs=out)
    next_page_btn.click(next_page, outputs=out)

image_upload = gr.Interface(upload_file,
                              gr.inputs.File(type="file" ,label="上传图片"),
                              gr.outputs.Label(),
                              title="述图（Real Imaging）",
                              description="上传图片到图库（仅支持单张图片或 zip 压缩包，图片形式目前仅限 .jpg, .jpeg, .png）"
                              )

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
        [image_search, image_upload, introduce],
        ["图库检索", "图片上传", "应用介绍"],
    ) as interface:
        interface.launch(inline=True, share=False)