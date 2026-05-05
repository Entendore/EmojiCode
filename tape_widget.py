"""Custom tape visualization widget with zoom and interaction support."""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPolygon, QWheelEvent


class TapeWidget(QWidget):
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
        self._scroll_offset = 0  # Manual scroll offset
        self.setMinimumHeight(140)
        self.setFont(QFont("Segoe UI Emoji", 24))
        self.setMouseTracking(True)
        self._hover_cell = -1

    def update_tape(self, tape, head, state, step_count=0, last_rule=None):
        self.tape = tape if tape else []
        self.head = head
        self.state = state
        self.step_count = step_count
        self.last_rule = last_rule
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
        """Scroll the tape with mouse wheel."""
        delta = event.angleDelta().y()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Wheel for zoom
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # Normal wheel for scrolling
            cells_to_scroll = delta // 120
            self._scroll_offset += cells_to_scroll
            self.update()

    def _get_newline_symbol(self):
        if hasattr(self.parent(), 'tm') and self.parent().tm:
            return self.parent().tm.em.get('NEWLINE', '')
        return ''

    def paintEvent(self, event):
        if not self.tape:
            self._paint_empty()
            return

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor("#1e1e1e"))

            w = self.width()
            num_cells = max(1, w // self.cell_width)
            start_idx = self.head - (num_cells // 2) + self._scroll_offset
            nl_sym = self._get_newline_symbol()

            top_margin = 28 if self.show_indices else 18

            # Draw last rule info bar
            rule_y = 2
            if self.last_rule:
                painter.setPen(QColor("#888888"))
                painter.setFont(QFont("Consolas", 9))
                rule_text = (f"Rule: [{self.last_rule['state']}, {self.last_rule['read']}] "
                             f"→ [{self.last_rule['write']}, {self.last_rule['move']}, "
                             f"{self.last_rule['next_state']}]")
                painter.drawText(280, rule_y + 12, rule_text)

            for cell_offset in range(num_cells):
                i = start_idx + cell_offset
                x = cell_offset * self.cell_width
                y = top_margin
                rect = QRect(x, y, self.cell_width, self.cell_height)

                is_newline = (0 <= i < len(self.tape) and self.tape[i] == nl_sym)
                is_head = (i == self.head)
                is_hover = (i == self._hover_cell)

                # Background colors
                if is_head:
                    bg_color = QColor("#4a3510" if is_newline else "#264f78")
                    border_color = QColor("#ffcc00" if is_newline else "#4fc1ff")
                    border_width = 2
                elif is_hover:
                    bg_color = QColor("#353535")
                    border_color = QColor("#666666")
                    border_width = 1
                else:
                    bg_color = QColor("#2a2520" if is_newline else "#252526")
                    border_color = QColor("#665500" if is_newline else "#444444")
                    border_width = 1

                painter.fillRect(rect, bg_color)
                painter.setPen(QPen(border_color, border_width))
                painter.drawRect(rect)

                # Cell indices
                if self.show_indices:
                    painter.setPen(QColor("#666666"))
                    painter.setFont(QFont("Consolas", 8))
                    painter.drawText(
                        QRect(x, y + self.cell_height, self.cell_width, 15),
                        Qt.AlignmentFlag.AlignCenter,
                        str(i)
                    )

                # Cell content
                if 0 <= i < len(self.tape):
                    current_sym = self.tape[i]
                    is_nl = (current_sym == "↵" or current_sym == nl_sym)
                    text_color = QColor("#ffcc00" if is_nl else "white")
                    font_size = max(12, min(24, self.cell_width // 3)) if is_nl else max(14, min(28, self.cell_width // 2))
                    painter.setPen(text_color)
                    painter.setFont(QFont("Consolas", font_size))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, current_sym)

            # Draw head triangle
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

            # State and step info
            painter.setPen(QColor("#00ff00"))
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            painter.drawText(10, rule_y + 12, f"State: {self.state}")

            painter.setPen(QColor("#aaaaaa"))
            painter.setFont(QFont("Consolas", 10))
            painter.drawText(150, rule_y + 12, f"Steps: {self.step_count}")

            # Zoom indicator
            painter.setPen(QColor("#555555"))
            painter.setFont(QFont("Consolas", 8))
            painter.drawText(w - 80, rule_y + 12, f"Zoom: {self.cell_width}px")

    def _paint_empty(self):
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
        w = self.width()
        num_cells = max(1, w // self.cell_width)
        start_idx = self.head - (num_cells // 2) + self._scroll_offset
        cell_at_mouse = start_idx + (event.position().x() // self.cell_width)
        if cell_at_mouse != self._hover_cell:
            self._hover_cell = cell_at_mouse
            self.update()

    def leaveEvent(self, event):
        self._hover_cell = -1
        self.update()