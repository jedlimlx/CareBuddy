import traceback
import requests
import json
from libs.Firebase import auth as authentication, db as database
from PyQt5.Qt import pyqtSignal as Signal, QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox


class Login(QWidget):
    login = Signal()
    new_account = Signal()

    def __init__(self):
        super().__init__()

        grid = QGridLayout()
        self.setLayout(grid)

        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segeo UI", 20))
        grid.addWidget(email_label)

        self.email_entry = QLineEdit()
        self.email_entry.setFont(QFont("Segeo UI", 20))
        grid.addWidget(self.email_entry)

        password_label = QLabel("Password:")
        password_label.setFont(QFont("Segeo UI", 20))
        grid.addWidget(password_label)

        self.password_entry = QLineEdit()
        self.password_entry.setFont(QFont("Segeo UI", 20))
        self.password_entry.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.password_entry)

        login_btn = QPushButton(text="Login")
        login_btn.setFont(QFont("Segeo UI", 20))
        login_btn.clicked.connect(self.login_func)
        grid.addWidget(login_btn)

        new_account_btn = QPushButton(text="Create Account")
        new_account_btn.setFont(QFont("Segeo UI", 20))
        new_account_btn.clicked.connect(self.new_account.emit)
        grid.addWidget(new_account_btn)

    def login_func(self):
        try:
            user = authentication.sign_in_with_email_and_password(self.email_entry.text(),
                                                                  self.password_entry.text())
            user_info = database.child("users").child(user["localId"]).get().val()
            user_info["user_id"] = user["localId"]
            json.dump(user_info, open("user.json", "w"))
            self.login.emit()
        except requests.HTTPError:
            QMessageBox.warning(self, "Invalid Login", "Invalid Email or Password",
                                QMessageBox.Ok, QMessageBox.Ok)
            print(traceback.format_exc())


class NewAccount(QWidget):
    new_account = Signal()

    def __init__(self, admin: bool):
        super().__init__()

        grid = QGridLayout()
        self.setLayout(grid)

        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segeo UI", 20))
        grid.addWidget(email_label)

        self.email_entry = QLineEdit()
        self.email_entry.setFont(QFont("Segeo UI", 20))
        grid.addWidget(self.email_entry)

        password_label = QLabel("Password:")
        password_label.setFont(QFont("Segeo UI", 20))
        grid.addWidget(password_label)

        self.password_entry = QLineEdit()
        self.password_entry.setFont(QFont("Segeo UI", 20))
        self.password_entry.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.password_entry)

        repeat_password_label = QLabel("Repeat Password:")
        repeat_password_label.setFont(QFont("Segeo UI", 20))
        grid.addWidget(repeat_password_label)

        self.repeat_password_entry = QLineEdit()
        self.repeat_password_entry.setFont(QFont("Segeo UI", 20))
        self.repeat_password_entry.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.repeat_password_entry)

        create_account_btn = QPushButton(text="Create Account")
        create_account_btn.setFont(QFont("Segeo UI", 20))
        create_account_btn.clicked.connect(lambda: self.create_account(admin))
        grid.addWidget(create_account_btn)

    def create_account(self, admin):
        if self.password_entry.text() == self.repeat_password_entry.text():
            try:
                user = authentication.create_user_with_email_and_password(email=self.email_entry.text(),
                                                                          password=self.password_entry.text())

                # Store whether the user is an admin in the database
                database.child("users").child(user["localId"]).update({"admin": admin})

                # Storing User ID
                self.user_id = user["localId"]
                self.new_account.emit()
            except requests.HTTPError:
                print(traceback.format_exc())
                QMessageBox.warning(self, "Invalid Email!",
                                    "Invalid Email! Please enter a valid email!",
                                    QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Passwords are not the same!",
                                "The 2 entered passwords are not the same.",
                                QMessageBox.Ok, QMessageBox.Ok)

    def get_user_id(self):
        return self.user_id
