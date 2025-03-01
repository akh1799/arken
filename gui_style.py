# gui_style.py

DARK_STYLE_SHEET = """
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
"""
