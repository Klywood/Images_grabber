from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle('YandexImageGrabber')
        self.setGeometry(300, 250, 350, 250)

        self.new_text = QtWidgets.QLabel(self)

        self.main_text = QtWidgets.QLabel(self)
        self.main_text.setText('Hello')
        self.main_text.adjustSize()
        self.main_text.move(100, 100)

        self.btn = QtWidgets.QPushButton(self)
        self.btn.move(150, 200)
        self.btn.setText('Run!')
        self.btn.clicked.connect(self.push_btn)

    def push_btn(self):
        self.new_text.setText('New text')
        self.new_text.move(100, 222)
        self.new_text.adjustSize()


def application():
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    application()
