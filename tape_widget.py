"""Custom tape visualization widget with zoom and interaction support."""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPolygon, QWheelEvent


class TapeWidget(QWidget):
    # Signal emitted when user double-clicks a cell
    cell_center_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tape = []
        self.head = 0
        self.state = "⏸️"
        self.step_count = 0
        self.cell_width = 60
        self.cell_height = 60
        self.show_indices = True
        self.last_rule = None
        self._newline_symbol = ""
        self._last_written_pos = -1  # Track last written position for highlighting
        self._scroll_offset = 0
        self.setMinimumHeight(140)
        self.setFont(QFont("Segoe UI Emoji", 24))
        self.setMouseTracking(True)
        self._hover_cell = -1

    def update_tape(self, tape, head, state, step_count=0, last_rule=None, 
                    newline_symbol="", last_written_pos=-1):
        """Update tape visualization with all parameters."""
        self.tape = tape if tape else []
        self.head = head
        self.state = state
        self.step_count = step_count
        self.last_rule = last_rule
        self._newline_symbol = newline_symbol
        self._last_written_pos = last_written_pos
        self.update()

    def center_on_cell(self, cell_index):
        """Center the view on a specific cell."""
        w = self.width()
        num_cells = max(1, w // self.cell_width)
        self._scroll_offset = cell_index - self.head + (num_cells // 2)
        self.update()

    def zoom_in(self):
        self.cell_width = min(120, self.cell_width + 10)
        self.cell_height = min(120, self.cell_height + 10)
        self.update()

    def zoom_out(self):
        self.cell_width = max(30, self.cell_width - 10)
        self.cell_height = max(30, self.cell_height - 10)
        self.update()

    def reset_zoom(self):
        self.cell_width = 60
        self.cell_height = 60
        self._scroll_offset = 0
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for scrolling and zooming."""
        delta = event.angleDelta().y()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            cells_to_scroll = delta // 120
            self._scroll_offset += cells_to_scroll
            self.update()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to center on cell."""
        w = self.width()
        num_cells = max(1, w // self.cell_width)
        start_idx = self.head - (num_cells // 2) + self._scroll_offset
        cell_at_mouse = start_idx + (event.position().x() // self.cell_width)
        if 0 <= cell_at_mouse < len(self.tape):
            self.cell_center_requested.emit(cell_at_mouse)

    def paintEvent(self, event):
        """Paint the tape visualization."""
        if not self.tape:
            self._paint_empty()
            return

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor("#1e1e1e"))

            w = self.width()
            h = self.height()
            num_cells = max(1, w // self.cell_width)
            start_idx = self.head - (num_cells // 2) + self._scroll_offset
            nl_sym = self._newline_symbol

            top_margin = 28 if self.show_indices else 18

            # Draw info bar at top
            rule_y = 2
            
            # State info
            painter.setPen(QColor("#00ff00"))
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            painter.drawText(10, rule_y + 12, f"State: {self.state}")

            # Step count
            painter.setPen(QColor("#aaaaaa"))
            painter.setFont(QFont("Consolas", 10))
            painter.drawText(150, rule_y + 12, f"Steps: {self.step_count:,}")

            # Last rule info
            if self.last_rule:
                painter.setPen(QColor("#888888"))
                painter.setFont(QFont("Consolas", 9))
                rule_text = (
                    f"Rule: [{self.last_rule['state']}, {self.last_rule['read']}] "
                    f"→ [{self.last_rule['write']}, {self.last_rule['move']}, "
                    f"{self.last_rule['next_state']}]"
                )
                painter.drawText(280, rule_y + 12, rule_text)

            # Zoom indicator
            painter.setPen(QColor("#555555"))
            painter.setFont(QFont("Consolas", 8))
            painter.drawText(w - 100, rule_y + 12, f"Zoom: {self.cell_width}px")

            # Draw cells
            for cell_offset in range(num_cells):
                i = start_idx + cell_offset
                x = cell_offset * self.cell_width
                y = top_margin
                rect = QRect(x, y, self.cell_width, self.cell_height)

                # Determine cell states
                is_valid_cell = 0 <= i < len(self.tape)
                is_newline = is_valid_cell and nl_sym and self.tape[i] == nl_sym
                is_head = (i == self.head)
                is_hover = (i == self._hover_cell)
                is_written = (i == self._last_written_pos)

                # Determine colors
                if is_head:
                    if is_written:
                        bg_color = QColor("#3a4510")
                        border_color = QColor("#88ff00")
                        border_width = 3
                    elif is_newline:
                        bg_color = QColor("#4a3510")
                        border_color = QColor("#ffcc00")
                        border_width = 2
                    else:
                        bg_color = QColor("#264f78")
                        border_color = QColor("#4fc1ff")
                        border_width = 2
                elif is_written:
                    bg_color = QColor("#2a3520")
                    border_color = QColor("#66aa00")
                    border_width = 2
                elif is_hover:
                    bg_color = QColor("#353535")
                    border_color = QColor("#666666")
                    border_width = 1
                elif is_newline:
                    bg_color = QColor("#2a2520")
                    border_color = QColor("#665500")
                    border_width = 1
                else:
                    bg_color = QColor("#252526")
                    border_color = QColor("#444444")
                    border_width = 1

                # Draw cell background
                painter.fillRect(rect, bg_color)
                painter.setPen(QPen(border_color, border_width))
                painter.drawRect(rect)

                # Draw cell indices
                if self.show_indices:
                    painter.setPen(QColor("#666666"))
                    painter.setFont(QFont("Consolas", 8))
                    index_text = str(i) if is_valid_cell else "·"
                    painter.drawText(
                        QRect(x, y + self.cell_height, self.cell_width, 15),
                        Qt.AlignmentFlag.AlignCenter,
                        index_text
                    )

                # Draw cell content
                if is_valid_cell:
                    current_sym = self.tape[i]
                    is_nl = (current_sym == "↵" or (nl_sym and current_sym == nl_sym))
                    
                    if is_nl:
                        text_color = QColor("#ffcc00")
                        font_size = max(12, min(24, self.cell_width // 3))
                        display_text = "↵"
                    else:
                        text_color = QColor("white")
                        font_size = max(14, min(28, self.cell_width // 2))
                        display_text = current_sym
                    
                    painter.setPen(text_color)
                    painter.setFont(QFont("Segoe UI Emoji", font_size))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, display_text)

            # Draw head triangle indicator
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

            # Draw left/right indicators if tape extends beyond view
            if start_idx > 0:
                painter.setPen(QColor("#666666"))
                painter.setFont(QFont("Segoe UI", 16))
                painter.drawText(QRect(5, top_margin + self.cell_height // 2 - 10, 20, 20), 
                               Qt.AlignmentFlag.AlignCenter, "◄")
            
            end_idx = start_idx + num_cells
            if end_idx < len(self.tape):
                painter.setPen(QColor("#666666"))
                painter.setFont(QFont("Segoe UI", 16))
                painter.drawText(QRect(w - 25, top_margin + self.cell_height // 2 - 10, 20, 20),
                               Qt.AlignmentFlag.AlignCenter, "►")

    def _paint_empty(self):
        """Paint empty state when no tape is loaded."""
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor("#1e1e1e"))
            
            painter.setPen(QColor("#666666"))
            painter.setFont(QFont("Segoe UI", 14))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No tape loaded")
            
            painter.setPen(QColor("#444444"))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(
                QRect(0, self.height() // 2 + 20, self.width(), 30),
                Qt.AlignmentFlag.AlignCenter,
                "Load an example or write emoji code to begin"
            )

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effect."""
        w = self.width()
        num_cells = max(1, w // self.cell_width)
        start_idx = self.head - (num_cells // 2) + self._scroll_offset
        cell_at_mouse = start_idx + (event.position().x() // self.cell_width)
        if cell_at_mouse != self._hover_cell:
            self._hover_cell = cell_at_mouse
            self.update()

    def leaveEvent(self, event):
        """Clear hover effect when mouse leaves widget."""
        self._hover_cell = -1
        self.update()