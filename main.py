# 第一行！！最先执行补丁
import preload_patch

import sys
from PyQt6.QtWidgets import QApplication
from windows import HomeWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HomeWindow()
    win.show()
    sys.exit(app.exec())