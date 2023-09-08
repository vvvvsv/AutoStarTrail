from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QPushButton, \
    QGridLayout, QLabel, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt

from startrail import StarTrail

import natsort
import time
import sys
import os

class MyThread(QThread):
    # 信号
    changeValue = pyqtSignal(int)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.input_filepathes = []
        self.output_path = None
        self.decay = None
        self.output_filepath = None
        self.start_time = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AutoStarTrail")
        self.resize(600, 350)
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        self.input_button = QPushButton("导入文件")
        main_layout.addWidget(self.input_button, 0, 0, 1, 2)
        self.input_button.clicked.connect(self.__open_input_folder)
        self.input_label = QLabel("您已导入0张图片（支持.jpg .jpeg .png .bmp）")
        main_layout.addWidget(self.input_label, 0, 2, 1, 2)

        self.output_button = QPushButton("导出文件位置")
        main_layout.addWidget(self.output_button, 1, 0, 1, 2)
        self.output_button.clicked.connect(self.__open_output_folder)

        self.output_label = QLabel("您将要导出到：")
        self.output_label.setWordWrap(True)
        main_layout.addWidget(self.output_label, 1, 2, 1, 2)

        tmp_label = QLabel("衰减：")
        main_layout.addWidget(tmp_label, 2, 0)

        doubleVal = QDoubleValidator()
        doubleVal.setRange(0.0,1.0)
        doubleVal.setNotation(QDoubleValidator.StandardNotation) # 标准显示
        doubleVal.setDecimals(5)
        self.decay_line_edit = QLineEdit()
        self.decay_line_edit.setPlaceholderText("请填入0到1的小数，以0.9到1.0为佳，数字越大星轨拖尾越长")
        self.decay_line_edit.setText("1.0")
        self.decay_line_edit.setValidator(doubleVal)
        main_layout.addWidget(self.decay_line_edit, 2, 1, 1, 3)

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
        self.video_line_edit.setPlaceholderText("支持.mp4，默认帧率25")
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

        self.input_filepathes = natsort.natsorted(self.input_filepathes, alg=natsort.PATH)
        # 修改文本
        self.input_label.setText(f"您已导入{image_count}张图片（支持.jpg .jpeg .png .bmp）")

    def __open_output_folder(self):
        self.output_path = QFileDialog.getExistingDirectory(self,
                  "选择导出文件位置",
                  "./")
        self.output_label.setText(f"您将要导出到： {self.output_path}/")

    # mode 为 "image", "video", or "frame"
    def __output_ok(self, mode):
        if(len(self.input_filepathes) == 0):
            QMessageBox.critical(self, "错误", "未导入图片！")
            return False
        if self.output_path is None:
            QMessageBox.critical(self, "错误", "未设置导出文件位置！")
            return False
        self.decay = self.decay_line_edit.text()
        try:
            self.decay = float(self.decay)
            if(self.decay < 0 or self.decay > 1):
                QMessageBox.critical(self, "错误", "衰减值应为0到1的小数，以0.9到1.0为佳，数字越大星轨拖尾越长")
                return False
        except ValueError:
            QMessageBox.critical(self, "错误", "衰减值应为0到1的小数，以0.9到1.0为佳，数字越大星轨拖尾越长")
            return False

        if mode == 'image':
            try:
                filename = self.image_line_edit.text()
                file_extension = os.path.splitext(filename)[-1].lower()
                if file_extension not in [".jpg", ".jpeg", ".png", ".bmp"]:
                    QMessageBox.critical(self, "错误", "支持输出.jpg .jpeg .png .bmp")
                    return False
                filepath = os.path.join(self.output_path, filename)
                if(os.path.exists(filepath)):
                    QMessageBox.critical(self, "错误", f"{filename} 已存在！")
                    return False
                self.output_filepath = filepath
            except:
                QMessageBox.critical(self, "错误", "支持输出.jpg .jpeg .png .bmp")
                False
        elif mode == 'video':
            try:
                filename = self.video_line_edit.text()
                file_extension = os.path.splitext(filename)[-1].lower()
                if file_extension not in [".mp4"]:
                    QMessageBox.critical(self, "错误", "支持输出.mp4")
                    return False
                filepath = os.path.join(self.output_path, filename)
                if(os.path.exists(filepath)):
                    QMessageBox.critical(self, "错误", f"{filename} 已存在！")
                    return False
                self.output_filepath = filepath
            except:
                QMessageBox.critical(self, "错误", "支持输出.mp4")
                False
        elif mode == 'frame':
            self.output_filepath = os.path.join(self.output_path, self.frame_line_edit.text())
            if(os.path.exists(self.output_filepath) and len(os.listdir(self.output_filepath)) != 0):
                QMessageBox.critical(self, "错误", "导出文件夹非空！")
                self.output_filepath = None
                return False
        return True

    def __output_preprocess(self):
        self.progress_bar.setValue(0)
        self.input_button.setDisabled(True)
        self.output_button.setDisabled(True)
        self.decay_line_edit.setDisabled(True)
        self.image_button.setDisabled(True)
        self.image_line_edit.setDisabled(True)
        self.video_button.setDisabled(True)
        self.video_line_edit.setDisabled(True)
        self.frame_button.setDisabled(True)
        self.frame_line_edit.setDisabled(True)

    def __output_postprocess(self):
        self.progress_bar.setValue(0)
        self.remain_time_label.setText("剩余时间：")
        self.input_button.setDisabled(False)
        self.output_button.setDisabled(False)
        self.decay_line_edit.setDisabled(False)
        self.image_button.setDisabled(False)
        self.image_line_edit.setDisabled(False)
        self.video_button.setDisabled(False)
        self.video_line_edit.setDisabled(False)
        self.frame_button.setDisabled(False)
        self.frame_line_edit.setDisabled(False)

    def __output_image(self):
        if not self.__output_ok("image"):
            return
        self.__output_preprocess()
        self.__star_trail_with_thread("image")

    def __output_video(self):
        if not self.__output_ok("video"):
            return
        self.__output_preprocess()
        self.__star_trail_with_thread("video")

    def __output_frame(self):
        if not self.__output_ok("frame"):
            return
        self.__output_preprocess()
        self.__star_trail_with_thread("frame")

    def handle_signal(self, val):
        if val == -1:
            # 线程结束
            QMessageBox.information(self, "完成", "导出完成")
            self.__output_postprocess()
        else:
            self.progress_bar.setValue(val)
            if val > 0:
                eta = (time.time() - self.start_time) / val * (100 - val) + 3
                eta = int(eta)
                hours = eta // 3600
                eta -= hours * 3600
                mins = eta // 60
                eta -= mins * 60
                secs = eta
                outstr = "剩余时间："
                if(hours != 0):
                    outstr += str(hours) + "小时"
                if(mins != 0):
                    outstr += str(mins) + "分钟"
                outstr += str(secs) + "秒"
                self.remain_time_label.setText(outstr)

    def __star_trail_with_thread(self, mode):
        self.thread = MyThread()
        if mode == 'image':
            self.thread.run = lambda: StarTrail(self.input_filepathes, self.output_filepath, self.decay).image(self.thread)
        elif mode == 'video':
            self.thread.run = lambda: StarTrail(self.input_filepathes, self.output_filepath, self.decay).video(self.thread)
        elif mode == 'frame':
            self.thread.run = lambda: StarTrail(self.input_filepathes, self.output_filepath, self.decay).frame(self.thread)
        self.thread.changeValue.connect(lambda val: self.handle_signal(val))
        self.thread.start()
        self.start_time = time.time()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())