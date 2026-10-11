import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QFrame,
    QSlider, QComboBox
)
from PySide6.QtCore import Qt, QRect, QTimer, QPoint
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPolygon


class EmojiTuringMachine:
    """Core Turing Machine Engine driven purely by emoji mappings."""
    
    def __init__(self, emoji_map):
        self.em = emoji_map
        self.reset()

    def reset(self):
        self.tape = []
        self.head = 0
        self.state = None
        self.rules = {}
        self.halted = False
        self.output_buffer = []
        self.step_count = 0

    def parse(self, code):
        self.reset()
        tokens = code.split()
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token == self.em['INIT_STATE']:
                if i + 1 < len(tokens):
                    self.state = tokens[i+1]
                    i += 2
                    continue
                    
            elif token == self.em['TAPE_START']:
                self.tape = []
                i += 1
                while i < len(tokens) and tokens[i] != self.em['TAPE_END']:
                    self.tape.append(tokens[i])
                    i += 1
                if not self.tape:
                    self.tape = [self.em['BLANK']]
                i += 1
                continue
                
            elif token == self.em['RULE_START']:
                if i + 6 < len(tokens):
                    c_state = tokens[i+1]
                    read = tokens[i+2]
                    write = tokens[i+3]
                    move = tokens[i+4]
                    n_state = tokens[i+5]
                    
                    d_move = 'S'
                    if move == self.em['MOVE_R']:
                        d_move = 'R'
                    elif move == self.em['MOVE_L']:
                        d_move = 'L'
                    elif move == self.em['MOVE_STAY']:
                        d_move = 'S'
                    else:
                        raise ValueError(f"Invalid move symbol: {move}")
                    
                    self.rules[(c_state, read)] = (write, d_move, n_state)
                    i += 6
                    if i < len(tokens) and tokens[i] == self.em['RULE_END']:
                        i += 1
                    continue
                    
            elif token == self.em['PRINT']:
                self.output_buffer.append(self.format_tape())
                i += 1
                continue
                
            i += 1
            
        if not self.state:
            raise ValueError("No initial state defined.")

    def format_tape(self):
        """Formats the tape into complex multi-line output using the NEWLINE symbol."""
        output = ""
        nl_sym = self.em.get('NEWLINE', '')
        blank_sym = self.em['BLANK']
        
        for sym in self.tape:
            if sym == nl_sym:
                output += "\n"
            elif sym == blank_sym:
                continue
            else:
                output += sym
                
        return output.strip()

    def step(self):
        if self.halted or self.state == self.em['HALT_STATE']:
            self.halted = True
            return False

        if self.head < 0:
            self.tape.insert(0, self.em['BLANK'])
            self.head = 0
        elif self.head >= len(self.tape):
            self.tape.append(self.em['BLANK'])

        read_sym = self.tape[self.head]
        key = (self.state, read_sym)

        if key not in self.rules:
            self.halted = True
            return False

        write_sym, move, next_state = self.rules[key]
        
        self.tape[self.head] = write_sym
        self.state = next_state
        self.step_count += 1
        
        if move == 'R':
            self.head += 1
        elif move == 'L':
            self.head -= 1

        if self.state == self.em['HALT_STATE']:
            self.halted = True

        return True

    def run(self, max_steps=10000):
        steps = 0
        while self.step() and steps < max_steps:
            steps += 1
        if steps == max_steps:
            raise RuntimeError("Exceeded maximum steps (infinite loop).")


