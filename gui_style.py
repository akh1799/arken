from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QFrame, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtCore import QRectF, QTimer
from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel

DARK_STYLE_SHEET = """
QMainWindow {
    background-color: #252525;
    color: white;
    min-width: 1200px;
    min-height: 800px;
}

QWidget {
    background-color: #252525;
    color: white;
}

/* Default styling for QTextEdit */
QTextEdit {
    background-color: #2E2E2E;  /* Lighter than main background */
    color: white;
    border: 1px solid #404040;
    font-size: 16px;
    selection-color: white;
    selection-background-color: #0078d7;
}

/* -- Specific styling for the Example Input/Output text box -- */
QTextEdit#example_text {
    /* Thicker 3px border and rounded corners */
    border: 3px solid #404040;
    border-radius: 10px;
}

/* The "Best Model" text box: blends with background, normal border */
QTextEdit#results_text {
    background-color: #252525;  
    color: white;
    border: 1px solid #404040;
    font-size: 16px;
}

QTextEdit::cursor {
    background-color: #0078d7;  /* Blue cursor */
    width: 2px;
}

/* Scrollbar styling */
QScrollBar:vertical {
    border: none;
    background: #333333;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: white;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* Horizontal scrollbar styling */
QScrollBar:horizontal {
    border: none;
    background: #333333;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: white;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* Task description box */
QTextEdit#task_description {
    background-color: #2E2E2E;  /* Lighter than main background */
    color: white;
    border: 2px solid #404040;
    border-radius: 10px;
    padding: 5px;
    font-size: 16px;
    min-height: 40px;
    max-height: 40px; /* Start with same height as button */
}

QTextEdit#task_description[placeholder="true"] {
    color: #808080;
}

QLabel {
    color: white;
    font-size: 16px;
}

QLabel#status_title {
    color: white;
    font-size: 16px;
    padding: 5px;
    margin: 0;
}

QLabel#status_label {
    font-size: 16px;
    padding: 5px;
    margin-left: 5px;
}

QLabel#status_label[status="ready"] {
    color: #4CAF50;  /* Green color for ready status */
}

QLabel#status_label[status="running"] {
    color: white;    /* White color for running status */
}

QLabel#status_label[status="error"] {
    color: #F44336;  /* Red color for error status */
}

QPushButton {
    background-color: #404040;
    color: white;
    border: 1px solid #505050;
    border-radius: 10px;
    padding: 8px 20px;
    font-size: 16px;
    min-height: 35px;
    max-height: 35px;
}

QPushButton:hover {
    background-color: #505050;
}

QPushButton:disabled {
    background-color: #303030;
    color: #808080;
}

QFrame#status_frame {
    background-color: #252525;
    border: none;
    margin: 0;
    padding: 0;
}

QTextEdit#example_text::placeholder {
    color: #808080;
    font-size: 16px;
}
"""


def set_single_line_dynamic_height(text_edit):

    text_edit.setMinimumHeight(70)
    text_edit.setMaximumHeight(100)

    def adjust_dynamic_height():
        doc_height = text_edit.document().size().height()
        margins = text_edit.contentsMargins()
        
        required_height = doc_height + margins.top() + margins.bottom()
        
        if required_height > text_edit.height() + 5:
            new_height = min(required_height, 200)
            text_edit.setMinimumHeight(int(new_height))
            text_edit.setMaximumHeight(int(new_height))
        elif required_height < text_edit.height() - 10 and text_edit.height() > 70:
            new_height = max(70, required_height)
            text_edit.setMinimumHeight(int(new_height))
            text_edit.setMaximumHeight(int(new_height))

    text_edit.textChanged.connect(adjust_dynamic_height)


def setup_status_animation(status_label):
    """
    Animates the status label when in 'running' state by rotating the text.
    """
    animation_timer = QTimer()
    animation_states = ["Searching.", "Searching..", "Searching..."]
    animation_index = 0

    def update_animation():
        nonlocal animation_index
        if status_label.property("status") == "running":
            status_label.setText(animation_states[animation_index])
            animation_index = (animation_index + 1) % len(animation_states)

    animation_timer.timeout.connect(update_animation)
    animation_timer.start(500)

    status_label.animation_timer = animation_timer

    def set_ready():
        status_label.setProperty("status", "ready")
        status_label.setText("Ready")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)

    def set_running():
        status_label.setProperty("status", "running")
        update_animation()
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)

    def set_error():
        status_label.setProperty("status", "error")
        status_label.setText("Error")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)

    status_label.set_ready = set_ready
    status_label.set_running = set_running
    status_label.set_error = set_error
    set_ready()


def setup_ui(window):
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.setHandleWidth(1) 
    splitter.setStyleSheet("""
        QSplitter::handle {
            background-color: #404040;
        }
        QSplitter::handle:horizontal {
            width: 1px;
        }
        QSplitter::handle:hover {
            background-color: #0078d7;
        }
    """)
    
    # Left side - Example Input/Output
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    window.example_text = QTextEdit()
    window.example_text.setMinimumHeight(70)
    window.example_text.setMaximumHeight(200) 
    window.example_text.setPlaceholderText("Example Input/Output")
    window.example_text.setObjectName("example_text")
    left_layout.addWidget(window.example_text)
    splitter.addWidget(left_container)
    
    # Right side - Best Model
    right_container = QWidget()
    right_layout = QVBoxLayout(right_container)
    right_layout.addWidget(QLabel("Best Model:"))
    window.results_text = QTextEdit()
    window.results_text.setObjectName("results_text")
    window.results_text.setMinimumHeight(500)
    window.results_text.setMinimumHeight(600) 
    window.results_text.setReadOnly(True)
    right_layout.addWidget(window.results_text)
    splitter.addWidget(right_container)
    
    splitter.setSizes([500, 500])
    
    main_layout.addWidget(splitter)

    main_layout.addStretch(1)
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine) 
    line.setFrameShadow(QFrame.Shadow.Sunken) 
    line.setLineWidth(2) 
    main_layout.addWidget(line, alignment=Qt.AlignmentFlag.AlignBottom)

    # Status bar at the bottom left
    status_frame = QFrame()
    status_frame.setObjectName("status_frame")
    status_layout = QHBoxLayout(status_frame)
    status_layout.setContentsMargins(10, 5, 10, 10)  # Left, top, right, bottom margins

    status_title = QLabel("Status:")
    status_title.setObjectName("status_title")
    status_layout.addWidget(status_title)

    window.status_label = QLabel("Ready")
    window.status_label.setObjectName("status_label")
    status_layout.addWidget(window.status_label)
    status_layout.addStretch()

    # Position the status frame at the bottom left
    main_layout.addStretch(1)  # Push everything up
    main_layout.addWidget(status_frame, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

    bottom_frame = QFrame()
    bottom_layout = QHBoxLayout(bottom_frame)
    
    window.task_text = QTextEdit()
    window.task_text.setObjectName("task_description")
    window.task_text.setMinimumHeight(35)
    window.task_text.setMaximumHeight(35)
    window.task_text.setPlaceholderText("Task Description")
    window.task_text.textChanged.connect(window.adjust_task_height)
    bottom_layout.addWidget(window.task_text)

    window.search_button = QPushButton("Search")
    window.search_button.clicked.connect(window.start_search)
    bottom_layout.addWidget(window.search_button)
    
    main_layout.addWidget(bottom_frame)

    window.worker = None

    set_single_line_dynamic_height(window.task_text)
    # set_single_line_dynamic_height(window.example_text) 
    # set_single_line_dynamic_height(window.results_text)  # Add this line for dynamic height adjustment

    setup_status_animation(window.status_label)