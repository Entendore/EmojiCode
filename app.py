"""Main application window for the Emoji Turing Machine."""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QFrame, QStatusBar, QFileDialog, QMessageBox,
    QPushButton, QMenuBar, QSpinBox
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QAction

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
        self.setGeometry(100, 100, 1300, 920)
        self.setMinimumSize(900, 600)

        self.tm = None
        self.max_steps = 10000
        self.run_timer = QTimer()
        self.run_timer.setInterval(51)
        self.run_timer.timeout.connect(self._auto_step)
        self.is_auto_running = False

        self._setup_styles()
        self._setup_menu_bar()
        self._setup_ui()
        self._setup_shortcuts()
        self._setup_status_bar()

        self.log("Welcome to the Emoji Turing Machine!")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("📖 Use '↵' for multi-line formatting in outputs")
        self.log("⌨️  Shortcuts: F5=Run, F10=Step, F6=Auto, Esc=Stop")
        self.log("🔍 Ctrl+Scroll to zoom the tape view")
        self.log("💡 Double-click tape cell to center on it")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _setup_styles(self):
        self.setStyleSheet(MAIN_STYLE)

    def _setup_menu_bar(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border-bottom: 1px solid #333;
                padding: 2px;
            }
            QMenuBar::item {
                padding: 4px 12px;
            }
            QMenuBar::item:selected {
                background-color: #264f78;
                border-radius: 4px;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #444;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 30px 6px 20px;
            }
            QMenu::item:selected {
                background-color: #264f78;
                border-radius: 3px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444;
                margin: 4px 10px;
            }
        """)

        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Run menu
        run_menu = menubar.addMenu("&Run")
        run_menu.addAction("Run All", self.run_machine, "F5")
        run_menu.addAction("Step", self.step_machine, "F10")
        run_menu.addAction("Toggle Auto-Run", self.toggle_auto_run, "F6")
        run_menu.addAction("Stop", self.stop_auto_run, "Escape")
        run_menu.addSeparator()
        run_menu.addAction("Reset", self.reset_machine, "Ctrl+R")

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        settings_menu.addAction("Configure Max Steps...", self._configure_max_steps)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("Help", self.show_help, "F1")
        help_menu.addSeparator()
        help_menu.addAction("About", self._show_about)

    def _show_about(self):
        QMessageBox.about(
            self,
            "About Emoji Turing Machine",
            "<h2>⬛ Pure Emoji Turing Machine ⬛</h2>"
            "<p>Version 1.0</p>"
            "<p>A Turing Machine simulator where all language constructs "
            "are defined using emoji symbols.</p>"
            "<p>Write programs using only emojis - no traditional "
            "programming syntax required!</p>"
            "<hr>"
            "<p>Built with Python & PySide6</p>"
        )

    def _configure_max_steps(self):
        """Dialog to configure maximum steps."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Configure Max Steps")
        dialog.setStyleSheet("""
            QMessageBox { background-color: #2b2b2b; color: #d4d4d4; }
            QLabel { color: #d4d4d4; }
            QPushButton { min-width: 80px; }
        """)
        
        layout = QVBoxLayout()
        label = QLabel(f"Maximum steps before auto-stop (current: {self.max_steps}):")
        label.setStyleSheet("margin-bottom: 10px;")
        
        spin = QSpinBox()
        spin.setRange(100, 1000000)
        spin.setSingleStep(1000)
        spin.setValue(self.max_steps)
        spin.setStyleSheet("padding: 5px; font-size: 14px;")
        
        layout.addWidget(label)
        layout.addWidget(spin)
        
        dialog.setLayout(layout)
        dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        ok_btn = dialog.addButton("Apply", QMessageBox.ButtonRole.AcceptRole)
        
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            self.max_steps = spin.value()
            self.log(f"⚙️ Max steps set to: {self.max_steps:,}")

    def _new_file(self):
        """Clear editor and reset machine."""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, "New File",
                "Discard current code?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        self.editor.clear()
        self.reset_machine()
        self.log("📄 New file created.")

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
        self.tape_widget.cell_center_requested.connect(self._center_on_cell)
        right_layout.addWidget(self.tape_widget, stretch=2)

        # Code editor
        editor_label = QLabel("💾 Pure Emoji Code")
        editor_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        right_layout.addWidget(editor_label)

        self.editor = QTextEdit()
        self.editor.setObjectName("editor")
        self.editor.setStyleSheet(EDITOR_STYLE)
        self.editor.setFont(QFont("Segoe UI Emoji", 16))
        self.editor.setPlaceholderText(
            "Write your emoji Turing machine code here...\n"
            "Or load an example from the dropdown below.\n\n"
            "Example structure:\n"
            "🟢 🟢\n"
            "📼 1 0 1 ⬜ ⏹️\n"
            "📜 🟢 1 0 ➡️ 🟢 🛑\n"
            "🖨️\n"
            "🚀"
        )
        self.editor.setAcceptRichText(False)
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

        # Console output - MUST be created BEFORE buttons reference it
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setStyleSheet(CONSOLE_STYLE)
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 12))
        self.console.setAcceptRichText(False)

        # Console header with buttons (AFTER console is created)
        console_header = QHBoxLayout()
        console_label = QLabel("🖥️ Output")
        console_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        console_header.addWidget(console_label)
        console_header.addStretch()

        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.setFixedWidth(70)
        btn_clear.setToolTip("Clear console output")
        btn_clear.setStyleSheet("padding: 4px 8px; font-size: 11px; min-height: 20px;")
        btn_clear.clicked.connect(self.console.clear)
        console_header.addWidget(btn_clear)

        btn_copy = QPushButton("📋 Copy")
        btn_copy.setFixedWidth(70)
        btn_copy.setToolTip("Copy output to clipboard")
        btn_copy.setStyleSheet("padding: 4px 8px; font-size: 11px; min-height: 20px;")
        btn_copy.clicked.connect(self._copy_output)
        console_header.addWidget(btn_copy)

        right_layout.addLayout(console_header)
        right_layout.addWidget(self.console, stretch=2)

        main_layout.addWidget(right_frame, stretch=1)

    def _center_on_cell(self, cell_index):
        """Center tape view on a specific cell."""
        self.tape_widget.center_on_cell(cell_index)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        shortcuts = [
            (QKeySequence(Qt.Key.Key_F1), self.show_help),
            (QKeySequence(Qt.Key.Key_F5), self.run_machine),
            (QKeySequence(Qt.Key.Key_F10), self.step_machine),
            (QKeySequence(Qt.Key.Key_F6), self.toggle_auto_run),
            (QKeySequence(Qt.Key.Key_Escape), self.stop_auto_run),
            (QKeySequence("Ctrl+R"), self.reset_machine),
            (QKeySequence("Ctrl+S"), self._save_file),
            (QKeySequence("Ctrl+O"), self._open_file),
            (QKeySequence("Ctrl+N"), self._new_file),
            (QKeySequence("Ctrl+="), self.tape_widget.zoom_in),
            (QKeySequence("Ctrl+-"), self.tape_widget.zoom_out),
            (QKeySequence("Ctrl+0"), self.tape_widget.reset_zoom),
        ]
        
        for key_seq, slot in shortcuts:
            shortcut = QShortcut(key_seq, self)
            shortcut.activated.connect(slot)

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
            halted_indicator = " ⏹️" if self.tm.halted else " ▶️"
            running_indicator = " 🔄" if self.is_auto_running else ""
            self.status_state.setText(f"State: {state_text}{halted_indicator}{running_indicator}")
            self.status_rules.setText(f"Rules: {stats['rule_count']}")
            self.status_steps.setText(f"Steps: {stats['step_count']:,}")
            self.status_tape.setText(f"Tape: {stats['tape_length']} cells | Head: {stats['head_position']}")
        else:
            self.status_state.setText("State: —")
            self.status_rules.setText("Rules: —")
            self.status_steps.setText("Steps: —")
            self.status_tape.setText("Tape: —")

    def _set_timer_interval(self, interval):
        self.run_timer.setInterval(interval)

    def log(self, msg):
        """Add message to console with auto-scroll."""
        self.console.append(msg)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _copy_output(self):
        """Copy console output to clipboard."""
        text = self.console.toPlainText()
        if text:
            try:
                QApplication.clipboard().setText(text)
                self.log("📋 Output copied to clipboard!")
            except Exception as e:
                self.log(f"❌ Failed to copy: {e}")
        else:
            self.log("ℹ️ Nothing to copy - output is empty.")

    def _save_file(self):
        """Save editor content to file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Code", "",
            "Emoji Code Files (*.emoji);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.log(f"💾 Saved to: {path}")
            except Exception as e:
                self.log(f"❌ Failed to save: {e}")
                QMessageBox.warning(self, "Save Error", f"Could not save file:\n{e}")

    def _open_file(self):
        """Open file into editor."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Code", "",
            "Emoji Code Files (*.emoji);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.reset_machine()
                self.log(f"📂 Opened: {path}")
            except Exception as e:
                self.log(f"❌ Failed to open: {e}")
                QMessageBox.warning(self, "Open Error", f"Could not open file:\n{e}")

    def _sync_visualizer(self):
        """Update tape widget with current TM state."""
        if self.tm:
            self.tape_widget.update_tape(
                tape=self.tm.tape,
                head=self.tm.head,
                state=self.tm.state if self.tm.state else "⏸️",
                step_count=self.tm.step_count,
                last_rule=self.tm.last_rule,
                newline_symbol=self.tm.em.get('NEWLINE', ''),
                last_written_pos=self.tm.last_written_pos
            )
        else:
            self.tape_widget.update_tape([], 0, "⏸️", 0)
        self._update_status_bar()

    def _init_machine(self):
        """Initialize or reinitialize the Turing machine."""
        em_map = self.config_panel.get_emoji_map()
        code = self.editor.toPlainText().strip()

        if not code:
            self.log("❌ Write some emoji code first!")
            return False

        valid, error = self.config_panel.validate()
        if not valid:
            self.log(f"❌ {error}")
            return False

        # Check for duplicate emojis that could cause issues
        emoji_values = list(em_map.values())
        if len(emoji_values) != len(set(emoji_values)):
            duplicates = [v for v in emoji_values if emoji_values.count(v) > 1]
            self.log(f"⚠️ Warning: Duplicate emojis detected: {set(duplicates)}")
            self.log("   This may cause parsing issues!")

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
        except KeyError as e:
            self.log(f"❌ CONFIG ERROR: Missing emoji mapping for {e}")
        except Exception as e:
            self.log(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return False

    def step_machine(self):
        """Execute a single step."""
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
                self._show_final_tape()
            else:
                self.log(f"💥 Crashed at step {self.tm.step_count:,}")
                self.log(f"   State: {self.tm.state}, Position: {self.tm.head}")
                self.log(f"   Symbol at head: {self.tm.tape[self.tm.head] if 0 <= self.tm.head < len(self.tm.tape) else 'OUT OF BOUNDS'}")

    def _show_final_tape(self):
        """Show final tape state when machine halts."""
        if self.tm and self.tm.tape:
            tape_str = self.tm.format_tape()
            if tape_str:
                self.log(f"📄 Final tape: {tape_str}")

    def _auto_step(self):
        """Execute one auto-step."""
        if not self.tm or self.tm.halted:
            self.stop_auto_run()
            return
        success = self.tm.step()
        self._sync_visualizer()
        if self.tm.halted or not success:
            self.stop_auto_run()
            if self.tm.halted:
                em = self.config_panel.get_emoji_map()
                if self.tm.state == em['HALT_STATE']:
                    self.log("🏁 Auto-run finished successfully.")
                else:
                    self.log("⚠️ Auto-run stopped - machine crashed.")
            else:
                self.log("⚠️ Auto-run stopped - no matching rule.")

    def toggle_auto_run(self):
        """Toggle auto-run mode."""
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
            self.log("🔁 Auto-running... (Press F6 or Esc to stop)")

    def stop_auto_run(self):
        """Stop auto-run mode."""
        was_running = self.is_auto_running
        self.is_auto_running = False
        self.run_timer.stop()
        self.control_panel.set_auto_running(False)
        if was_running:
            self.log("⏹️ Auto-run stopped.")

    def run_machine(self):
        """Run machine to completion."""
        if not self.tm or not self.tm.tape:
            if not self._init_machine():
                return
        self.stop_auto_run()
        
        self.log("⏩ Running to completion...")
        
        try:
            self.tm.run(max_steps=self.max_steps)
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
            self.log(f"📊 Executed {stats['step_count']:,} steps total.")
            
            if self.tm.halted:
                em = self.config_panel.get_emoji_map()
                if self.tm.state == em['HALT_STATE']:
                    self.log("✅ Machine halted successfully.")
                else:
                    self.log("⚠️ Machine stopped (crashed).")
                    self._show_final_tape()
                    
        except RuntimeError as e:
            self.log(f"❌ {e}")
            self._sync_visualizer()
        except Exception as e:
            self.log(f"❌ RUNTIME ERROR: {type(e).__name__}: {e}")
            self._sync_visualizer()

    def reset_machine(self):
        """Reset the Turing machine."""
        self.stop_auto_run()
        self.tm = None
        self._sync_visualizer()
        self.log("🔄 Machine reset.")

    def load_example(self, name):
        """Load an example program."""
        em_map = self.config_panel.get_emoji_map()
        code = get_example_code(name, em_map)
        if code:
            self.editor.setPlainText(code)
            self.reset_machine()
            self.log(f"📋 Loaded example: {name}")
        else:
            self.log(f"❌ Example not found: {name}")

    def show_help(self):
        """Show help dialog."""
        help_text = """
<h2>Emoji Turing Machine - Help</h2>

<h3>📚 Language Constructs</h3>
<table cellpadding="5" style="font-size: 12px;">
<tr><td><b>🟢 State</b></td><td>Set initial state</td></tr>
<tr><td><b>📼 ... ⏹️</b></td><td>Define tape contents</td></tr>
<tr><td><b>📜 State Read Write Move NextState 🛑</b></td><td>Define a transition rule</td></tr>
<tr><td><b>🖨️</b></td><td>Print current tape state</td></tr>
<tr><td><b>🚀</b></td><td>Execute (run to completion)</td></tr>
<tr><td><b># text</b></td><td>Comment (ignored)</td></tr>
</table>

<h3>➡️ Movement Symbols</h3>
<table cellpadding="5" style="font-size: 12px;">
<tr><td><b>➡️</b></td><td>Move head right</td></tr>
<tr><td><b>⬅️</b></td><td>Move head left</td></tr>
<tr><td><b>⏸️</b></td><td>Stay in place</td></tr>
</table>

<h3>⭐ Special Symbols</h3>
<table cellpadding="5" style="font-size: 12px;">
<tr><td><b>🏁</b></td><td>Halt state (machine stops)</td></tr>
<tr><td><b>⬜</b></td><td>Blank symbol</td></tr>
<tr><td><b>↵</b></td><td>Newline (for multi-line output)</td></tr>
</table>

<h3>⌨️ Keyboard Shortcuts</h3>
<table cellpadding="5" style="font-size: 12px;">
<tr><td><b>F1</b></td><td>Show help</td></tr>
<tr><td><b>F5</b></td><td>Run all</td></tr>
<tr><td><b>F6</b></td><td>Toggle auto-run</td></tr>
<tr><td><b>F10</b></td><td>Single step</td></tr>
<tr><td><b>Escape</b></td><td>Stop auto-run</td></tr>
<tr><td><b>Ctrl+R</b></td><td>Reset machine</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save file</td></tr>
<tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>
<tr><td><b>Ctrl+N</b></td><td>New file</td></tr>
<tr><td><b>Ctrl+Scroll</b></td><td>Zoom tape</td></tr>
<tr><td><b>Ctrl+0</b></td><td>Reset zoom</td></tr>
</table>

<h3>💡 Tips</h3>
<ul>
<li>Configure custom emojis in the left panel</li>
<li>Use # for comments in your code</li>
<li>Scroll the tape with mouse wheel</li>
<li>Double-click a tape cell to center on it</li>
<li>Watch the status bar for machine state</li>
<li>Configure max steps in Settings menu</li>
</ul>
"""
        QMessageBox.information(self, "Help - Emoji Turing Machine", help_text)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = EmojicodeGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()