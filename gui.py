import sys
import json
import os
import argparse
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

# Added import for the style
from gui_style import DARK_STYLE_SHEET

from _mmlu.search import search, AgentSystem, bootstrap_confidence_interval

class SearchWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def run(self):
        try:
            parser = argparse.ArgumentParser()
            args = parser.parse_args([])
            args.data_filename = "dataset/mmlu.csv"
            args.valid_size = 128
            args.test_size = 800
            args.shuffle_seed = 0
            args.n_repreat = 1
            args.multiprocessing = True
            args.max_workers = 48
            args.debug = True
            args.save_dir = 'results/'
            args.expr_name = "mmlu_gpt3.5_results"
            args.n_generation = 30
            args.debug_max = 3
            args.model = 'claude-3-5-haiku-latest'

            search(args)

            file_path = os.path.join(args.save_dir, f"{args.expr_name}_run_archive.json")
            with open(file_path, 'r') as json_file:
                archive = json.load(json_file)

            best_fitness = -1
            best_model = None
            for solution in archive:
                if 'fitness' in solution:
                    fitness_str = solution['fitness']
                    mean = float(fitness_str.split('±')[0].strip())
                    if mean > best_fitness:
                        best_fitness = mean
                        best_model = solution

            if best_model:
                self.finished.emit(best_model)
            else:
                self.error.emit("No valid model found")

        except Exception as e:
            self.error.emit(str(e))

class SearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MMLU Search GUI")
        self.showMaximized()
        self.init_ui()

    def init_ui(self):
        # The existing inline style remains exactly as it was.
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E2E2E;
                color: white;
            }
            QTextEdit {
                background-color: #2E2E2E;
                color: white;
                border: 1px solid #404040;
                font-size: 14px;
            }
            QTextEdit#task_description {
                background-color: #2E2E2E;
                color: white;
                border: 1px solid #404040;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                min-height: 35px;
                max-height: 100px;
            }
            QTextEdit#task_description[placeholder="true"] {
                color: #808080;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #505050;
                border-radius: 10px;
                padding: 8px 20px;
                font-size: 14px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #303030;
                color: #808080;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(QLabel("Example Input/Output:"))
        self.example_text = QTextEdit()
        self.example_text.setMinimumHeight(200)
        main_layout.addWidget(self.example_text)

        main_layout.addWidget(QLabel("Best Model:"))
        self.results_text = QTextEdit()
        self.results_text.setMinimumHeight(200)
        main_layout.addWidget(self.results_text)

        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addWidget(status_frame)

        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        
        self.task_text = QTextEdit()
        self.task_text.setObjectName("task_description")
        self.task_text.setMinimumHeight(35)
        self.task_text.setMaximumHeight(35)
        self.task_text.setPlaceholderText("Task Description")
        self.task_text.textChanged.connect(self.adjust_task_height)
        bottom_layout.addWidget(self.task_text)

        self.search_button = QPushButton("Start Search")
        self.search_button.clicked.connect(self.start_search)
        bottom_layout.addWidget(self.search_button)
        
        main_layout.addWidget(bottom_frame)

        self.worker = None

    def adjust_task_height(self):
        doc_height = self.task_text.document().size().height()
        margins = self.task_text.contentsMargins()
        required_height = doc_height + margins.top() + margins.bottom() + 10
        new_height = max(35, min(required_height, 100))
        if new_height != self.task_text.height():
            self.task_text.setMinimumHeight(int(new_height))
            self.task_text.setMaximumHeight(int(new_height))

    def start_search(self):
        if not self.task_text.toPlainText().strip():
            QMessageBox.critical(self, "Error", "Please enter a task description")
            return

        self.search_button.setEnabled(False)
        self.status_label.setText("Searching...")

        self.worker = SearchWorker()
        self.worker.finished.connect(self.search_completed)
        self.worker.error.connect(self.search_error)
        self.worker.start()

    def search_completed(self, best_model):
        self.results_text.clear()
        self.results_text.append(f"Best Model (Fitness: {best_model['fitness']}):\n\n")
        self.results_text.append(best_model['code'])
        self.status_label.setText("Search Complete!")
        self.search_button.setEnabled(True)

    def search_error(self, error_message):
        self.status_label.setText("Error occurred!")
        QMessageBox.critical(self, "Error", error_message)
        self.search_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    gui = SearchGUI()
    
    # Added line to apply stylesheet from gui_style.py
    gui.setStyleSheet(DARK_STYLE_SHEET)
    
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
