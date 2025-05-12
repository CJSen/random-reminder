#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QDialog,
)

from timer_thread import TimerThread
from sound_manager import SoundManager
from progress_display import ProgressDisplay
from break_window import BreakWindow


class BreakPromptDialog(QDialog):
    """专注周期结束后的提示对话框"""

    def __init__(self, parent=None, focus_time=90):
        super().__init__(parent)
        self.setWindowTitle("专注周期完成")
        self.setMinimumWidth(400)

        # 结果
        self.result_action = "rest"  # 默认选择休息

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel(f"恭喜您完成了{focus_time}分钟的专注!")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 提示
        prompt_label = QLabel("建议您休息20分钟，让大脑充分放松")
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(prompt_label)

        # 按钮
        button_layout = QHBoxLayout()

        self.rest_btn = QPushButton("去休息")
        self.rest_btn.setStyleSheet("font-size: 14pt; padding: 8px;")
        self.rest_btn.clicked.connect(self.choose_rest)

        self.restart_btn = QPushButton("重新开始")
        self.restart_btn.clicked.connect(self.choose_restart)

        button_layout.addWidget(self.restart_btn)
        button_layout.addWidget(self.rest_btn)

        layout.addLayout(button_layout)

    def choose_rest(self):
        """选择休息"""
        self.result_action = "rest"
        self.accept()

    def choose_restart(self):
        """选择重新开始"""
        self.result_action = "restart"
        self.accept()

