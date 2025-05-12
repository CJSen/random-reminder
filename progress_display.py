#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ProgressDisplay(QWidget):
    """进度显示组件，包含三个进度条：专注时间、提醒间隔和休息时间"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        main_layout = QVBoxLayout(self)

        # 创建三个进度显示组件
        self.focus_progress = self._create_progress_group("专注进度", 90)
        self.reminder_progress = self._create_progress_group("下次提醒")
        self.break_progress = self._create_progress_group("休息时间", 10)

        # 设置进度条初始范围
        self.focus_progress["progress_bar"].setRange(0, 90)  # 默认90分钟
        self.reminder_progress["progress_bar"].setRange(0, 100)
        self.break_progress["progress_bar"].setRange(0, 10)  # 默认10秒

        # 添加到主布局 - 重新调整顺序，让专注进度在最上面
        main_layout.addLayout(self.focus_progress["layout"])
        main_layout.addSpacing(10)
        main_layout.addLayout(self.reminder_progress["layout"])
        main_layout.addSpacing(10)
        main_layout.addLayout(self.break_progress["layout"])

    def _create_progress_group(self, title, total_seconds=0):
        """创建一个进度显示组（标题、时间标签和进度条）"""
        layout = QVBoxLayout()

        # 水平布局用于标题和进度条
        h_layout = QHBoxLayout()

        # 标题标签
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 时间标签 - 初始化为0
        time_label = QLabel("")
        if title == "专注进度":
            time_label.setText(f"已专注 0 分钟 / 剩余 {total_seconds} 分钟")
        elif title == "下次提醒":
            time_label.setText("已过 0 秒 / 待确定下次提醒")
        elif title == "休息时间":
            time_label.setText(f"已休息 0 秒 / 剩余 {total_seconds} 秒")

        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        if total_seconds > 0:
            progress_bar.setRange(0, total_seconds)

        # 组织布局
        h_layout.addWidget(title_label)
        h_layout.addStretch(1)

        layout.addLayout(h_layout)
        layout.addWidget(time_label)
        layout.addWidget(progress_bar)

        return {
            "layout": layout,
            "title_label": title_label,
            "time_label": time_label,
            "progress_bar": progress_bar
        }

    def update_focus_progress(self, elapsed_minutes, total_minutes):
        """更新专注时间进度"""
        progress_bar = self.focus_progress["progress_bar"]
        time_label = self.focus_progress["time_label"]

        # 更新进度条
        progress_bar.setRange(0, total_minutes)
        progress_bar.setValue(elapsed_minutes)

        # 更新时间标签
        remaining_minutes = total_minutes - elapsed_minutes
        time_label.setText(f"已专注 {elapsed_minutes} 分钟 / 剩余 {remaining_minutes} 分钟")

    def update_reminder_progress(self, current_seconds, total_seconds):
        """更新提醒间隔进度"""
        progress_bar = self.reminder_progress["progress_bar"]
        time_label = self.reminder_progress["time_label"]

        # 更新进度条
        progress_bar.setRange(0, total_seconds)
        progress_bar.setValue(current_seconds)

        # 更新时间标签
        remaining_seconds = total_seconds - current_seconds
        time_label.setText(f"已过 {current_seconds} 秒 / 剩余 {remaining_seconds} 秒")

    def update_break_progress(self, current_seconds, total_seconds):
        """更新休息时间进度"""
        progress_bar = self.break_progress["progress_bar"]
        time_label = self.break_progress["time_label"]

        # 更新进度条
        progress_bar.setRange(0, total_seconds)
        progress_bar.setValue(current_seconds)

        # 更新时间标签
        remaining_seconds = total_seconds - current_seconds
        time_label.setText(f"已休息 {current_seconds} 秒 / 剩余 {remaining_seconds} 秒")

    def clear_all_progress(self, focus_minutes, rest_seconds=10, interval_seconds=0):
        """重置所有进度显示为0

        Args:
            focus_minutes: 专注时间(分钟)
            rest_seconds: 休息时间(秒)
            interval_seconds: 提醒间隔(秒)，如果为0则显示"待定"
        """
        # 专注时间进度
        self.focus_progress["progress_bar"].setValue(0)
        self.focus_progress["progress_bar"].setMaximum(focus_minutes)
        self.focus_progress["time_label"].setText(f"已专注 0 分钟 / 剩余 {focus_minutes} 分钟")

        # 提醒间隔进度
        self.reminder_progress["progress_bar"].setValue(0)
        if interval_seconds > 0:
            self.reminder_progress["progress_bar"].setMaximum(interval_seconds)
            self.reminder_progress["time_label"].setText(f"已过 0 秒 / 剩余 {interval_seconds} 秒")
        else:
            # 重置为一个默认值，避免进度条异常
            self.reminder_progress["progress_bar"].setMaximum(100)
            self.reminder_progress["time_label"].setText("已过 0 秒 / 待确定下次提醒")

        # 休息时间进度
        self.break_progress["progress_bar"].setValue(0)
        self.break_progress["progress_bar"].setMaximum(rest_seconds)
        self.break_progress["time_label"].setText(f"已休息 0 秒 / 剩余 {rest_seconds} 秒")