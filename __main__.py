# -*- coding: utf-8 -*-
""" @author: Gabriel Maccari """

from PyQt6.QtWidgets import QApplication
from sys import argv
from icecream import ic

from view_controller import ViewController
from model import Model

if __name__ == '__main__':
    try:
        app = QApplication(argv)
        app.setStyle("fusion")

        controller = Model()

        window = ViewController(controller)
        window.show()
        app.exec()
    except Exception as exception:
        ic(exception)