class MainWindow(QMainWindow):
    """随机提醒应用主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化组件
        self.timer_thread = TimerThread()
        self.sound_manager = SoundManager()

        # 设置UI
        self.setup_ui()
        self.setup_connections()

        # 添加调试信息
        self.is_debug_mode = False

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("随机提醒")
        self.setMinimumSize(450, 400)

        # 主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # 顶部布局（标题和调试模式）
        top_layout = QHBoxLayout()

        # 标题
        title_label = QLabel("随机提醒应用")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")

        # 调试模式复选框
        self.debug_checkbox = QCheckBox("调试模式")
        self.debug_checkbox.setChecked(False)
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)

        # 添加一个弹性空间，将调试模式推到右边
        top_layout.addStretch(1)
        top_layout.addWidget(title_label, 4)  # 给标题更多的空间
        top_layout.addStretch(1)
        top_layout.addWidget(self.debug_checkbox, 0, Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_layout)

        # 设置区域
        settings_layout = QVBoxLayout()

        # 提示音设置
        sound_layout = QHBoxLayout()
        sound_label = QLabel("提示音:")

        # 添加短音效选择
        self.short_sound_radio = QPushButton("短音效")
        self.short_sound_radio.setCheckable(True)
        self.short_sound_radio.setChecked(True)
        self.short_sound_radio.clicked.connect(self.use_short_sound)

        self.long_sound_radio = QPushButton("长音效")
        self.long_sound_radio.setCheckable(True)
        self.long_sound_radio.clicked.connect(self.use_long_sound)

        test_sound_btn = QPushButton("测试")
        test_sound_btn.clicked.connect(self.test_sound)

        sound_layout.addWidget(sound_label)
        sound_layout.addWidget(self.short_sound_radio)
        sound_layout.addWidget(self.long_sound_radio)
        sound_layout.addWidget(test_sound_btn)
        settings_layout.addLayout(sound_layout)

        # 提醒间隔设置
        interval_layout = QHBoxLayout()
        interval_label = QLabel("提醒间隔(秒):")
        self.min_interval_spinbox = QSpinBox()
        self.min_interval_spinbox.setRange(3, 3600)  # 3秒到60分钟
        self.min_interval_spinbox.setValue(300)  # 默认5分钟 = 300秒
        self.min_interval_spinbox.setKeyboardTracking(False)  # 禁用键盘输入实时追踪

        interval_to_label = QLabel("到")

        self.max_interval_spinbox = QSpinBox()
        self.max_interval_spinbox.setRange(5, 3600)  # 5秒到60分钟
        self.max_interval_spinbox.setValue(480)  # 默认8分钟 = 480秒
        self.max_interval_spinbox.setKeyboardTracking(False)  # 禁用键盘输入实时追踪

        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.min_interval_spinbox)
        interval_layout.addWidget(interval_to_label)
        interval_layout.addWidget(self.max_interval_spinbox)
        settings_layout.addLayout(interval_layout)

        # 短休息时间设置
        rest_layout = QHBoxLayout()
        rest_label = QLabel("短休息时间(秒):")
        self.rest_spinbox = QSpinBox()
        self.rest_spinbox.setRange(1, 300)  # 1秒到5分钟
        self.rest_spinbox.setValue(10)  # 默认10秒
        self.rest_spinbox.setKeyboardTracking(False)  # 禁用键盘输入实时追踪
        self.rest_spinbox.valueChanged.connect(self.update_rest_time)

        rest_layout.addWidget(rest_label)
        rest_layout.addWidget(self.rest_spinbox)
        settings_layout.addLayout(rest_layout)

        main_layout.addLayout(settings_layout)

        # 专注时间设置
        focus_layout = QHBoxLayout()
        focus_label = QLabel("专注时间(分钟):")
        self.focus_spinbox = QSpinBox()
        self.focus_spinbox.setRange(1, 180)
        self.focus_spinbox.setValue(90)
        self.focus_spinbox.setKeyboardTracking(False)  # 禁用键盘输入实时追踪
        self.focus_spinbox.valueChanged.connect(self.update_focus_time)

        focus_layout.addWidget(focus_label)
        focus_layout.addWidget(self.focus_spinbox)
        settings_layout.addLayout(focus_layout)

        # 进度显示区域
        self.progress_display = ProgressDisplay()
        main_layout.addWidget(self.progress_display)

        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # 控制按钮
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始")
        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_timer)
        self.stop_btn.setEnabled(False)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        main_layout.addLayout(control_layout)

        self.setCentralWidget(central_widget)

        # 初始化显示
        self.update_focus_time()
        self.update_rest_time()

        # 将配置控件保存到列表中，方便统一管理
        self.config_widgets = [
            self.focus_spinbox,
            self.min_interval_spinbox,
            self.max_interval_spinbox,
            self.rest_spinbox,
            self.debug_checkbox,
            self.short_sound_radio,
            self.long_sound_radio,
            test_sound_btn
        ]

    def setup_connections(self):
        """设置信号连接"""
        self.timer_thread.signal_play_sound.connect(self.play_reminder_sound)
        self.timer_thread.signal_play_short_break_end_sound.connect(self.play_short_break_end_sound)
        self.timer_thread.signal_update_progress.connect(self.update_progress)
        self.timer_thread.signal_break_time.connect(self.show_break_time)
        self.timer_thread.signal_update_reminder_progress.connect(
            self.update_reminder_progress
        )
        self.timer_thread.signal_update_break_progress.connect(
            self.update_break_progress
        )
        self.timer_thread.signal_state_reset.connect(self.handle_state_reset)

        # 使用editingFinished而不是valueChanged，这样在输入完成后才会检查和更新
        self.min_interval_spinbox.editingFinished.connect(self.update_reminder_interval)
        self.max_interval_spinbox.editingFinished.connect(self.update_reminder_interval)

    def toggle_debug_mode(self, state):
        """切换调试模式"""
        if state == Qt.CheckState.Checked.value:
            self.is_debug_mode = True
            # 设置调试模式的值
            self.focus_spinbox.setValue(1)  # 1分钟
            self.min_interval_spinbox.setValue(5)  # 5秒
            self.max_interval_spinbox.setValue(8)  # 8秒
            self.rest_spinbox.setValue(3)  # 3秒休息时间
        else:
            self.is_debug_mode = False
            # 恢复默认值
            self.focus_spinbox.setValue(90)  # 90分钟
            self.min_interval_spinbox.setValue(180)  # 3分钟
            self.max_interval_spinbox.setValue(300)  # 5分钟
            self.rest_spinbox.setValue(10)  # 10秒休息时间

    def use_short_sound(self):
        """使用短音效"""
        sound_file = self.sound_manager.use_short_sound()
        self.short_sound_radio.setChecked(True)
        self.long_sound_radio.setChecked(False)

    def use_long_sound(self):
        """使用长音效"""
        sound_file = self.sound_manager.use_long_sound()
        self.short_sound_radio.setChecked(False)
        self.long_sound_radio.setChecked(True)

    def test_sound(self):
        """测试提示音"""
        self.sound_manager.play_current_sound(self)

    def update_focus_time(self):
        """更新专注时间设置"""
        focus_time = self.focus_spinbox.value()
        self.timer_thread.set_focus_time(focus_time)
        self.progress_display.focus_progress["progress_bar"].setMaximum(focus_time)
        # 更新初始显示的剩余时间
        self.progress_display.update_focus_progress(0, focus_time)

    def update_reminder_interval(self):
        """更新提醒间隔设置"""
        min_interval = self.min_interval_spinbox.value()
        max_interval = self.max_interval_spinbox.value()

        # 确保最小值不大于最大值，仅在编辑完成后执行检查
        if min_interval > max_interval:
            self.max_interval_spinbox.setValue(min_interval)
            max_interval = min_interval

        self.timer_thread.set_reminder_interval(min_interval, max_interval)

    def update_rest_time(self):
        """更新休息时间设置"""
        rest_time = self.rest_spinbox.value()
        self.timer_thread.set_rest_time(rest_time)
        self.progress_display.break_progress["progress_bar"].setMaximum(rest_time)
        # 更新初始显示的剩余时间
        self.progress_display.update_break_progress(0, rest_time)

    def handle_state_reset(self):
        """处理计时器状态重置信号"""
        # 重置所有进度条显示
        focus_time = self.focus_spinbox.value()
        rest_time = self.rest_spinbox.value()
        self.progress_display.clear_all_progress(focus_time, rest_time, 0)

        # 在状态重置时更新按钮状态
        if not self.timer_thread.running:
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("已停止")

            # 启用所有配置控件
            self.set_config_widgets_enabled(True)

    def start_timer(self):
        """开始计时器"""
        self.update_focus_time()
        self.update_reminder_interval()
        self.update_rest_time()

        # 禁用所有配置控件
        self.set_config_widgets_enabled(False)

        if not self.timer_thread.isRunning():
            self.timer_thread.start()
            self.status_label.setText("专注中...")
        else:
            self.timer_thread.resume()
            self.status_label.setText("已恢复")

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

    def pause_timer(self):
        """暂停计时器"""
        if self.timer_thread.isRunning():
            self.timer_thread.pause()
            self.status_label.setText("已暂停")
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)

    def stop_timer(self):
        """停止计时器"""
        self.status_label.setText("正在停止...")

        # 禁用所有按钮，防止用户在停止过程中操作
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        if self.timer_thread.isRunning():
            # 停止计时器并等待状态重置信号
            self.timer_thread.stop()
            # 注意：重置UI的工作会在handle_state_reset中完成
        else:
            # 如果线程已经不在运行，手动更新UI
            self.status_label.setText("已停止")
            self.start_btn.setEnabled(True)
            # 启用所有配置控件
            self.set_config_widgets_enabled(True)

    def play_reminder_sound(self):
        """播放提醒声音并显示休息提示"""
        success = self.sound_manager.play_current_sound(self)
        if success:
            rest_time = self.rest_spinbox.value()
            self.status_label.setText(f"请休息{rest_time}秒钟!")

    def play_short_break_end_sound(self):
        """播放短休息结束提示音"""
        success = self.sound_manager.play_short_sound(self)
        if success:
            self.status_label.setText("休息结束，继续专注!")

    def update_progress(self, elapsed_minutes):
        """更新专注时间进度"""
        total_minutes = self.focus_spinbox.value()
        self.progress_display.update_focus_progress(elapsed_minutes, total_minutes)

    def update_reminder_progress(self, current_seconds, total_seconds):
        """更新提醒间隔进度"""
        self.progress_display.update_reminder_progress(current_seconds, total_seconds)

    def update_break_progress(self, current_seconds, total_seconds):
        """更新休息时间进度"""
        self.progress_display.update_break_progress(current_seconds, total_seconds)

    def show_break_time(self):
        """显示长休息时间提示"""
        focus_time = self.focus_spinbox.value()
        self.status_label.setText("专注周期完成!")

        # 播放长提示音
        self.sound_manager.play_long_sound(self)

        # 显示选择对话框
        dialog = BreakPromptDialog(self, focus_time)
        dialog.exec()

        # 根据用户选择执行操作
        if dialog.result_action == "rest":
            self.show_break_window()
        else:
            # 重新开始
            self.restart_timer()

    def show_break_window(self):
        """显示休息窗口"""
        # 停止当前计时器
        if self.timer_thread.isRunning():
            self.timer_thread.stop()

        # 创建并显示休息窗口，传递调试模式状态
        self.break_window = BreakWindow(self, debug_mode=self.is_debug_mode)
        self.break_window.break_finished.connect(self.on_break_finished)
        self.break_window.restart_requested.connect(self.restart_timer)
        self.break_window.show()

    def on_break_finished(self):
        """休息结束处理"""
        # 播放提示音
        self.sound_manager.play_long_sound(self)
        self.status_label.setText("休息结束，可以开始新的专注")

        # 启用所有配置控件
        self.set_config_widgets_enabled(True)

        # 启用开始按钮
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

    def restart_timer(self):
        """重新开始计时器"""
        # 停止当前计时器（如果在运行）
        if self.timer_thread.isRunning():
            self.timer_thread.stop()

        # 启用所有设置，然后立即开始
        self.set_config_widgets_enabled(True)
        self.start_timer()

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.timer_thread.isRunning():
            self.timer_thread.stop()
            self.timer_thread.wait()
        event.accept()

    def set_config_widgets_enabled(self, enabled):
        """设置所有配置控件的启用状态"""
        for widget in self.config_widgets:
            widget.setEnabled(enabled)