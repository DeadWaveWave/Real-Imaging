from PyQt5 import QtWidgets, QtGui
from PIL import Image, ImageDraw, ImageFont, ImageQt
from search import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('述图')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(self.layout)

        # 创建菜单栏
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')
        file_option1 = file_menu.addAction('选项1')
        file_option2 = file_menu.addAction('选项2')
        
        # 文件菜单
        file_menu = menubar.addMenu('介绍')
        file_option1 = file_menu.addAction('关于我们')

        # 输入框
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.setPlaceholderText('请输入文字')
        self.layout.addWidget(self.text_input)

        # 图片显示区域
        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setSceneRect(0, 0, 800, 600)
        self.layout.addWidget(self.view)

        # 搜索按钮
        self.search_button = QtWidgets.QPushButton('搜索')
        self.search_button.clicked.connect(self.search_image)
        self.layout.addWidget(self.search_button)

    def search_image(self):
        text = self.text_input.text()
        image_paths = search_function(text, "wave", ["007"])

        image_size = 250  # 设置图片的大小
        row = 0
        column = 0

        for image_path in image_paths:
            pixmap = QtGui.QPixmap(image_path).scaled(image_size, image_size)  # 设置图片的大小
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            item.setPos(column * image_size, row * image_size)  # 设置图片的位置

            self.scene.addItem(item)
            column += 1
            if column >= 3:
                column =0
                row += 1

        self.view.update()
        self.view.show()

       

app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec_()
