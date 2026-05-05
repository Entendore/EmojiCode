"""Left panel widget for configuring emoji language symbols."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


DEFAULT_EMOJIS = {
    'INIT_STATE': "🟢",
    'HALT_STATE': "🏁",
    'BLANK': "⬜",
    'TAPE_START': "📼",
    'TAPE_END': "⏹️",
    'RULE_START': "📜",
    'RULE_END': "🛑",
    'MOVE_R': "➡️",
    'MOVE_L': "⬅️",
    'MOVE_STAY': "⏸️",
    'RUN': "🚀",
    'PRINT': "🖨️",
    'NEWLINE': "↵"
}

EMOJI_LABELS = {
    'INIT_STATE': 'Initial State',
    'HALT_STATE': 'Halt State',
    'BLANK': 'Blank Symbol',
    'TAPE_START': 'Tape Start',
    'TAPE_END': 'Tape End',
    'RULE_START': 'Rule Start',
    'RULE_END': 'Rule End',
    'MOVE_R': 'Move Right',
    'MOVE_L': 'Move Left',
    'MOVE_STAY': 'Move Stay',
    'RUN': 'Execute',
    'PRINT': 'Print Tape',
    'NEWLINE': 'Newline (↵)'
}


class EmojiConfigPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(270)
        self.emoji_inputs = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title = QLabel("⚙️ Language Config")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        sub = QLabel("Define emoji symbols for\neach language construct:")
        sub.setStyleSheet("color: #888; font-size: 10px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        # Scrollable area for inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(4)
        scroll_layout.setContentsMargins(2, 2, 2, 2)

        for key, label_text in EMOJI_LABELS.items():
            row = self._create_emoji_row(key, label_text)
            scroll_layout.addWidget(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Reset button
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        layout.addWidget(reset_btn)

    def _create_emoji_row(self, key, label_text):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(2, 2, 2, 2)
        row_layout.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setFixedWidth(105)
        lbl.setStyleSheet("font-size: 11px;")

        inp = QLineEdit()
        inp.setFixedWidth(55)
        inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inp.setFont(QFont("Segoe UI Emoji", 16))
        inp.setText(DEFAULT_EMOJIS.get(key, "❓"))
        inp.setPlaceholderText("❓")

        self.emoji_inputs[key] = inp
        row_layout.addWidget(lbl)
        row_layout.addWidget(inp)
        row_layout.addStretch()

        return row

    def _reset_defaults(self):
        for key, default in DEFAULT_EMOJIS.items():
            if key in self.emoji_inputs:
                self.emoji_inputs[key].setText(default)

    def get_emoji_map(self):
        return {k: v.text() for k, v in self.emoji_inputs.items()}

    def validate(self):
        """Validate all emoji fields are filled. Returns (valid, error_msg)."""
        for key, inp in self.emoji_inputs.items():
            if not inp.text().strip():
                return False, f"Please define an emoji for: {EMOJI_LABELS.get(key, key)}"
        return True, ""