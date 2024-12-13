import sys
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtGui import QKeyEvent

class HomeworkManager(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("homework_manager.ui", self)
        self.conn = sqlite3.connect("homework_manager.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                task TEXT NOT NULL,
                deadline_date TEXT NOT NULL,
                deadline_time TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        self.conn.commit()

        self.addTaskButton.clicked.connect(self.open_add_task_window)
        self.deleteButton.clicked.connect(self.delete_task)
        self.completeButton.clicked.connect(self.complete_task)

        self.apply_button_styles()
        self.load_tasks()

    def apply_button_styles(self):
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """
        self.addTaskButton.setStyleSheet(button_style)
        self.deleteButton.setStyleSheet(button_style)
        self.completeButton.setStyleSheet(button_style)

    def load_tasks(self):
        self.taskList.clear()
        self.completedTaskList.clear()
        self.cursor.execute("SELECT subject, task, deadline_date, deadline_time, status FROM tasks ORDER BY deadline_date, deadline_time")
        for subject, task, deadline_date, deadline_time, status in self.cursor.fetchall():
            task_display = f"{subject}: {task} (до {deadline_date} {deadline_time})"
            if status == "active":
                self.taskList.addItem(task_display)
            elif status == "completed":
                self.completedTaskList.addItem(task_display)

    def keyPressEvent(self, event: QKeyEvent):
        pass

    def open_add_task_window(self):
        self.add_task_window = uic.loadUi("add_task_window.ui")
        self.add_task_window.add_task_button.clicked.connect(self.add_task_from_ui)
        self.add_task_window.show()

    def add_task_from_ui(self):
        subject = self.add_task_window.subject_input.text().strip()
        task = self.add_task_window.task_input.toPlainText().strip()
        deadline_date = self.add_task_window.deadline_date_input.text()
        deadline_time = self.add_task_window.deadline_time_input.text()

        if not subject or not task:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        self.cursor.execute(
            "INSERT INTO tasks (subject, task, deadline_date, deadline_time, status) VALUES (?, ?, ?, ?, ?)",
            (subject, task, deadline_date, deadline_time, "active")
        )
        self.conn.commit()
        self.load_tasks()
        QMessageBox.information(self, "Успех", "Задание добавлено!")
        self.add_task_window.close()

    def delete_task(self):
        selected_items = self.taskList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите задание для удаления.")
            return
        for item in selected_items:
            task_text = item.text().split(": ")[1].split(" (до ")[0]
            self.cursor.execute("DELETE FROM tasks WHERE task = ?", (task_text,))
            self.conn.commit()
            self.taskList.takeItem(self.taskList.row(item))

    def complete_task(self):
        selected_items = self.taskList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите задание для выполнения.")
            return
        for item in selected_items:
            task_text = item.text().split(": ")[1].split(" (до ")[0]
            self.cursor.execute("UPDATE tasks SET status = ? WHERE task = ?", ("completed", task_text))
            self.conn.commit()
            self.load_tasks()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeworkManager()
    window.show()
    sys.exit(app.exec())
