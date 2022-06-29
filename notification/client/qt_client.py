import json
import os
import sys
import pickle

import PyQt5
from PyQt5.QtCore import QUrl, QTimer, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QSizePolicy
from PyQt5 import QtCore, QtWebSockets, QtGui
from ui_main_window import Ui_MainWindow
import webbrowser
import requests


class QtTestApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(QtTestApp, self).__init__()
        self.setupUi(self)

        self.client = None
        self.websocket_connection()
        self.tableWidget.itemDoubleClicked.connect(self.open_link)
        self.students_data = None
        self.link_icon = QIcon("images/link.png")

    def config_size_table(self):
        self.tableWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setFixedSize(
            self.tableWidget.horizontalHeader().length() + self.tableWidget.verticalHeader().width(),
            self.tableWidget.verticalHeader().length() + self.tableWidget.horizontalHeader().height())

    @staticmethod
    def put_student_request(fio: str, link: str):
        requests.put("http://127.0.0.1:5000/student", params={"fio": fio,
                                                              "student_url": link,
                                                              "computer_name": os.environ["COMPUTERNAME"]})

    def open_link(self, item: QTableWidgetItem):
        item_column = item.column()
        item_row = item.row()
        if item_column == 1 and not self.students_data[item_row]["is_moderated"]:
            self.put_student_request(self.students_data[item_row]["fio"],
                                     self.students_data[item_row]["student_url"])
            self.students_data[item_row]["is_moderated"] = True
            self.set_color_to_row(item_row, PyQt5.QtCore.Qt.gray)
            webbrowser.open(self.students_data[item_row]["student_url"])

    def websocket_connection(self):
        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        self.client.error.connect(self.error)

        self.client.open(QUrl("ws://127.0.0.1:5000"))
        self.client.textMessageReceived.connect(self.receive_message)

    def send_message(self):
        self.client.sendTextMessage("ok")

    def receive_message(self, message):
        message = json.loads(message)
        print(f"client: receive message: {message}")
        # self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.students_data = message["students"]
        for student in self.students_data:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(student["fio"]))
            table_widget_item_link = QTableWidgetItem()
            table_widget_item_link.setIcon(self.link_icon)
            self.tableWidget.setItem(row_position, 1, table_widget_item_link)
            self.tableWidget.setItem(row_position, 2, QTableWidgetItem("\n".join(student["directions"])))
            self.tableWidget.setItem(row_position, 3, QTableWidgetItem(student["status"]))
            self.tableWidget.setItem(row_position, 4, QTableWidgetItem(student["time_send"]))
            self.tableWidget.setItem(row_position, 5, QTableWidgetItem(student["time_created"]))
            computer_name = student["computer_name"] if student["computer_name"] else "Свободен"
            self.tableWidget.setItem(row_position, 6, QTableWidgetItem(computer_name))
            self.tableWidget.setItem(row_position, 7, QTableWidgetItem(student["last_moderator"]))
            if student["is_moderated"]:
                self.set_color_to_row(row_position, PyQt5.QtCore.Qt.gray)
        self.config_size_table()
        self.client.sendTextMessage("ok")

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def set_color_to_row(self, row_index, color):
        for j in range(self.tableWidget.columnCount()):
            table_item = self.tableWidget.item(row_index, j)
            table_item.setBackground(color)


sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = QtTestApp()
    client.show()
    sys.exit(app.exec())