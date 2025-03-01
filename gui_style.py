# gui_style.py

from PyQt6.QtGui import QFontMetrics
from PyQt6.QtCore import QRectF, QTimer

DARK_STYLE_SHEET = """
QMainWindow {
    background-color: #2E2E2E;
    color: white;
    min-width: 1200px;
    min-height: 800px;
}
QWidget {
    background-color: #2E2E2E;
    color: white;
}
QTextEdit {
    background-color: #2E2E2E;
    color: white;
    border: 1px solid #404040;
    font-size: 16px;
}
QTextEdit#task_description {
    background-color: #2E2E2E;
    color: white;
    border: 1px solid #404040;
    border-radius: 10px;
    padding: 5px;
    font-size: 16px;
    min-height: 35px;
    max-height: 100px;
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
}
QPushButton:hover {
    background-color: #505050;
}
QPushButton:disabled {
    background-color: #303030;
    color: #808080;
}
QFrame#status_frame {
    background-color: #2E2E2E;
    border: none;
    margin: 0;
    padding: 0;
}
"""

def set_single_line_dynamic_height(text_edit):
    """
    Overrides the fixed height lines in gui.py to allow
    starting at one line in height and expanding as needed.
    """

    # You can pick a suitable upper bound for max height.
    # For demonstration, let's allow up to ~10 lines.
    text_edit.setMinimumHeight(1)
    text_edit.setMaximumHeight(1000)

    def adjust_dynamic_height():
        doc_height = text_edit.document().size().height()
        margins = text_edit.contentsMargins()
        required_height = doc_height + margins.top() + margins.bottom() + 10
        current_min = text_edit.minimumHeight()
        current_max = text_edit.maximumHeight()
        new_height = max(current_min, min(required_height, current_max))

        if new_height != text_edit.height():
            text_edit.setMinimumHeight(int(new_height))
            text_edit.setMaximumHeight(int(new_height))

    # Whenever text changes, resize
    text_edit.textChanged.connect(adjust_dynamic_height)
    # Immediately size to current content (including placeholder)
    adjust_dynamic_height()

# Add a new function to handle status animation
def setup_status_animation(status_label):
    """
    Sets up animation for the status label when in 'running' state
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
    animation_timer.start(500)  # Update every 500ms
    
    # Store the timer as an attribute of the label to prevent garbage collection
    status_label.animation_timer = animation_timer
    
    # Add methods to set different statuses
    def set_ready():
        status_label.setProperty("status", "ready")
        status_label.setText("Ready")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)
    
    def set_running():
        status_label.setProperty("status", "running")
        animation_index = 0
        update_animation()
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)
    
    def set_error():
        status_label.setProperty("status", "error")
        status_label.setText("Error occurred!")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)
    
    # Attach methods to the label
    status_label.set_ready = set_ready
    status_label.set_running = set_running
    status_label.set_error = set_error
    
    # Initialize with ready state
    set_ready()
