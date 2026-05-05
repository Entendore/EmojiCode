"""Main application window for the Emoji Turing Machine."""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QFrame, QStatusBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from emoji_turing_machine import EmojiTuringMachine
from tape_widget import TapeWidget
from emoji_config_panel import EmojiConfigPanel
from control_panel import ControlPanel
from examples import get_example_code
from styles import MAIN_STYLE, CONSOLE_STYLE, EDITOR_STYLE


class EmojicodeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⬛ Pure Emoji Turing Machine ⬛")
        self.setGeometry(100, 100, 1250, 900)

        self.tm = None
        self.run_timer = QTimer()
        self.run_timer.setInterval(51)
        self.run_timer.timeout.connect(self._auto_step)
        self.is_auto_running = False

        self._setup_styles()
        self._setup_ui()
        self._setup_shortcuts()
        self._setup_status_bar()

        self.log("Welcome to the Emoji Turing Machine!")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("📖 Use '↵' for multi-line formatting in outputs")
        self.log("⌨️  Shortcuts: F5=Run, F10=Step, F6=Auto, Esc=Stop")
        self.log("🔍 Ctrl+Scroll to zoom the tape view")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _setup_styles(self):
        self.setStyleSheet(MAIN_STYLE)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Left panel - config
        self.config_panel = EmojiConfigPanel()
        main_layout.addWidget(self.config_panel)

        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.VLine)
        main_layout.addWidget(separator)

        # Right panel
        right_frame = QWidget()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Tape visualizer
        self.tape_widget = TapeWidget()
        right_layout.addWidget(self.tape_widget, stretch=2)

        # Code editor
        editor_label = QLabel("💾 Pure Emoji Code")
        editor_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        right_layout.addWidget(editor_label)

        self.editor = QTextEdit()
        self.editor.setObjectName("editor")
        self.editor.setStyleSheet(EDITOR_STYLE)
        self.editor.setFont(QFont("Segoe UI Emoji", 16))
        self.editor.setPlaceholderText("Write your emoji Turing machine code here...\nOr load an example from the dropdown above.")
        right_layout.addWidget(self.editor, stretch=3)

        # Control panel
        self.control_panel = ControlPanel()
        self.control_panel.step_clicked.connect(self.step_machine)
        self.control_panel.run_clicked.connect(self.run_machine)
        self.control_panel.auto_toggled.connect(self.toggle_auto_run)
        self.control_panel.stop_clicked.connect(self.stop_auto_run)
        self.control_panel.reset_clicked.connect(self.reset_machine)
        self.control_panel.example_load_requested.connect(self.load_example)
        self.control_panel.speed_changed.connect(self._set_timer_interval)
        self.control_panel.btn_zoom_in.clicked.connect(self.tape_widget.zoom_in)
        self.control_panel.btn_zoom_out.clicked.connect(self.tape_widget.zoom_out)
        self.control_panel.btn_zoom_reset.clicked.connect(self.tape_widget.reset_zoom)
        right_layout.addWidget(self.control_panel)

        # Console output with clear button
        console_header = QHBoxLayout()
        console_label = QLabel("🖥️ Output")
        console_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        console_header.addWidget(console_label)
        console_header.addStretch()

        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.setFixedWidth(70)
        btn_clear.setStyleSheet("padding: 4px 8px; font-size: 11px; min-height: 20px;")
        btn_clear.clicked.connect(self.console.clear)
        console_header.addWidget(btn_clear)

        btn_copy = QPushButton("📋 Copy")
        btn_copy.setFixedWidth(70)
        btn_copy.setStyleSheet("padding: 4px 8px; font-size: 11px; min-height: 20px;")
        btn_copy.clicked.connect(self._copy_output)
        console_header.addWidget(btn_copy)

        right_layout.addLayout(console_header)

        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setStyleSheet(CONSOLE_STYLE)
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 12))
        right_layout.addWidget(self.console, stretch=2)

        main_layout.addWidget(right_frame, stretch=1)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # F5 - Run all
        run_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        run_shortcut.activated.connect(self.run_machine)

        # F10 - Step
        step_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F10), self)
        step_shortcut.activated.connect(self.step_machine)

        # F6 - Toggle auto run
        auto_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F6), self)
        auto_shortcut.activated.connect(self.toggle_auto_run)

        # Escape - Stop
        stop_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        stop_shortcut.activated.connect(self.stop_auto_run)

        # Ctrl+R - Reset
        reset_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reset_shortcut.activated.connect(self.reset_machine)

        # Ctrl+S - Save file
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self._save_file)

        # Ctrl+O - Open file
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self._open_file)

        # Ctrl+= Zoom in
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in_shortcut.activated.connect(self.tape_widget.zoom_in)

        # Ctrl+- Zoom out
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self.tape_widget.zoom_out)

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_state = QLabel("State: —")
        self.status_rules = QLabel("Rules: —")
        self.status_steps = QLabel("Steps: —")
        self.status_tape = QLabel("Tape: —")

        for label in [self.status_state, self.status_rules, self.status_steps, self.status_tape]:
            label.setStyleSheet("padding: 0 10px;")
            self.status_bar.addPermanentWidget(label)

        self._update_status_bar()

    def _update_status_bar(self):
        if self.tm:
            stats = self.tm.get_stats()
            state_text = self.tm.state if self.tm.state else "—"
            self.status_state.setText(f"State: {state_text}")
            self.status_rules.setText(f"Rules: {stats['rule_count']}")
            self.status_steps.setText(f"Steps: {stats['step_count']}")
            self.status_tape.setText(f"Tape: {stats['tape_length']} cells")
        else:
            self.status_state.setText("State: —")
            self.status_rules.setText("Rules: —")
            self.status_steps.setText("Steps: —")
            self.status_tape.setText("Tape: —")

    def _set_timer_interval(self, interval):
        self.run_timer.setInterval(interval)

    def log(self, msg):
        self.console.append(msg)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _copy_output(self):
        text = self.console.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.log("📋 Output copied to clipboard!")

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Code", "", "Emoji Code Files (*.emoji);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.log(f"💾 Saved to: {path}")

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Code", "", "Emoji Code Files (*.emoji);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.reset_machine()
            self.log(f"📂 Opened: {path}")

    def _sync_visualizer(self):
        if self.tm:
            self.tape_widget.update_tape(
                self.tm.tape, self.tm.head,
                self.tm.state if self.tm.state else "⏸️",
                self.tm.step_count,
                self.tm.last_rule
            )
        else:
            self.tape_widget.update_tape([], 0, "⏸️", 0)
        self._update_status_bar()

    def _init_machine(self):
        em_map = self.config_panel.get_emoji_map()
        code = self.editor.toPlainText().strip()

        if not code:
            self.log("❌ Write some emoji code first!")
            return False

        valid, error = self.config_panel.validate()
        if not valid:
            self.log(f"❌ {error}")
            return False

        try:
            self.tm = EmojiTuringMachine(em_map)
            self.tm.parse(code)
            self._sync_visualizer()
            stats = self.tm.get_stats()
            self.log(f"✅ Parsed successfully.")
            self.log(f"   📊 {stats['rule_count']} rules, {stats['tape_length']} tape cells, {stats['unique_states']} states")
            return True
        except ValueError as e:
            self.log(f"❌ PARSE ERROR: {e}")
        except Exception as e:
            self.log(f"❌ UNEXPECTED ERROR: {e}")
        return False

    def step_machine(self):
        if not self.tm or not self.tm.tape:
            if not self._init_machine():
                return
        if self.tm.halted:
            self.log("🏁 Machine is already halted.")
            return

        success = self.tm.step()
        self._sync_visualizer()

        if not success:
            em = self.config_panel.get_emoji_map()
            if self.tm.state == em['HALT_STATE']:
                self.log("🏁 Machine halted successfully.")
            else:
                self.log(f"💥 Crashed at step {self.tm.step_count} - no matching rule found.")

    def _auto_step(self):
        if not self.tm or self.tm.halted:
            self.stop_auto_run()
            return
        self.tm.step()
        self._sync_visualizer()
        if self.tm.halted:
            self.stop_auto_run()
            self.log("🏁 Auto-run finished.")

    def toggle_auto_run(self):
        if self.is_auto_running:
            self.stop_auto_run()
        else:
            if not self.tm or not self.tm.tape:
                if not self._init_machine():
                    return
            if self.tm.halted:
                self.log("🏁 Machine is already halted.")
                return
            self.is_auto_running = True
            self.run_timer.start()
            self.control_panel.set_auto_running(True)
            self.log("🔁 Auto-running...")

    def stop_auto_run(self):
        self.is_auto_running = False
        self.run_timer.stop()
        self.control_panel.set_auto_running(False)

    def run_machine(self):
        if not self.tm or not self.tm.tape:
            if not self._init_machine():
                return
        self.stop_auto_run()
        try:
            self.tm.run()
            self._sync_visualizer()
            self.log("━" * 50)
            if self.tm.output_buffer:
                for i, out in enumerate(self.tm.output_buffer, 1):
                    self.log(f"📄 Output {i}:")
                    self.log(out)
                    if i < len(self.tm.output_buffer):
                        self.log("")
            else:
                self.log("ℹ️ No PRINT commands were executed.")
            self.log("━" * 50)
            stats = self.tm.get_stats()
            self.log(f"📊 Executed {stats['step_count']} steps total.")
        except RuntimeError as e:
            self.log(f"❌ {e}")
            self._sync_visualizer()
        except Exception as e:
            self.log(f"❌ RUNTIME ERROR: {e}")
            self._sync_visualizer()

    def reset_machine(self):
        self.stop_auto_run()
        self.tm = None
        self._sync_visualizer()
        self.log("🔄 Machine reset.")

    def load_example(self, name):
        em_map = self.config_panel.get_emoji_map()
        code = get_example_code(name, em_map)
        if code:
            self.editor.setPlainText(code)
            self.reset_machine()
            self.log(f"📋 Loaded example: {name}")
        else:
            self.log(f"❌ Example not found: {name}")

    def show_help(self):
        help_text = """
<h2>Emoji Turing Machine - Help</h2>

<h3>Language Constructs</h3>
<ul>
<li><b>🟢 State</b> - Set initial state</li>
<li><b>📼 ... ⏹️</b> - Define tape contents</li>
<li><b>📜 State Read Write Move NextState 🛑</b> - Define a rule</li>
<li><b>🖨️</b> - Print current tape state</li>
<li><b>🚀</b> - Execute (run to completion)</li>
</ul>

<h3>Movement Symbols</h3>
<ul>
<li><b>➡️</b> - Move right</li>
<li><b>⬅️</b> - Move left</li>
<li><b>⏸️</b> - Stay in place</li>
</ul>

<h3>Special Symbols</h3>
<ul>
<li><b>🏁</b> - Halt state</li>
<li><b>⬜</b> - Blank symbol</li>
<li><b>↵</b> - Newline (for multi-line output)</li>
</ul>

<h3>Keyboard Shortcuts</h3>
<ul>
<li><b>F5</b> - Run all</li>
<li><b>F10</b> - Step</li>
<li><b>F6</b> - Toggle auto-run</li>
<li><b>Escape</b> - Stop</li>
<li><b>Ctrl+R</b> - Reset</li>
<li><b>Ctrl+S</b> - Save file</li>
<li><b>Ctrl+O</b> - Open file</li>
<li><b>Ctrl+Scroll</b> - Zoom tape</li>
</ul>
"""
        QMessageBox.information(self, "Help - Emoji Turing Machine", help_text)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = EmojicodeGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()