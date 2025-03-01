import sys
import json
import os
import argparse
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QFrame, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer


from _mmlu.search import search, AgentSystem, bootstrap_confidence_interval
from gui_style import DARK_STYLE_SHEET, set_single_line_dynamic_height, setup_status_animation, setup_ui


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
            args.model = 'gpt-3.5-turbo-0125'

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
        # self.init_ui()
        setup_ui(self)
        # MainWindow.init_ui(self)

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
        self.status_label.set_running()

        self.worker = SearchWorker()
        self.worker.finished.connect(self.search_completed)
        self.worker.error.connect(self.search_error)
        self.worker.start()

    def search_completed(self, best_model):
        self.results_text.clear()
        self.results_text.append(f"Best Model (Fitness: {best_model['fitness']}):\n\n")
        self.results_text.append(best_model['code'])
        self.status_label.set_ready()
        self.search_button.setEnabled(True)

    def search_error(self, error_message):
        self.status_label.set_error()
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