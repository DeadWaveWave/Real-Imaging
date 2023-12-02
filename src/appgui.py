from PyQt6 import QtWidgets, QtCore, QtGui
from PIL import Image, ImageDraw, ImageFont, ImageQt
from search import *
import sys
import time

def get_library_names():
    return ["004", "005", "006", "007"]


class MainWindow(QtWidgets.QMainWindow):
    def centerOnScreen(self):
        resolution = QtGui.QGuiApplication.primaryScreen().geometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                (resolution.height() / 2) - (self.frameSize().height() / 2))

    def resizeWindow(self):
        self.resize(1000, 1000)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')
        file_option1 = file_menu.addAction('选项1')
        file_option2 = file_menu.addAction('选项2')

        # 介绍菜单
        intro_menu = menubar.addMenu('介绍')
        intro_option = intro_menu.addAction('关于我们')

    def create_library_list(self):
        self.library_list = QtWidgets.QListWidget()
        self.library_list.addItems(get_library_names())  # 假设 get_library_names() 方法返回所有的图库名称
        self.library_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        return self.library_list

    def create_image_view(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setSceneRect(0, 0, 1250, 750)
        # self.view.setAlignment(QtCore.Qt.AlignCenter)
        return self.view

    def create_text_input(self):
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.setPlaceholderText('请输入文字')
        return self.text_input

    def create_search_button(self):
        self.search_button = QtWidgets.QPushButton('搜索')
        self.search_button.clicked.connect(self.search_image)
        return self.search_button

    def search_image(self):
        text = self.text_input.text()
        library_names = [item.text() for item in self.library_list.selectedItems()]

        image_size = 250  # 设置图片的大小
        row = 0
        column = 0

        self.scene.clear()

        if len(library_names) == 0:
            return
        else:
            image_paths = search_function(text, "wave", library_names)
            for image_path in image_paths:
                # get img size
                st = time.time()
                pil_image = Image.open(image_path)
                # resize image to 50% of original size
                width = 200
                height = int((pil_image.height / pil_image.width) * width)
                pil_image = pil_image.resize((width, height))
                # open image
                # Convert Pillow image to QImage
                image_bytes = pil_image.convert("RGB").tobytes()
                print("open image time: ", time.time() - st)
                qt_image = QtGui.QImage(image_bytes, pil_image.width, pil_image.height, QtGui.QImage.Format.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qt_image)
                # create item
                pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)
                pixmap_item.setPos(column * image_size, row * image_size)  # 设置图片的位置
                self.scene.addItem(pixmap_item)
                column += 1
                if column >= 4:
                    column =0
                    row += 1

        self.view.update()
        self.view.show()

    def create_layout(self):
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.create_library_list())
        h_layout.addWidget(self.create_image_view())
        self.layout.addWidget(self.create_text_input())
        self.layout.addWidget(self.create_search_button())
        self.layout.addLayout(h_layout)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('述图')
        self.setGeometry(100, 100, 1500, 800)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(self.layout)

        self.create_menu_bar()
        self.create_layout()
        
        self.centerOnScreen()
        self.resizeWindow()
       
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # 使用资源文件管理器加载资源
    # QtCore.QResource.registerResource('resources.qrc')
    window = MainWindow()
    window.show()
    # app.exec()
    sys.exit(app.exec())
