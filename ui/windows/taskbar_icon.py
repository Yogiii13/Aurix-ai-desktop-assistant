from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, qApp
from PyQt5.QtGui import QIcon

class TaskbarIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__(QIcon("ui/assets/app_icon.ico"))
        
        menu = QMenu()
        activate_action = menu.addAction("Open")
        activate_action.triggered.connect(self.show_main_window)
        menu.addAction("Exit").triggered.connect(qApp.quit)
        
        self.setContextMenu(menu)
        self.setToolTip("AI Assistant")
        self.show()
        
    def show_main_window(self):
        from main_window import MainWindow
        window = MainWindow()
        window.show()