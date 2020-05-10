import json
import sys
import traceback
import threading
from typing import List

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QTabWidget

from libs.Chooser import Chooser
from libs.Login import Login, NewAccount
from libs.Schedule import Schedule
from libs.ElderlyInterface import start, ClientInterface


def switch_tab(tab_to_show, tab_to_hide, tab_name):
    try:
        tabs.removeTab(tabs.indexOf(tab_to_hide))
        tabs.insertTab(0, tab_to_show, tab_name)

        tabs_lst.remove(tab_to_hide)
        tabs_lst.insert(0, tab_to_show)
    except Exception:
        print(traceback.format_exc())


def close_tab(index):
    try:
        tabs.removeTab(index)
        tabs_lst.pop(index)
    except Exception:
        print(traceback.format_exc())


def selected_elderly(user_id, name):
    try:
        schedule = Schedule(user_id)  # Create Schedule Widget

        tabs.insertTab(len(tabs_lst), schedule, name)  # Insert New Tab
        tabs_lst.append(schedule)

        tabs.setTabsClosable(True)
        tabs.tabCloseRequested.connect(close_tab)
    except Exception:
        print(traceback.format_exc())


def login_user():
    user_info = json.load(open("user.json", "r"))
    if user_info["admin"]:
        switch_tab(picker, login_widget, "Administrator Interface")
    else:
        try:
            switch_tab(client_interface, login_widget, "Client Interface")
            client_interface.setStyleSheet("background-color:#a6ddf7;")

            thread = threading.Thread(target=lambda: start(user_info["user_id"], client_interface))
            thread.start()
        except Exception:
            print(traceback.format_exc())


app = QApplication(sys.argv)
app.setStyle("fusion")

# Main Grid for Widgets
grid = QGridLayout()

# Main Window
window = QWidget()
window.setLayout(grid)

# Tabs of Application
tabs = QTabWidget()
grid.addWidget(tabs)

# Login Widget
login_widget = Login()
tabs.addTab(login_widget, "Login")

# New Account Widget
new_account_widget = NewAccount(True)

# Elderly Picker
picker = Chooser()
picker.select_user_signal.connect(selected_elderly)

# Elderly Facing Interface
client_interface = ClientInterface()

# Switching Tabs on Signal
login_widget.login.connect(login_user)
login_widget.new_account.connect(lambda: switch_tab(new_account_widget, login_widget, "New Account"))
new_account_widget.new_account.connect(lambda: switch_tab(login_widget, new_account_widget, "Login"))

# Keeping Track of all tabs
tabs_lst: List[QWidget] = [login_widget]

try:
    open("user.json", "r")
    login_user()
except FileNotFoundError:
    pass

window.show()
app.exec()
