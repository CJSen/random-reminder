#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
from pathlib import Path
from PyQt6.QtCore import QObject, QUrl, QTimer
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QMessageBox


def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发环境和打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不在打包环境中，使用当前目录所在路径
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


class SoundManager(QObject):
    """处理声音相关功能的管理类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_sound_files()
        self.sound_effect = QSoundEffect()
        self.sound_effect.setVolume(1.0)  # 确保音量设置为最大

        # 监听状态变化
        self.sound_effect.statusChanged.connect(self._status_changed)
        self.sound_effect.playingChanged.connect(self._playing_changed)

        self.current_sound = self.short_sound_file  # 默认使用短音效
        print(f"SoundManager初始化完成，当前音效: {self.current_sound}")

    def _init_sound_files(self):
        """初始化声音文件路径"""
        # 设置默认提示音文件路径
        static_dir = Path(resource_path("static"))
        static_dir.mkdir(exist_ok=True)

        self.short_sound_file = str(static_dir / "dingdong.wav")
        self.long_sound_file = str(static_dir / "dingdong-long.wav")

        # 验证文件是否存在并输出详细信息
        if os.path.exists(self.short_sound_file):
            print(f"短音效文件存在: {self.short_sound_file}, 大小: {os.path.getsize(self.short_sound_file)} 字节")
        else:
            print(f"警告: 短音效文件不存在: {self.short_sound_file}")

        if os.path.exists(self.long_sound_file):
            print(f"长音效文件存在: {self.long_sound_file}, 大小: {os.path.getsize(self.long_sound_file)} 字节")
        else:
            print(f"警告: 长音效文件不存在: {self.long_sound_file}")

        # 列出static目录中的所有文件
        print("static目录中的文件列表:")
        if static_dir.exists():
            for file in static_dir.iterdir():
                print(f"  {file.name} - {os.path.getsize(file)} 字节")
        else:
            print("  静态目录不存在")

    def use_short_sound(self):
        """使用短音效"""
        self.current_sound = self.short_sound_file
        return self.short_sound_file

    def use_long_sound(self):
        """使用长音效"""
        self.current_sound = self.long_sound_file
        return self.long_sound_file

    def _status_changed(self):
        status = self.sound_effect.status()
        print(f"音效状态变化: {status}")

    def _playing_changed(self):
        is_playing = self.sound_effect.isPlaying()
        print(f"音效播放状态变化: {'正在播放' if is_playing else '停止播放'}")

    def play_current_sound(self, parent_widget=None):
        """播放当前选择的提示音"""
        try:
            print(f"尝试播放当前音效: {self.current_sound}, 大小: {os.path.getsize(self.current_sound)} 字节")

            # 尝试使用备用播放方法
            # if self._play_using_system_command(self.current_sound):
            #     return True

            # 如果系统命令失败，使用Qt方法
            # 确保释放之前的资源
            self.sound_effect.stop()

            # 设置音效源
            url = QUrl.fromLocalFile(self.current_sound)
            print(f"音效URL: {url.toString()}")
            self.sound_effect.setSource(url)

            is_loaded = self.sound_effect.isLoaded()
            print(f"音效是否已加载: {is_loaded}")

            # 等待音效加载完成
            if not is_loaded:
                print("音效未加载，正在加载...")
                self.sound_effect.setLoopCount(1)  # 确保只播放一次
                # 添加小的延迟以确保音效加载
                timer = QTimer()
                timer.singleShot(100, self.sound_effect.play)
                return True

            # 播放音效
            self.sound_effect.play()
            print(f"音效播放请求已发送，音量: {self.sound_effect.volume()}")
            return True
        except Exception as e:
            error_msg = f"播放提示音失败: {str(e)}"
            print(f"错误: {error_msg}")
            if parent_widget:
                QMessageBox.warning(parent_widget, "错误", f"播放提示音失败: {str(e)}")
            return False

    def _play_using_system_command(self, sound_file):
        """使用系统命令播放音频文件"""
        try:
            system = platform.system()

            if not os.path.exists(sound_file):
                print(f"文件不存在: {sound_file}")
                return False

            print(f"使用系统命令播放: {sound_file}")

            if system == "Darwin":  # macOS
                subprocess.Popen(["afplay", sound_file])
                return True
            elif system == "Windows":
                # Windows使用PowerShell播放
                subprocess.Popen(["powershell", "-c", f"(New-Object Media.SoundPlayer '{sound_file}').PlaySync();"])
                return True
            elif system == "Linux":
                # Linux系统尝试使用aplay
                subprocess.Popen(["aplay", sound_file])
                return True
            else:
                print(f"不支持的操作系统: {system}")
                return False
        except Exception as e:
            print(f"使用系统命令播放音频失败: {e}")
            return False

    def play_specific_sound(self, sound_file, parent_widget=None):
        """播放指定的提示音文件"""
        try:
            print(f"尝试播放指定音效: {sound_file}")

            # 首先尝试使用系统命令播放
            # if self._play_using_system_command(sound_file):
            #     return True

            # 如果系统命令失败，使用Qt方法
            # 确保释放之前的资源
            self.sound_effect.stop()

            # 设置音效源
            url = QUrl.fromLocalFile(sound_file)
            self.sound_effect.setSource(url)

            # 添加小的延迟以确保音效加载
            timer = QTimer()
            timer.singleShot(100, self.sound_effect.play)
            return True
        except Exception as e:
            if parent_widget:
                QMessageBox.warning(parent_widget, "错误", f"播放提示音失败: {str(e)}")
            return False

    def play_short_sound(self, parent_widget=None):
        """播放短提示音"""
        return self.play_specific_sound(self.short_sound_file, parent_widget)

    def play_long_sound(self, parent_widget=None):
        """播放长提示音"""
        return self.play_specific_sound(self.long_sound_file, parent_widget)