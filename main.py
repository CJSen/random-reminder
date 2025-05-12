#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from sound_manager import resource_path


def ensure_static_dir():
    """确保static目录存在"""
    static_dir = Path(resource_path("static"))
    static_dir.mkdir(exist_ok=True)

    # 检查默认音效文件是否存在，如不存在则创建默认文件
    # 在实际应用中，这里应该复制预置的音效文件


def main():
    """应用程序主入口"""
    # 确保必要的目录和文件存在
    ensure_static_dir()

    # 创建应用程序
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 进入事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
