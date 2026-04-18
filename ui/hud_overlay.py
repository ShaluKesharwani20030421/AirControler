import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient


class HUDOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.cursor_pos   = QPoint(0, 0)
        self.buttons      = []
        self.hovered_button = None
        self.state_text   = "HOME MENU"
        self.info_text    = ""
        self.hand_detected   = False
        self.depth_mm        = 0.0
        self._flash_until    = 0.0   # epoch time until which we show click flash
        self._dwell_progress = 0.0   # 0..1 arc for dwell-click

        self.init_ui()

        # Repaint at ~60 fps for smooth flash animations
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(16)

    # ── Init ────────────────────────────────────────────────────────────
    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.show()

    # ── Public setters ───────────────────────────────────────────────────
    def set_cursor_position(self, x, y):
        self.cursor_pos = QPoint(int(x), int(y))

    def set_buttons(self, buttons):
        self.buttons = buttons

    def set_hovered_button(self, idx):
        self.hovered_button = idx

    def set_state_text(self, text):
        self.state_text = text

    def set_info_text(self, text):
        self.info_text = text

    def set_hand_status(self, detected: bool, depth_mm: float):
        self.hand_detected = detected
        self.depth_mm = depth_mm

    def set_dwell_progress(self, progress: float):
        """progress in [0..1]; shown as arc ring on hovered button."""
        self._dwell_progress = progress

    def flash_click(self):
        """Call this when an air-push is triggered for visual feedback."""
        self._flash_until = time.time() + 0.25  # 250 ms flash

    # ── Paint ────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        W = self.width()
        H = self.height()
        now = time.time()
        flashing = now < self._flash_until

        # ── 1. TOP STATUS BAR ─────────────────────────────────────────
        painter.setBrush(QBrush(QColor(0, 0, 0, 160)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, 520, 95, 12, 12)

        # Mode title
        painter.setPen(QPen(QColor(100, 220, 255, 255)))
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(20, 38, f"⬡  {self.state_text}")

        # Info line
        painter.setPen(QPen(QColor(200, 200, 200, 220)))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(20, 60, self.info_text)

        # Depth indicator
        if self.hand_detected:
            depth_cm = self.depth_mm / 10.0
            depth_color = QColor(0, 230, 100, 255)
            depth_label = f"Hand: {depth_cm:.1f} cm  ✓ DETECTED"
        else:
            depth_color = QColor(255, 80, 80, 255)
            depth_label = "Hand: NOT DETECTED — show hand to camera"
        painter.setPen(QPen(depth_color))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(20, 92, depth_label)

        # ── 2. DEPTH RANGE BAR (right side) ──────────────────────────
        bar_x, bar_y, bar_w, bar_h = W - 200, 10, 180, 20
        painter.setBrush(QBrush(QColor(40, 40, 40, 160)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)

        if self.hand_detected and self.depth_mm > 0:
            fill_ratio = min(1.0, max(0.0, (self.depth_mm - 150) / (1200 - 150)))
            fill_w = int(bar_w * fill_ratio)
            g = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            g.setColorAt(0.0, QColor(0, 200, 100))
            g.setColorAt(1.0, QColor(255, 120, 0))
            painter.setBrush(QBrush(g))
            painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 4, 4)

        painter.setPen(QPen(QColor(200, 200, 200, 180)))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(bar_x, bar_y + bar_h + 14, "15 cm ←  Distance  → 120 cm")

        # ── 3. BACK BUTTON (top-center, shown only in non-HOME modes) ─
        # Positioned at the same rect as MenuRenderer.get_back_button_rect()
        if self.state_text != "HOME MENU":
            bw_back, bh_back = 200, 70
            bx_back = W // 2 - bw_back // 2
            by_back = 15
            is_back_hovered = (
                bx_back <= self.cursor_pos.x() <= bx_back + bw_back and
                by_back <= self.cursor_pos.y() <= by_back + bh_back
            )
            if is_back_hovered:
                painter.setPen(QPen(QColor(255, 200, 0, 255), 3))
                painter.setBrush(QBrush(QColor(255, 200, 0, 160)))
            else:
                painter.setPen(QPen(QColor(255, 90, 90, 220), 3))
                painter.setBrush(QBrush(QColor(200, 40, 40, 130)))
            painter.drawRoundedRect(bx_back, by_back, bw_back, bh_back, 16, 16)
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
            painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            painter.drawText(
                QRect(bx_back, by_back, bw_back, bh_back),
                Qt.AlignmentFlag.AlignCenter, "↩  BACK  (hover 1.5s)")

        # ── 4. BUTTONS ────────────────────────────────────────────────
        for i, btn in enumerate(self.buttons):
            x, y, w, h = btn['rect']
            is_hovered = (i == self.hovered_button)

            if is_hovered:
                # Bright yellow hover
                painter.setPen(QPen(QColor(255, 230, 0, 255), 4))
                painter.setBrush(QBrush(QColor(255, 230, 0, 160)))
            else:
                painter.setPen(QPen(QColor(80, 180, 255, 220), 3))
                painter.setBrush(QBrush(QColor(30, 100, 200, 100)))

            painter.drawRoundedRect(x, y, w, h, 18, 18)

            # Button text
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
            painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            painter.drawText(QRect(x, y, w, h), Qt.AlignmentFlag.AlignCenter, btn['text'])

            # Dwell arc + hover hint
            if is_hovered and self._dwell_progress > 0:
                import math
                arc_rect = QRect(x + w // 2 - 28, y + h // 2 - 28, 56, 56)
                painter.setPen(QPen(QColor(255, 230, 0, 255), 5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                span = int(-self._dwell_progress * 360 * 16)
                painter.drawArc(arc_rect, 90 * 16, span)
            if is_hovered:
                painter.setPen(QPen(QColor(255, 255, 160, 220)))
                painter.setFont(QFont("Arial", 10))
                painter.drawText(QRect(x, y + h - 28, w, 24),
                                 Qt.AlignmentFlag.AlignCenter,
                                 "Air-Push or Hold 1.5s ▼")

        # ── 5. GHOST CURSOR ──────────────────────────────────────────
        cx, cy = self.cursor_pos.x(), self.cursor_pos.y()
        if flashing:
            # Red flash ring on click
            painter.setPen(QPen(QColor(255, 60, 60, 220), 4))
            painter.setBrush(QBrush(QColor(255, 60, 60, 80)))
            painter.drawEllipse(self.cursor_pos, 24, 24)
            painter.setPen(QPen(QColor(255, 255, 255, 255), 3))
            painter.setBrush(QBrush(QColor(255, 60, 60, 200)))
            painter.drawEllipse(self.cursor_pos, 10, 10)
        else:
            # Normal cursor: outer ring + inner dot
            color = QColor(0, 230, 100, 200) if self.hand_detected else QColor(150, 150, 150, 150)
            painter.setPen(QPen(color, 3))
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 60)))
            painter.drawEllipse(self.cursor_pos, 20, 20)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(self.cursor_pos, 6, 6)
            # Crosshair lines
            painter.setPen(QPen(color, 1))
            painter.drawLine(cx - 28, cy, cx - 22, cy)
            painter.drawLine(cx + 22, cy, cx + 28, cy)
            painter.drawLine(cx, cy - 28, cx, cy - 22)
            painter.drawLine(cx, cy + 22, cx, cy + 28)

        # ── 6. NO HAND OVERLAY ───────────────────────────────────────
        if not self.hand_detected:
            painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, W, H)
            painter.setPen(QPen(QColor(255, 100, 100, 255)))
            painter.setFont(QFont("Arial", 36, QFont.Weight.Bold))
            painter.drawText(
                QRect(0, H // 2 - 60, W, 60),
                Qt.AlignmentFlag.AlignCenter,
                "✋  Show Your Hand to the Camera"
            )
            painter.setPen(QPen(QColor(200, 200, 200, 200)))
            painter.setFont(QFont("Arial", 18))
            painter.drawText(
                QRect(0, H // 2 + 10, W, 40),
                Qt.AlignmentFlag.AlignCenter,
                "Hold your right hand 30–80 cm in front of the Orbbec camera"
            )

        # ── 7. CLICK FLASH BANNER ────────────────────────────────────
        if flashing:
            painter.setBrush(QBrush(QColor(255, 200, 0, 90)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, W, H)
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
            painter.setFont(QFont("Arial", 42, QFont.Weight.Bold))
            painter.drawText(
                QRect(0, H // 2 - 40, W, 80),
                Qt.AlignmentFlag.AlignCenter,
                "✓  CLICK!"
            )
