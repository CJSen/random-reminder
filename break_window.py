#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
)


class CircularProgressBar(QWidget):
    """圆形进度条"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 100
        self.text = "20:00"  # 添加文本属性
        self.setMinimumSize(250, 250)

    def setValue(self, value):
        """设置进度值 (0-100)"""
        self.value = value
        self.update()  # 触发重绘

    def setText(self, text):
        """设置显示的文本"""
        self.text = text
        self.update()  # 触发重绘

    def paintEvent(self, event):
        """重绘事件"""
        width = self.width()
        height = self.height()
        size = min(width, height)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制背景圆 - 将浮点数转换为整数
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(10)
        painter.setPen(pen)

        # 使用QRect对象，避免浮点数问题
        x = int(width/2 - size/2 + 15)
        y = int(height/2 - size/2 + 15)
        w = int(size - 30)
        h = int(size - 30)

        painter.drawEllipse(x, y, w, h)

        # 绘制进度圆弧
        pen = QPen(QColor(76, 175, 80))  # 绿色
        pen.setWidth(10)
        painter.setPen(pen)

        # 计算角度 (从90度开始，逆时针)
        start_angle = 90 * 16
        span_angle = int(-self.value / 100 * 360 * 16)

        painter.drawArc(x, y, w, h, start_angle, span_angle)

        # 绘制中心文字
        painter.setPen(QColor(50, 50, 50))
        font = QFont()
        font.setPointSize(24)  # 增大字体
        font.setBold(True)    # 设置为粗体
        painter.setFont(font)

        # 计算文本矩形并居中绘制
        rect = painter.boundingRect(x, y, w, h, Qt.AlignmentFlag.AlignCenter, self.text)
        painter.drawText(x, y, w, h, Qt.AlignmentFlag.AlignCenter, self.text)


class BreakWindow(QDialog):
    """休息窗口，显示20分钟的休息倒计时"""

    break_finished = pyqtSignal()  # 休息结束信号
    restart_requested = pyqtSignal()  # 请求重新开始信号

    def __init__(self, parent=None, debug_mode=False):
        super().__init__(parent)
        self.setWindowTitle("休息时间")
        self.setMinimumSize(400, 500)
        self.setModal(True)  # 设置为模态对话框

        # 休息时间 (20分钟 = 1200秒，调试模式下10秒)
        self.debug_mode = debug_mode
        self.total_seconds = 10 if debug_mode else 1200
        self.remaining_seconds = self.total_seconds

        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """设置用户界面"""
        main_layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("休息时间")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title_label)

        # 说明
        if self.debug_mode:
            desc_text = "调试模式：休息10秒钟"
        else:
            desc_text = "请休息20分钟，让大脑得到充分放松"

        desc_label = QLabel(desc_text)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-size: 14pt; margin: 10px;")
        main_layout.addWidget(desc_label)

        # 圆形进度条
        self.progress_bar = CircularProgressBar()

        # 设置初始时间文本
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        initial_time_text = f"{minutes:02d}:{seconds:02d}"
        self.progress_bar.setText(initial_time_text)

        main_layout.addWidget(self.progress_bar, 1)

        # 计时器显示
        self.time_label = QLabel(initial_time_text)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 32pt; font-weight: bold; margin: 20px;")
        main_layout.addWidget(self.time_label)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.exit_btn = QPushButton("退出")
        self.exit_btn.clicked.connect(self.close)

        self.restart_btn = QPushButton("重新开始")
        self.restart_btn.clicked.connect(self.request_restart)

        button_layout.addWidget(self.exit_btn)
        button_layout.addWidget(self.restart_btn)

        main_layout.addLayout(button_layout)

    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 每秒更新一次

    def update_timer(self):
        """更新计时器显示"""
        self.remaining_seconds -= 1

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.break_finished.emit()
            return

        # 更新进度条
        progress = (self.remaining_seconds / self.total_seconds) * 100
        self.progress_bar.setValue(progress)

        # 更新时间显示
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        time_text = f"{minutes:02d}:{seconds:02d}"

        # 更新时间标签和进度条上的文本
        self.time_label.setText(time_text)
        self.progress_bar.setText(time_text)

    def request_restart(self):
        """请求重新开始"""
        self.restart_requested.emit()
        self.close()

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.timer.stop()
        event.accept()