class TapeWidget(QWidget):
    """Custom widget to draw the infinite tape using QPainter."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tape = []
        self.head = 0
        self.state = "⏸️"
        self.step_count = 0
        self.cell_width = 60
        self.cell_height = 60
        self.show_indices = True
        self.setMinimumHeight(120)
        self.setFont(QFont("Segoe UI Emoji", 24))

    def update_tape(self, tape, head, state, step_count=0):
        self.tape = tape if tape else []
        self.head = head
        self.state = state
        self.step_count = step_count
        self.update()

    def paintEvent(self, event):
        if not self.tape:
            with QPainter(self) as painter:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.fillRect(self.rect(), QColor("#1e1e1e"))
                painter.setPen(QColor("#666666"))
                painter.setFont(QFont("Segoe UI", 14))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No tape loaded")
            return

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor("#1e1e1e"))

            w = self.width()
            num_cells = max(1, w // self.cell_width)
            start_idx = self.head - (num_cells // 2)
            start_idx = max(-num_cells // 2, start_idx)

            top_margin = 25 if self.show_indices else 15
            
            for cell_offset in range(num_cells):
                i = start_idx + cell_offset
                x = cell_offset * self.cell_width
                y = top_margin
                rect = QRect(x, y, self.cell_width, self.cell_height)

                is_newline = (0 <= i < len(self.tape) and self.tape[i] == self.parent().tm.em.get('NEWLINE', '') if hasattr(self.parent(), 'tm') and self.parent().tm else False)
                
                if i == self.head:
                    painter.fillRect(rect, QColor("#4a3510" if is_newline else "#264f78"))
                    painter.setPen(QPen(QColor("#ffcc00" if is_newline else "#4fc1ff"), 2))
                    painter.drawRect(rect)
                else:
                    painter.fillRect(rect, QColor("#2a2520" if is_newline else "#252526"))
                    painter.setPen(QPen(QColor("#665500" if is_newline else "#444444"), 1))
                    painter.drawRect(rect)

                if self.show_indices:
                    painter.setPen(QColor("#666666"))
                    painter.setFont(QFont("Consolas", 8))
                    painter.drawText(
                        QRect(x, y + self.cell_height, self.cell_width, 15),
                        Qt.AlignmentFlag.AlignCenter,
                        str(i)
                    )

                if 0 <= i < len(self.tape):
                    current_sym = self.tape[i]
                    is_nl = (current_sym == "↵")
                    painter.setPen(QColor("#ffcc00" if is_nl else "white"))
                    painter.setFont(QFont("Consolas", 20 if is_nl else 24))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, current_sym)

            if start_idx <= self.head < start_idx + num_cells:
                head_x = (self.head - start_idx) * self.cell_width + self.cell_width // 2
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor("#4fc1ff"))
                
                triangle = QPolygon([
                    QPoint(head_x, top_margin - 2),
                    QPoint(head_x - 8, top_margin - 15),
                    QPoint(head_x + 8, top_margin - 15)
                ])
                painter.drawPolygon(triangle)
            
            painter.setPen(QColor("#00ff00"))
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            painter.drawText(10, 15, f"State: {self.state}")
            
            painter.setPen(QColor("#aaaaaa"))
            painter.setFont(QFont("Consolas", 10))
            painter.drawText(200, 15, f"Steps: {self.step_count}")


class EmojicodeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⬛ Pure Emoji Turing Machine (Complex Outputs) ⬛")
        self.setGeometry(100, 100, 1200, 850)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.tm = None
        self.emoji_inputs = {}
        self.run_timer = QTimer()
        self.run_timer.setInterval(100)
        self.run_timer.timeout.connect(self.auto_step)
        self.is_auto_running = False
        
        self.setup_styles()
        self.build_left_panel(main_layout)
        self.build_right_panel(main_layout)
        
        self.log("Welcome! New Feature: '↵' (Newline) symbol added.")
        self.log("Use it in your tape to create complex multi-line outputs!")

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QWidget { background-color: #2b2b2b; color: #d4d4d4; }
            QLabel { background-color: transparent; }
            QLineEdit { background-color: #45494a; color: white; border: 1px solid #555; border-radius: 4px; padding: 2px; }
            QLineEdit:focus { border: 1px solid #4fc1ff; }
            QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; border-radius: 4px; font-family: 'Segoe UI Emoji'; font-size: 16px; }
            QTextEdit:focus { border: 1px solid #4fc1ff; }
            QPushButton { background-color: #3c3f41; color: white; border: 1px solid #555; border-radius: 4px; padding: 8px 16px; font-size: 14px; min-height: 30px; }
            QPushButton:hover { background-color: #505355; }
            QPushButton:pressed { background-color: #2b2d2e; }
            QPushButton:disabled { background-color: #2a2a2a; color: #555; }
            QComboBox { background-color: #45494a; color: white; border: 1px solid #555; border-radius: 4px; padding: 6px; min-height: 25px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #45494a; color: white; selection-background-color: #264f78; }
            QScrollArea { border: none; background-color: transparent; }
            QSlider::groove:horizontal { border: 1px solid #444; height: 6px; background: #2b2b2b; border-radius: 3px; }
            QSlider::handle:horizontal { background: #4fc1ff; border: none; width: 16px; margin: -5px 0; border-radius: 8px; }
        """)

    def build_left_panel(self, parent_layout):
        left_frame = QFrame()
        left_frame.setFixedWidth(260)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("⚙️ Language Config")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        
        sub = QLabel("Includes '↵' for multi-line\nformatting in outputs:")
        sub.setStyleSheet("color: #888; font-size: 10px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)

        labels = {
            'INIT_STATE': 'Initial State', 'HALT_STATE': 'Halt State', 'BLANK': 'Blank Symbol',
            'TAPE_START': 'Tape Start', 'TAPE_END': 'Tape End', 'RULE_START': 'Rule Start',
            'RULE_END': 'Rule End', 'MOVE_R': 'Move Right', 'MOVE_L': 'Move Left',
            'MOVE_STAY': 'Move Stay', 'RUN': 'Execute', 'PRINT': 'Print Tape',
            'NEWLINE': 'Newline (↵)'
        }

        for key, text in labels.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0,0,0,0)
            
            lbl = QLabel(text)
            lbl.setFixedWidth(100)
            
            inp = QLineEdit()
            inp.setFixedWidth(50)
            inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inp.setFont(QFont("Segoe UI Emoji", 16))
            inp.setText(self.get_default_emoji(key))
            
            self.emoji_inputs[key] = inp
            row_layout.addWidget(lbl)
            row_layout.addWidget(inp)
            row_layout.addStretch()
            scroll_layout.addWidget(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        left_layout.addWidget(scroll)
        parent_layout.addWidget(left_frame)

    def get_default_emoji(self, key):
        defaults = {
            'INIT_STATE': "🟢", 'HALT_STATE': "🏁", 'BLANK': "⬜",
            'TAPE_START': "📼", 'TAPE_END': "⏹️", 'RULE_START': "📜",
            'RULE_END': "🛑", 'MOVE_R': "➡️", 'MOVE_L': "⬅️",
            'MOVE_STAY': "⏸️", 'RUN': "🚀", 'PRINT': "🖨️",
            'NEWLINE': "↵"
        }
        return defaults.get(key, "❓")

    def get_emoji_map(self):
        return {k: v.text() for k, v in self.emoji_inputs.items()}

    def build_right_panel(self, parent_layout):
        right_frame = QWidget()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(8)
        
        self.tape_widget = TapeWidget()
        right_layout.addWidget(self.tape_widget, stretch=2)

        editor_label = QLabel("💾 Pure Emoji Code")
        editor_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        right_layout.addWidget(editor_label)
        
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Segoe UI Emoji", 16))
        right_layout.addWidget(self.editor, stretch=3)

        ctrl_layout = QHBoxLayout()
        speed_label = QLabel("⏱️ Speed:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_value = QLabel("51ms")
        speed_value.setFixedWidth(40)
        self.speed_value_label = speed_value
        
        ctrl_layout.addWidget(speed_label)
        ctrl_layout.addWidget(self.speed_slider)
        ctrl_layout.addWidget(speed_value)
        ctrl_layout.addStretch()

        self.example_combo = QComboBox()
        self.example_combo.addItems([
            "Binary Incrementer", 
            "Math: Binary Decrementer", 
            "Game: Rock-Paper-Scissors", 
            "Output: ASCII Box Maker",
            "Output: Inventory Filter",
            "Output: Battle Logger"
        ])
        btn_load = QPushButton("📋 Load")
        btn_load.setFixedWidth(80)
        btn_load.clicked.connect(self.load_example)
        
        ctrl_layout.addWidget(self.example_combo)
        ctrl_layout.addWidget(btn_load)
        right_layout.addLayout(ctrl_layout)

        btn_layout = QHBoxLayout()
        self.btn_step = QPushButton("▶️ Step")
        self.btn_run = QPushButton("⏩ Run All")
        self.btn_auto = QPushButton("🔁 Auto Run")
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.setEnabled(False)
        self.btn_reset = QPushButton("🔄 Reset")
        
        self.btn_step.clicked.connect(self.step_machine)
        self.btn_run.clicked.connect(self.run_machine)
        self.btn_auto.clicked.connect(self.toggle_auto_run)
        self.btn_stop.clicked.connect(self.stop_auto_run)
        self.btn_reset.clicked.connect(self.reset_machine)
        
        btn_layout.addWidget(self.btn_step)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_auto)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_reset)
        right_layout.addLayout(btn_layout)

        console_label = QLabel("🖥️ Output")
        console_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        right_layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 12))
        self.console.setStyleSheet("color: #4ec9b0;")
        right_layout.addWidget(self.console, stretch=2)

        parent_layout.addWidget(right_frame, stretch=1)

    def update_speed(self, value):
        interval = max(1, 101 - value)
        self.run_timer.setInterval(interval)
        self.speed_value_label.setText(f"{interval}ms")

    def log(self, msg):
        self.console.append(msg)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def sync_visualizer(self):
        if self.tm:
            self.tape_widget.update_tape(self.tm.tape, self.tm.head, self.tm.state if self.tm.state else "⏸️", self.tm.step_count)
        else:
            self.tape_widget.update_tape([], 0, "⏸️", 0)

    def init_machine(self):
        em_map = self.get_emoji_map()
        code = self.editor.toPlainText().strip()
        if not code:
            self.log("❌ Write some emoji code first!")
            return False
        for key, val in em_map.items():
            if not val:
                self.log(f"❌ Please define an emoji for: {key}")
                return False
        try:
            self.tm = EmojiTuringMachine(em_map)
            self.tm.parse(code)
            self.sync_visualizer()
            self.log(f"✅ Parsed successfully. Rules: {len(self.tm.rules)}")
            return True
        except Exception as e:
            self.log(f"❌ PARSE ERROR: {str(e)}")
            return False

    def step_machine(self):
        if not self.tm or not self.tm.tape:
            if not self.init_machine(): return
        if self.tm.halted:
            self.log("🏁 Machine is already halted."); return
        success = self.tm.step()
        self.sync_visualizer()
        if not success:
            if self.tm.state == self.get_emoji_map()['HALT_STATE']:
                self.log("🏁 Machine halted successfully.")
            else:
                self.log(f"💥 Crashed at step {self.tm.step_count}.")

    def auto_step(self):
        if not self.tm or self.tm.halted:
            self.stop_auto_run(); return
        self.tm.step()
        self.sync_visualizer()
        if self.tm.halted:
            self.stop_auto_run()
            self.log("🏁 Auto-run finished.")

    def toggle_auto_run(self):
        if self.is_auto_running:
            self.stop_auto_run()
        else:
            if not self.tm or not self.tm.tape:
                if not self.init_machine(): return
            if self.tm.halted:
                self.log("🏁 Machine is already halted."); return
            self.is_auto_running = True
            self.run_timer.start()
            self.btn_auto.setText("⏸️ Pause")
            self.btn_stop.setEnabled(True)
            self.btn_step.setEnabled(False)
            self.btn_run.setEnabled(False)
            self.log("🔁 Auto-running...")

    def stop_auto_run(self):
        self.is_auto_running = False
        self.run_timer.stop()
        self.btn_auto.setText("🔁 Auto Run")
        self.btn_stop.setEnabled(False)
        self.btn_step.setEnabled(True)
        self.btn_run.setEnabled(True)

    def run_machine(self):
        if not self.tm or not self.tm.tape:
            if not self.init_machine(): return
        self.stop_auto_run()
        try:
            self.tm.run()
            self.sync_visualizer()
            self.log("--------------------------------------------------")
            for out in self.tm.output_buffer:
                self.log(out)
            self.log("--------------------------------------------------")
            self.log(f"📊 Executed {self.tm.step_count} steps.")
        except Exception as e:
            self.log(f"❌ RUNTIME ERROR: {str(e)}")
            self.sync_visualizer()

    def reset_machine(self):
        self.stop_auto_run()
        self.tm = None
        self.sync_visualizer()
        self.log("🔄 Machine reset.")

    def get_example_code(self, name):
        em = self.get_emoji_map()
        nl = em['NEWLINE']
        
        if name == "Binary Incrementer":
            return (
                f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
                f"{em['TAPE_START']} 1 1 1 {em['BLANK']} {em['TAPE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 1 0 {em['MOVE_L']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} {em['BLANK']} 1 {em['MOVE_R']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['PRINT']}\n" f"{em['RUN']}"
            )
        elif name == "Math: Binary Decrementer":
            return (
                f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
                f"{em['TAPE_START']} 1 0 0 0 {em['BLANK']} {em['TAPE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 1 1 {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 0 0 {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} {em['BLANK']} {em['BLANK']} {em['MOVE_L']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 0 1 {em['MOVE_L']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 1 0 {em['MOVE_R']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 {em['BLANK']} ❌ {em['MOVE_STAY']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['PRINT']}\n" f"{em['RUN']}"
            )
        elif name == "Game: Rock-Paper-Scissors":
            return (
                f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
                f"{em['TAPE_START']} ✊ ✋ {em['BLANK']} {em['TAPE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} ✊ ✊ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} ✋ ✋ {em['MOVE_R']} 🟡 {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} ✌️ ✌️ {em['MOVE_R']} 🟣 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 ✊ = {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 ✋ 2 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 ✌️ 1 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 ✊ 1 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 ✋ = {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 ✌️ 2 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟣 ✊ 2 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟣 ✋ 1 {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟣 ✌️ = {em['MOVE_L']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['PRINT']}\n" f"{em['RUN']}"
            )
        elif name == "Output: ASCII Box Maker":
            return (
                f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
                f"{em['TAPE_START']} / - - - - - \\ {nl} | {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} | {nl} \\ - - - - - / {em['TAPE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} / / {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} - - {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} \\ \\ {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} {nl} {nl} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} | | {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 {em['BLANK']} ⭐ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 | | {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['PRINT']}\n" f"{em['RUN']}"
            )
        elif name == "Output: Inventory Filter":
            return (
                f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
                f"{em['TAPE_START']} 🍎 🗑️ ⚔️ 🗑️ 🛡️ {em['TAPE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 🍎 🍎 {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} ⚔️ ⚔️ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 🛡️ 🛡️ {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 🗑️ {em['BLANK']} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 🍎 {nl} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 ⚔️ {nl} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 🛡️ {nl} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 🗑️ {em['BLANK']} {em['MOVE_L']} 🟡 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 {em['BLANK']} {em['BLANK']} {em['MOVE_STAY']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 🍎 🍎 {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 ⚔️ ⚔️ {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 🛡️ 🛡️ {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 {nl} {nl} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟡 {em['BLANK']} {em['BLANK']} {em['MOVE_R']} {em['INIT_STATE']} {em['RULE_END']}\n"
                f"{em['PRINT']}\n" f"{em['RUN']}"
            )
        elif name == "Output: Battle Logger":
            # FIX: Replaced {em['END_TAPE']} with {em['BLANK']}
            return (
                f"{em['INIT_STATE']} {em['INIT_STATE']}\n"
                f"{em['TAPE_START']} 🧙 🧟 {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['BLANK']} {em['TAPE_END']}\n"
                f"# Copy combatants\n"
                f"{em['RULE_START']} {em['INIT_STATE']} 🧙 🧙 {em['MOVE_R']} 🔵 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵 🧟 🧟 {em['MOVE_R']} 🟡 {em['RULE_END']}\n"
                f"# Write combat symbol\n"
                f"{em['RULE_START']} 🟡 {em['BLANK']} ⚔️ {em['MOVE_R']} 🟣 {em['RULE_END']}\n"
                f"# Write line break\n"
                f"{em['RULE_START']} 🟣 {em['BLANK']} {nl} {em['MOVE_R']} 🟠 {em['RULE_END']}\n"
                f"# Write BAM!\n"
                f"{em['RULE_START']} 🟠 {em['BLANK']} B {em['MOVE_R']} 🟤 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟤 {em['BLANK']} A {em['MOVE_R']} 🟢2 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟢2 {em['BLANK']} M {em['MOVE_R']} 🔵2 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵2 {em['BLANK']} ! {em['MOVE_R']} 🟡2 {em['RULE_END']}\n"
                f"# Write line break\n"
                f"{em['RULE_START']} 🟡2 {em['BLANK']} {nl} {em['MOVE_R']} 🟣2 {em['RULE_END']}\n"
                f"# Write winner\n"
                f"{em['RULE_START']} 🟣2 {em['BLANK']} 🧙 {em['MOVE_R']} 🟠2 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟠2 {em['BLANK']} W {em['MOVE_R']} 🟤2 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟤2 {em['BLANK']} I {em['MOVE_R']} 🟢3 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🟢3 {em['BLANK']} N {em['MOVE_R']} 🔵3 {em['RULE_END']}\n"
                f"{em['RULE_START']} 🔵3 {em['BLANK']} S {em['MOVE_STAY']} {em['HALT_STATE']} {em['RULE_END']}\n"
                f"{em['PRINT']}\n" f"{em['RUN']}"
            )
        return ""

    def load_example(self):
        name = self.example_combo.currentText()
        code = self.get_example_code(name)
        self.editor.setPlainText(code)
        self.reset_machine()
        self.log(f"📋 Loaded: {name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmojicodeGUI()
    window.show()
    sys.exit(app.exec())