import traceback

from PyQt5.Qt import pyqtSignal as Signal
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QDialog, QLineEdit, \
    QListWidget, QListWidgetItem, QInputDialog
from libs.Firebase import db as database
from libs.Login import NewAccount


class Chooser(QWidget):
    select_user_signal = Signal(str, str)

    def __init__(self):
        super().__init__()

        grid = QGridLayout()
        self.setLayout(grid)

        # Create Account for the Elderly to Use
        new_account_btn = QPushButton("Create Account for Client")
        new_account_btn.clicked.connect(self.new_account)
        grid.addWidget(new_account_btn)

        search_label = QLabel("Enter Name to Search: ")
        grid.addWidget(search_label)

        search_widget = QWidget()  # Searching by Elderly Name
        search_grid = QGridLayout()
        search_widget.setLayout(search_grid)

        self.search_entry = QLineEdit()
        search_grid.addWidget(self.search_entry, 0, 1)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_user)
        search_grid.addWidget(search_btn, 0, 2)
        grid.addWidget(search_widget)

        self.current_items = []
        self.list_users = QListWidget()
        self.list_users.itemDoubleClicked.connect(self.select_user)
        grid.addWidget(self.list_users)

        self.search_user()

    def new_account(self):
        new_account_popup = NewAccountPopUp()
        user_id = new_account_popup.get_results()  # Get User ID to store name in database

        # Getting Elderly's Name (Needed for Searching)
        name = QInputDialog.getText(self, "Name", "Please enter the client's name:", QLineEdit.Normal, "")
        database.child("elderly").child(user_id).update({"name": name[0]})

        # Update QListWidget
        self.search_entry.setText("")
        self.search_user()

    def search_user(self):
        try:
            self.current_items = {}
            self.list_users.clear()
            users = database.child("elderly").get()  # Getting all elderly users from database

            name = self.search_entry.text()
            for user_id in users.val():
                user = users.val()[user_id]
                if name in user["name"]:  # Checking for <name> as a substring
                    self.list_users.addItem(QListWidgetItem(user["name"]))
                    self.current_items[user["name"]] = user_id

        except Exception:
            print(traceback.format_exc())

    def select_user(self, item: QListWidgetItem):
        self.select_user_signal.emit(self.current_items[item.text()], item.text())


class NewAccountPopUp(QDialog):
    def __init__(self):
        super().__init__()

        grid = QGridLayout()
        self.setLayout(grid)

        self.new_account_widget = NewAccount(False)
        self.new_account_widget.new_account.connect(self.accept)
        grid.addWidget(self.new_account_widget, 0, 0)

    def get_results(self):
        if self.exec() == QDialog.Accepted:
            return self.new_account_widget.get_user_id()
        else:
            return None
