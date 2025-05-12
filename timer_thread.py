#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
from PyQt6.QtCore import QThread, pyqtSignal


class TimerThread(QThread):
    """后台计时器线程，负责时间管理和发出提醒信号"""

    signal_play_sound = pyqtSignal()
    signal_play_short_break_end_sound = pyqtSignal()  # 短休息结束提示音信号
    signal_update_progress = pyqtSignal(int)
    signal_break_time = pyqtSignal()
    signal_update_reminder_progress = pyqtSignal(int, int)  # 当前秒数, 总秒数
    signal_update_break_progress = pyqtSignal(int, int)  # 当前秒数, 总秒数
    signal_state_reset = pyqtSignal()  # 状态重置信号

    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化默认值
        self.running = False
        self.paused = False
        self.is_resting = False  # 是否处于休息状态
        self.rest_seconds = 0  # 休息已经过的秒数
        self.rest_total = 10  # 短休息时间，默认10秒
        self.focus_time = 90  # 默认专注时间90分钟
        self.min_interval = 180  # 最小提醒间隔（秒）
        self.max_interval = 300  # 最大提醒间隔（秒）
        self.elapsed_time = 0  # 已经过的时间（分钟）
        self.next_reminder = 0  # 下一次提醒的时间（分钟）
        self.seconds_counter = 0  # 秒计数器
        self.reminder_seconds_passed = 0  # 距离上次提醒已经过的秒数
        self.reminder_interval_seconds = 0  # 当前提醒间隔（秒）

    def reset_state(self):
        """重置所有状态变量"""
        self.paused = False
        self.is_resting = False
        self.rest_seconds = 0
        self.elapsed_time = 0
        self.next_reminder = 0
        self.seconds_counter = 0
        self.reminder_seconds_passed = 0
        self.reminder_interval_seconds = 0
        # 发出状态重置信号
        self.signal_state_reset.emit()

    def run(self):
        """线程主运行方法"""
        # 完全重置所有状态
        self.reset_state()
        self.running = True

        # 安排第一个提醒间隔
        self.schedule_next_reminder()

        while self.running:
            if not self.paused:
                time.sleep(1)  # 每秒更新一次

                # 退出检查 - 如果在sleep时被停止，立即退出循环
                if not self.running:
                    break

                # 专注计时器始终运行
                self.seconds_counter += 1
                if self.seconds_counter >= 60:
                    self.elapsed_time += 1
                    self.seconds_counter = 0
                    self.signal_update_progress.emit(self.elapsed_time)

                # 检查专注时间是否到达，优先级最高
                if self.elapsed_time >= self.focus_time:
                    self.signal_break_time.emit()
                    self.running = False
                    continue

                # 退出检查 - 再次检查是否被停止
                if not self.running:
                    break

                if self.is_resting:
                    # 休息状态计时
                    self.rest_seconds += 1
                    self.signal_update_break_progress.emit(
                        self.rest_seconds, self.rest_total
                    )
                    # 检查休息时间是否结束
                    if self.rest_seconds >= self.rest_total:
                        self.is_resting = False
                        self.rest_seconds = 0
                        self.signal_play_short_break_end_sound.emit()  # 发送短休息结束信号
                        self.schedule_next_reminder()  # 休息结束后重新安排下一次提醒
                else:
                    # 非休息状态下，提醒间隔计时
                    self.reminder_seconds_passed += 1
                    if self.reminder_interval_seconds > 0:
                        self.signal_update_reminder_progress.emit(
                            self.reminder_seconds_passed, self.reminder_interval_seconds
                        )
                    # 检查是否到达提醒间隔
                    if self.reminder_seconds_passed >= self.reminder_interval_seconds:
                        self.signal_play_sound.emit()
                        self.is_resting = True  # 进入休息状态
                        self.rest_seconds = 0  # 重置休息时间计数器
                        self.reminder_seconds_passed = 0  # 清零提醒计时
            else:
                time.sleep(0.1)  # 暂停时减少CPU使用
                # 退出检查 - 如果在暂停时被停止，立即退出循环
                if not self.running:
                    break

    def schedule_next_reminder(self):
        """安排下一次随机提醒的时间"""
        # 将秒转换为分钟，并加上当前已经过的分钟数
        self.reminder_interval_seconds = random.randint(
            self.min_interval, self.max_interval
        )
        interval_minutes = self.reminder_interval_seconds / 60
        # 确保下一次提醒时间是基于当前时间计算的，避免立即触发
        self.next_reminder = self.elapsed_time + interval_minutes
        self.reminder_seconds_passed = 0  # 重置已经过的秒数

    def get_current_reminder_interval(self):
        """获取当前的提醒间隔（秒）

        如果尚未设置提醒间隔，返回0
        """
        return self.reminder_interval_seconds

    def stop(self):
        """停止计时器"""
        # 先设置停止标志
        self.running = False
        # 等待线程完全停止，设置较长的超时确保线程能停止
        if not self.wait(1000):  # 等待最多2秒
            self.terminate()  # 如果线程仍然运行，强制终止
            self.wait(1000)   # 等待终止完成

        # 确保线程已完全停止后再重置状态
        self.reset_state()

    def pause(self):
        """暂停计时器"""
        self.paused = True

    def resume(self):
        """恢复计时器"""
        self.paused = False

    def set_focus_time(self, minutes):
        """设置专注时间"""
        self.focus_time = minutes

    def set_reminder_interval(self, min_seconds, max_seconds):
        """设置提醒间隔范围（秒）"""
        self.min_interval = min_seconds
        self.max_interval = max_seconds

    def set_rest_time(self, seconds):
        """设置休息时间（秒）"""
        self.rest_total = seconds