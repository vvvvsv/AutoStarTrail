import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QPushButton, \
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt

from PIL import Image
import numpy as np

class MyThread(QThread):
    # 信号
    changeValue = pyqtSignal(int)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.input_filepathes = []
        self.output_path = None
        self.num_threads = None
        self.decay = None
        self.output_filepath = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AutoStarTrail")
        self.resize(700, 350)
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        self.input_button = QPushButton("导入文件")
        main_layout.addWidget(self.input_button, 0, 0, 1, 2)
        self.input_button.clicked.connect(self.__open_input_folder)
        self.input_label = QLabel("您已导入 0 张图片（支持.jpg .jpeg .png .bmp）")
        main_layout.addWidget(self.input_label, 0, 2, 1, 2)

        self.output_button = QPushButton("导出文件位置")
        main_layout.addWidget(self.output_button, 1, 0, 1, 2)
        self.output_button.clicked.connect(self.__open_output_folder)

        self.output_label = QLabel("您将要导出到：")
        self.output_label.setWordWrap(True)
        main_layout.addWidget(self.output_label, 1, 2, 1, 2)

        tmp_label = QLabel("线程数：")
        main_layout.addWidget(tmp_label, 2, 0)
        self.threads_combo_box = QComboBox()
        self.threads_combo_box.addItems([str(i) for i in range(1,9)])
        main_layout.addWidget(self.threads_combo_box, 2, 1)
        tmp_label = QLabel("衰减：")
        main_layout.addWidget(tmp_label, 2, 2)

        doubleVal = QDoubleValidator()
        doubleVal.setRange(0.0,1.0)
        doubleVal.setNotation(QDoubleValidator.StandardNotation) # 标准显示
        doubleVal.setDecimals(5)
        self.decay_line_edit = QLineEdit()
        self.decay_line_edit.setPlaceholderText("请填入0到1的小数，以0.9到1.0为佳，数字越大星轨拖尾越长")
        self.decay_line_edit.setText("1.0")
        self.decay_line_edit.setValidator(doubleVal)
        main_layout.addWidget(self.decay_line_edit, 2, 3)

        self.image_button = QPushButton("导出图片")
        main_layout.addWidget(self.image_button, 3, 0)
        self.image_button.clicked.connect(self.__output_image)
        tmp_label = QLabel("文件名：")
        main_layout.addWidget(tmp_label, 3, 1)
        self.image_line_edit = QLineEdit()
        self.image_line_edit.setPlaceholderText("支持.jpg .jpeg .png .bmp")
        self.image_line_edit.setText("StarTrail.png")
        main_layout.addWidget(self.image_line_edit, 3, 2, 1, 2)

        self.video_button = QPushButton("导出视频")
        main_layout.addWidget(self.video_button, 4, 0)
        self.video_button.clicked.connect(self.__output_video)
        tmp_label = QLabel("文件名：")
        main_layout.addWidget(tmp_label, 4, 1)
        self.video_line_edit = QLineEdit()
        self.video_line_edit.setPlaceholderText("支持.mp4 .avi .flv")
        self.video_line_edit.setText("StarTrail.mp4")
        main_layout.addWidget(self.video_line_edit, 4, 2, 1, 2)

        self.frame_button = QPushButton("导出视频各帧")
        main_layout.addWidget(self.frame_button, 5, 0)
        self.frame_button.clicked.connect(self.__output_frame)
        tmp_label = QLabel("文件夹名：")
        main_layout.addWidget(tmp_label, 5, 1)
        self.frame_line_edit = QLineEdit()
        self.frame_line_edit.setPlaceholderText("请保证该文件夹不存在或为空")
        self.frame_line_edit.setText("StarTrail")
        main_layout.addWidget(self.frame_line_edit, 5, 2, 1, 2)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.progress_bar, 6, 0, 1, 4)

        self.remain_time_label = QLabel("剩余时间：")
        self.remain_time_label.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.remain_time_label, 7, 0, 1, 4)

    def __open_input_folder(self):
        files, _ = QFileDialog.getOpenFileNames(self,
                  "导入一个或多个文件",
                  "./",
                  "All Files (*);;Image Files (*.jpg *.jpeg *.png *.bmp)")

        self.input_filepathes = []

        image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
        image_count = 0
        # 遍历文件夹中的所有文件
        for filepath in files:
            # 获取文件扩展名
            file_extension = os.path.splitext(filepath)[-1].lower()
            # 检查是否是图像文件
            if file_extension in image_extensions:
                image_count += 1
                self.input_filepathes.append(filepath)

        # 修改文本
        self.input_label.setText(f"您已导入 {image_count} 张图片（支持.jpg .jpeg .png .bmp）")

    def __open_output_folder(self):
        self.output_path = QFileDialog.getExistingDirectory(self,
                  "选择导出文件位置",
                  "./")
        self.output_label.setText(f"您将要导出到： {self.output_path}/")

    # mode 为 "image", "video", or "frame"
    def __output_ok(self, mode):
        if(len(self.input_filepathes) == 0):
            QMessageBox.information(self, "错误", "未导入图片！")
            return False
        if self.output_path is None:
            QMessageBox.information(self, "错误", "未设置导出文件位置！")
            return False
        self.num_threads = int(self.threads_combo_box.currentText())
        self.decay = self.decay_line_edit.text()
        try:
            self.decay = float(self.decay)
            if(self.decay < 0 or self.decay > 1):
                QMessageBox.information(self, "错误", "衰减值应为0到1的小数，以0.9到1.0为佳，数字越大星轨拖尾越长")
                return False
        except ValueError:
            QMessageBox.information(self, "错误", "衰减值应为0到1的小数，以0.9到1.0为佳，数字越大星轨拖尾越长")
            return False

        if mode == 'image':
            try:
                filename = self.image_line_edit.text()
                file_extension = os.path.splitext(filename)[-1].lower()
                if file_extension not in [".jpg", ".jpeg", ".png", ".bmp"]:
                    QMessageBox.information(self, "错误", "支持输出.jpg .jpeg .png .bmp")
                    return False
                filepath = os.path.join(self.output_path, filename)
                if(os.path.exists(filepath)):
                    QMessageBox.information(self, "错误", f"{filename}已存在")
                    return False
                self.output_filepath = filepath
            except:
                QMessageBox.information(self, "错误", "支持输出.jpg .jpeg .png .bmp")
                False
        elif mode == 'video':
            try:
                filename = self.video_line_edit.text()
                file_extension = os.path.splitext(filename)[-1].lower()
                if file_extension not in [".mp4", ".avi", ".flv"]:
                    QMessageBox.information(self, "错误", "支持输出.mp4 .avi .flv")
                    return False
                filepath = os.path.join(self.output_path, filename)
                if(os.path.exists(filepath)):
                    QMessageBox.information(self, "错误", f"{filename}已存在")
                    return False
                self.output_filepath = filepath
            except:
                QMessageBox.information(self, "错误", "支持输出.mp4 .avi .flv")
                False
        elif mode == 'frame':
            self.output_filepath = os.path.join(self.output_path, self.frame_line_edit.text())
            if(os.path.exists(self.output_filepath) and len(os.listdir(self.output_filepath)) != 0):
                QMessageBox.information(self, "错误", "导出文件夹非空！")
                self.output_filepath = None
                return False
        return True

    def __output_preprocess(self):
        pass

    def __output_postprocess(self):
        pass

    def __output_image(self):
        if not self.__output_ok("image"):
            return
        print("ok")
        pass

        # self.__disable_buttons()
        # self.root.overrideredirect(True)
        # # self.root.attributes('-disabled', True)
        # StarTrail(self.root, self.progress_bar).image(self.input_filepathes, self.output_filepath, int(self.threads_combo_box.get()))
        # # self.root.attributes('-disabled', False)
        # self.root.overrideredirect(False)
        # self.__enable_buttons()

    def __output_video(self):
        if not self.__output_ok("video"):
            return
        print("ok")
        pass
        # if not self.__pathes_ok():
        #     return
        # if not self.__decay_ok():
        #     return

        # self.__disable_buttons()
        # StarTrail(self.root, self.progress_bar).video(self.input_filepathes, self.output_filepath, int(self.threads_combo_box.get()), self.decay)
        # self.__enable_buttons()

    def __output_frame(self):
        if not self.__output_ok("frame"):
            return
        print("ok")
        pass
        # if not self.__pathes_ok():
        #     return
        # if not self.__decay_ok():
        #     return

        # self.__disable_buttons()
        # StarTrail(self.root, self.progress_bar).frame(self.input_filepathes, self.output_filepath, int(self.threads_combo_box.get()), self.decay)
        # self.__enable_buttons()


    def startProgressBar(self):
        self.DoWithThread(self.progressbar)

    def DoWithThread(self, progressbar: QProgressBar):
        self.thread = MyThread()
        self.thread.run = lambda: self.ThreadRun(self.thread)
        self.thread.changeValue.connect(lambda val: progressbar.setValue(val))
        self.thread.start()

    def ThreadRun(self, thread):
        dirpath = "LR导出"
        startid = 7939
        endid = 8155
        stride = 10000
        os.makedirs("max_output", exist_ok=True)
        result = None
        result_L = None
        for i in range(startid, endid+1):
            imgpath = os.path.join(dirpath, f"IMG_{i}.jpg")
            img = Image.open(imgpath)
            img_L = img.convert('L')
            img = np.array(img)
            img_L = np.array(img_L)

            if ((i - startid) % stride == 0):
                result = img
                result_L = img_L
            else:
                idx = img_L > result_L
                result[idx] = img[idx]
                result_L[idx] = img_L[idx]

            if ((i + 1 - startid) % stride == 0) or (i == endid):
                Image.fromarray(result).save(f"max_output/IMG_{i}.jpg")
            thread.changeValue.emit(i-startid+1)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())

