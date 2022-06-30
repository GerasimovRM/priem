import json
import os
import sys
import pickle
from configparser import ConfigParser


import PyQt5
from PyQt5.QtCore import QUrl, QTimer, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem as _QTableWidgetItem, QSizePolicy
from PyQt5 import QtCore, QtWebSockets, QtGui
from ui_main_window import Ui_MainWindow
import webbrowser
import requests


class QTableWidgetItem(_QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextAlignment(Qt.AlignCenter)


class QtTestApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(QtTestApp, self).__init__()
        self.setupUi(self)

        config = ConfigParser()
        config.read("config.ini")
        self.server_address = config.get("QT", "SERVER_ADDRESS")
        self.server_port = config.get("QT", "SERVER_PORT")
        self.icons = {"link": QIcon("images/link.png"),
                      "red_button": QIcon("images/red_circle.png"),
                      "green_button": QIcon("images/green_circle.png"),
                      "cancel_button": QIcon("images/cancel.png")}

        self.client = None
        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        self.client.error.connect(self.error)
        self.label_icon_connection.setPixmap(self.icons["red_button"].pixmap(20))
        self.label_status_connection.setText("Соединение разорвано")
        self.websocket_connection()
        self.tableWidget.itemDoubleClicked.connect(self.open_link)
        self.students_data = None

    def config_size_table(self):
        self.tableWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setFixedSize(
            self.tableWidget.horizontalHeader().length() + self.tableWidget.verticalHeader().width(),
            self.tableWidget.verticalHeader().length() + self.tableWidget.horizontalHeader().height())

    def put_student_request(self, fio: str, link: str, is_moderated: bool):
        requests.put(f"http://{self.server_address}:{self.server_port}/student", params={"fio": fio,
                                                                                         "student_url": link,
                                                                                         "computer_name": os.environ[
                                                                                             "COMPUTERNAME"],
                                                                                         "is_moderated": is_moderated})

    def open_link(self, item: QTableWidgetItem):
        item_column = item.column()
        item_row = item.row()
        if item_column == 1 and not self.students_data[item_row]["is_moderated"]:
            self.put_student_request(self.students_data[item_row]["fio"],
                                     self.students_data[item_row]["student_url"],
                                     True)
            self.students_data[item_row]["is_moderated"] = True

            self.tableWidget.setItem(item_row, 6, QTableWidgetItem(os.environ["COMPUTERNAME"]))
            table_widget_item_cancel = QTableWidgetItem()
            table_widget_item_cancel.setIcon(self.icons["cancel_button"])
            table_widget_item_cancel.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter | Qt.AlignHCenter)
            self.tableWidget.setItem(item_row, 7, table_widget_item_cancel)
            webbrowser.open(self.students_data[item_row]["student_url"])
            self.set_color_to_row(item_row, PyQt5.QtCore.Qt.gray)
        elif item_column == 7 and self.students_data[item_row]["is_moderated"]:
            self.put_student_request(self.students_data[item_row]["fio"],
                                     self.students_data[item_row]["student_url"],
                                     False)
            self.students_data[item_row]["is_moderated"] = False
            self.tableWidget.setItem(item_row, 6, QTableWidgetItem("Свободен"))
            table_widget_item_cancel = QTableWidgetItem()
            table_widget_item_cancel.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter | Qt.AlignHCenter)
            self.tableWidget.setItem(item_row, 7, table_widget_item_cancel)
            self.set_color_to_row(item_row, None)

    def websocket_connection(self):
        self.client.open(QUrl(f"ws://{self.server_address}:{self.server_port}"))
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
            table_widget_item_link.setIcon(self.icons["link"])
            table_widget_item_link.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter | Qt.AlignHCenter)
            self.tableWidget.setItem(row_position, 1, table_widget_item_link)
            self.tableWidget.setItem(row_position, 2, QTableWidgetItem("\n".join(student["directions"])))
            self.tableWidget.setItem(row_position, 3, QTableWidgetItem(student["status"]))
            self.tableWidget.setItem(row_position, 4, QTableWidgetItem(student["time_send"]))
            self.tableWidget.setItem(row_position, 5, QTableWidgetItem(student["time_created"]))
            computer_name = student["computer_name"] if student["computer_name"] else "Свободен"
            self.tableWidget.setItem(row_position, 6, QTableWidgetItem(computer_name))
            table_widget_item_cancel = QTableWidgetItem()
            if student["is_moderated"] and computer_name == os.environ["COMPUTERNAME"]:
                table_widget_item_cancel.setIcon(self.icons["cancel_button"])
            self.tableWidget.setItem(row_position, 7, table_widget_item_cancel)
            self.tableWidget.setItem(row_position, 8, QTableWidgetItem(student["last_moderator"]))
            if student["is_moderated"]:
                self.set_color_to_row(row_position, PyQt5.QtCore.Qt.gray)
        self.config_size_table()
        self.label_icon_connection.setPixmap(self.icons["green_button"].pixmap(20))
        self.label_status_connection.setText("Подключено")
        self.client.sendTextMessage("ok")

    def error(self, error_code):
        self.label_icon_connection.setPixmap(self.icons["red_button"].pixmap(20))
        self.label_status_connection.setText("Соединение разорвано")
        self.tableWidget.setRowCount(0)
        print("error code: {}".format(error_code))
        print(self.client.errorString())
        self.websocket_connection()

    def set_color_to_row(self, row_index, color):
        for j in range(self.tableWidget.columnCount()):
            table_item = self.tableWidget.item(row_index, j)
            if color:
                table_item.setBackground(color)
            else:
                table_item.setData(Qt.BackgroundRole, None)


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