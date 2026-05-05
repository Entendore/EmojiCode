"""Application stylesheets."""


MAIN_STYLE = """
    QMainWindow {
        background-color: #2b2b2b;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #d4d4d4;
    }
    QLabel {
        background-color: transparent;
    }
    QLineEdit {
        background-color: #45494a;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 2px;
    }
    QLineEdit:focus {
        border: 1px solid #4fc1ff;
    }
    QTextEdit {
        background-color: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #333;
        border-radius: 4px;
        font-family: 'Segoe UI Emoji';
        font-size: 16px;
    }
    QTextEdit:focus {
        border: 1px solid #4fc1ff;
    }
    QPushButton {
        background-color: #3c3f41;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
        min-height: 30px;
    }
    QPushButton:hover {
        background-color: #505355;
        border-color: #4fc1ff;
    }
    QPushButton:pressed {
        background-color: #2b2d2e;
    }
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #555;
        border-color: #333;
    }
    QComboBox {
        background-color: #45494a;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 6px;
        min-height: 25px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border: none;
    }
    QComboBox QAbstractItemView {
        background-color: #45494a;
        color: white;
        selection-background-color: #264f78;
        border: 1px solid #555;
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        background: #2b2b2b;
        width: 10px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #555;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #666;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QSlider::groove:horizontal {
        border: 1px solid #444;
        height: 6px;
        background: #2b2b2b;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #4fc1ff;
        border: none;
        width: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }
    QSlider::handle:horizontal:hover {
        background: #6fd1ff;
    }
    QStatusBar {
        background-color: #252526;
        color: #888;
        font-size: 11px;
        border-top: 1px solid #333;
    }
    QStatusBar::item {
        border: none;
    }
    QFrame#separator {
        background-color: #333;
        max-width: 1px;
    }
"""

CONSOLE_STYLE = """
    QTextEdit#console {
        background-color: #1e1e1e;
        color: #4ec9b0;
        border: 1px solid #333;
        border-radius: 4px;
        font-family: 'Consolas';
        font-size: 12px;
    }
"""

EDITOR_STYLE = """
    QTextEdit#editor {
        background-color: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #333;
        border-radius: 4px;
        font-family: 'Segoe UI Emoji';
        font-size: 16px;
    }
    QTextEdit#editor:focus {
        border: 1px solid #4fc1ff;
    }
"""