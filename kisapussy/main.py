import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QListWidget, QMessageBox, QDialog, QGroupBox,
                             QRadioButton, QHBoxLayout, QComboBox)
from PyQt5.QtCore import QDateTime, Qt


class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role  # 'admin' or 'client'


class RepairRequest:
    def __init__(self, request_id, equipment, issue_type, description, client, status, date_added):
        self.request_id = request_id
        self.equipment = equipment
        self.issue_type = issue_type
        self.description = description
        self.client = client
        self.status = status
        self.date_added = date_added


class Database:
    def __init__(self):
        self.repair_requests = []
        self.users = []
        self.next_request_id = 1

    def add_repair_request(self, request):
        request.request_id = self.next_request_id
        self.repair_requests.append(request)
        self.next_request_id += 1

    def add_user(self, user):
        self.users.append(user)

    def get_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Учет заявок на ремонт оборудования")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.db = Database()
        self.logged_in_user = None

        self.init_ui()

    def init_ui(self):
        self.label = QLabel("Список заявок на ремонт")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.label)

        self.request_list = QListWidget()
        self.request_list.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.request_list)

        self.refresh_button = QPushButton("Обновить список")
        self.refresh_button.setStyleSheet("font-size: 14px;")
        self.refresh_button.clicked.connect(self.refresh_list)
        self.layout.addWidget(self.refresh_button)

        self.view_completed_button = QPushButton("Посмотреть выполненные заявки")
        self.view_completed_button.setStyleSheet("font-size: 14px;")
        self.view_completed_button.clicked.connect(self.view_completed_requests)
        self.layout.addWidget(self.view_completed_button)

        self.add_request_button = QPushButton("Добавить заявку")
        self.add_request_button.setStyleSheet("font-size: 14px;")
        self.add_request_button.clicked.connect(self.show_add_request_dialog)
        self.layout.addWidget(self.add_request_button)

        self.edit_request_button = QPushButton("Редактировать заявку")
        self.edit_request_button.setStyleSheet("font-size: 14px;")
        self.edit_request_button.clicked.connect(self.show_edit_request_dialog)
        self.layout.addWidget(self.edit_request_button)

        self.accept_request_button = QPushButton("Принять заявку")
        self.accept_request_button.setStyleSheet("font-size: 14px;")
        self.accept_request_button.clicked.connect(self.accept_request)
        self.layout.addWidget(self.accept_request_button)

        self.reject_request_button = QPushButton("Отклонить заявку")
        self.reject_request_button.setStyleSheet("font-size: 14px;")
        self.reject_request_button.clicked.connect(self.reject_request)
        self.layout.addWidget(self.reject_request_button)

        self.complete_request_button = QPushButton("Выполнено")
        self.complete_request_button.setStyleSheet(
            "font-size: 14px; background-color: #4CAF50; color: white; border: none; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; margin: 4px 2px; cursor: pointer;")
        self.complete_request_button.clicked.connect(self.complete_request)
        self.layout.addWidget(self.complete_request_button)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.setStyleSheet("font-size: 14px;")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

        self.show_login_dialog()

    def refresh_list(self):
        self.request_list.clear()
        for request in self.db.repair_requests:
            if self.logged_in_user.role == 'admin' or request.client == self.logged_in_user.username:
                self.request_list.addItem(
                    f"Заявка #{request.request_id} - {request.equipment} ({request.status}) - Добавлена: {request.date_added.toString(Qt.DefaultLocaleShortDate)}")

    def view_completed_requests(self):
        self.request_list.clear()
        for request in self.db.repair_requests:
            if request.status == "выполнено":
                if self.logged_in_user.role == 'admin' or request.client == self.logged_in_user.username:
                    self.request_list.addItem(
                        f"Заявка #{request.request_id} - {request.equipment} ({request.status}) - Добавлена: {request.date_added.toString(Qt.DefaultLocaleShortDate)}")

    def show_add_request_dialog(self):
        if self.logged_in_user:
            dialog = AddRequestDialog(self)
            if dialog.exec_():
                request = dialog.get_repair_request()
                request.client = self.logged_in_user.username
                self.db.add_repair_request(request)
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Войдите в систему, чтобы добавить заявку.", QMessageBox.Ok)

    def show_edit_request_dialog(self):
        if self.logged_in_user:
            current_item = self.request_list.currentItem()
            if current_item is not None:
                index = self.request_list.row(current_item)
                request = self.db.repair_requests[index]
                if self.logged_in_user.role == 'admin' or request.client == self.logged_in_user.username:
                    dialog = EditRequestDialog(self, request)
                    if dialog.exec_():
                        edited_request = dialog.get_repair_request()
                        self.db.repair_requests[index] = edited_request
                        self.refresh_list()
                        QMessageBox.information(self, "Успех", "Заявка успешно отредактирована.", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Ошибка", "У вас нет прав для редактирования этой заявки.", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Ошибка", "Войдите в систему, чтобы редактировать заявки.", QMessageBox.Ok)

    def accept_request(self):
        if self.logged_in_user and self.logged_in_user.role == 'admin':
            current_item = self.request_list.currentItem()
            if current_item is not None:
                index = self.request_list.row(current_item)
                request = self.db.repair_requests[index]
                request.status = "в работе"
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Только администраторы могут принимать заявки.", QMessageBox.Ok)

    def reject_request(self):
        if self.logged_in_user and self.logged_in_user.role == 'admin':
            current_item = self.request_list.currentItem()
            if current_item is not None:
                index = self.request_list.row(current_item)
                request = self.db.repair_requests[index]
                request.status = "отклонено"
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Только администраторы могут отклонять заявки.", QMessageBox.Ok)

    def complete_request(self):
        if self.logged_in_user and self.logged_in_user.role == 'admin':
            current_item = self.request_list.currentItem()
            if current_item is not None:
                index = self.request_list.row(current_item)
                request = self.db.repair_requests[index]
                request.status = "выполнено"
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Только администраторы могут завершать заявки.", QMessageBox.Ok)

    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_():
            self.logged_in_user = dialog.get_user()
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {self.logged_in_user.username}!", QMessageBox.Ok)
            self.refresh_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось войти в систему.", QMessageBox.Ok)
            self.close()

    def logout(self):
        self.logged_in_user = None
        QMessageBox.information(self, "Успех", "Вы вышли из системы.", QMessageBox.Ok)
        self.show_login_dialog()


class LoginDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.username_label)
        self.username_edit = QLineEdit()
        self.username_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.username_edit)

        self.password_label = QLabel("Пароль:")
        self.password_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.password_label)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.password_edit)

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet("font-size: 14px;")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet("font-size: 14px;")
        self.register_button.clicked.connect(self.show_register_dialog)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        user = self.parent().db.get_user(username)
        if user and user.password == password:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неправильное имя пользователя или пароль.", QMessageBox.Ok)

    def show_register_dialog(self):
        dialog = RegisterDialog(self.parent())
        if dialog.exec_():
            user = dialog.get_user()
            self.parent().db.add_user(user)
            QMessageBox.information(self, "Успех", "Регистрация успешна. Теперь вы можете войти в систему.", QMessageBox.Ok)

    def get_user(self):
        return self.user if hasattr(self, 'user') else None


class RegisterDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Регистрация")

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.username_label)
        self.username_edit = QLineEdit()
        self.username_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.username_edit)

        self.password_label = QLabel("Пароль:")
        self.password_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.password_label)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.password_edit)

        self.role_label = QLabel("Роль:")
        self.role_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.role_label)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "client"])
        self.role_combo.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.role_combo)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet("font-size: 14px;")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        role = self.role_combo.currentText()

        if self.parent().db.get_user(username):
            QMessageBox.warning(self, "Ошибка", "Имя пользователя уже занято.", QMessageBox.Ok)
        else:
            self.user = User(username, password, role)
            self.accept()

    def get_user(self):
        return self.user if hasattr(self, 'user') else None


class AddRequestDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить заявку")

        self.layout = QVBoxLayout()

        self.equipment_label = QLabel("Оборудование:")
        self.equipment_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.equipment_label)
        self.equipment_edit = QLineEdit()
        self.equipment_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.equipment_edit)

        self.issue_type_label = QLabel("Тип неисправности:")
        self.issue_type_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.issue_type_label)
        self.issue_type_edit = QLineEdit()
        self.issue_type_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.issue_type_edit)

        self.description_label = QLabel("Описание проблемы:")
        self.description_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.description_label)
        self.description_edit = QTextEdit()
        self.description_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.description_edit)

        self.client_label = QLabel("Клиент:")
        self.client_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.client_label)
        self.client_edit = QLineEdit()
        self.client_edit.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.client_edit)

        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet("font-size: 14px;")
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def get_repair_request(self):
        equipment = self.equipment_edit.text()
        issue_type = self.issue_type_edit.text()
        description = self.description_edit.toPlainText()
        client = self.client_edit.text()
        status = "в ожидании"
        date_added = QDateTime.currentDateTime()
        return RepairRequest(None, equipment, issue_type, description, client, status, date_added)


class EditRequestDialog(AddRequestDialog):
    def __init__(self, parent, request):
        super().__init__(parent)
        self.setWindowTitle("Редактировать заявку")

        self.equipment_edit.setText(request.equipment)
        self.issue_type_edit.setText(request.issue_type)
        self.description_edit.setText(request.description)
        self.client_edit.setText(request.client)
        self.request = request

    def get_repair_request(self):
        edited_request = super().get_repair_request()
        edited_request.request_id = self.request.request_id
        return edited_request


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())