"""
Premium HUD Overlay with Magical UI Effects
- Energy Orb cursor with glow/halo
- Ripple animations on air-push
- Circular dwell-to-click timer
- Semi-transparent glassmorphic design
"""

import time
import math
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, 
                         QLinearGradient, QRadialGradient, QPainterPath)


class RippleEffect:
    """Single ripple animation that expands and fades."""
    def __init__(self, x, y, max_radius=150, duration=0.8):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.duration = duration
        self.start_time = time.time()
    
    def is_alive(self):
        return (time.time() - self.start_time) < self.duration
    
    def get_progress(self):
        """Returns 0.0 to 1.0"""
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / self.duration)
    
    def draw(self, painter):
        progress = self.get_progress()
        radius = self.max_radius * progress
        opacity = int(255 * (1.0 - progress))  # Fade out
        
        # Outer ripple
        painter.setPen(QPen(QColor(100, 200, 255, opacity // 2), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(self.x, self.y), radius, radius)
        
        # Inner ripple (slightly delayed)
        if progress > 0.2:
            inner_radius = radius * 0.7
            painter.setPen(QPen(QColor(200, 230, 255, opacity), 2))
            painter.drawEllipse(QPointF(self.x, self.y), inner_radius, inner_radius)


class HUDOverlay(QWidget):
    """
    Premium glassmorphic HUD with magical cursor effects.
    
    Features:
    - Energy orb cursor with animated glow
    - Ripple animations on click
    - Circular dwell progress timer
    - Semi-transparent UI elements
    - Smooth animations at 60 FPS
    """
    
    def __init__(self):
        super().__init__()
        
        # State
        self.cursor_pos = QPoint(0, 0)
        self.buttons = []
        self.hovered_button = None
        self.state_text = "HOME MENU"
        self.info_text = ""
        self.hand_detected = False
        self.depth_mm = 0.0
        self._dwell_progress = 0.0
        
        # Animation state
        self._ripples = []  # List of active ripple effects
        self._orb_pulse = 0.0  # For pulsing energy orb
        self._flash_until = 0.0
        
        self.init_ui()
        
        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)  # ~60 FPS
    
    def init_ui(self):
        """Initialize transparent overlay window."""
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
    
    # ── Public API ────────────────────────────────────────────────────
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
        """Set dwell-to-click progress (0.0 to 1.0)."""
        self._dwell_progress = progress
    
    def flash_click(self):
        """Trigger ripple animation on air-push."""
        self._flash_until = time.time() + 0.25
        # Add ripple at cursor position
        self._ripples.append(RippleEffect(
            self.cursor_pos.x(),
            self.cursor_pos.y(),
            max_radius=180,
            duration=1.0
        ))
    
    # ── Animation Loop ────────────────────────────────────────────────
    def _animate(self):
        """Called every 16ms for smooth animations."""
        # Update orb pulse (sine wave)
        self._orb_pulse = (self._orb_pulse + 0.08) % (2 * math.pi)
        
        # Remove dead ripples
        self._ripples = [r for r in self._ripples if r.is_alive()]
        
        # Trigger repaint
        self.update()
    
    # ── Paint Event ───────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        W, H = self.width(), self.height()
        now = time.time()
        flashing = now < self._flash_until
        
        # Draw all UI elements
        self._draw_status_bar(painter, W, H)
        self._draw_depth_indicator(painter, W, H)
        self._draw_back_button(painter, W, H)
        self._draw_buttons(painter)
        self._draw_ripples(painter)
        self._draw_energy_orb_cursor(painter, flashing)
        
        if not self.hand_detected:
            self._draw_no_hand_overlay(painter, W, H)
        
        if flashing:
            self._draw_click_flash(painter, W, H)
    
    # ── UI Components ─────────────────────────────────────────────────
    def _draw_status_bar(self, painter, W, H):
        """Glassmorphic status bar at top."""
        # Semi-transparent background with blur effect
        painter.setBrush(QBrush(QColor(10, 10, 30, 140)))
        painter.setPen(QPen(QColor(100, 150, 255, 100), 2))
        painter.drawRoundedRect(10, 10, 540, 100, 16, 16)
        
        # Glow effect
        glow = QRadialGradient(280, 60, 200)
        glow.setColorAt(0.0, QColor(100, 200, 255, 30))
        glow.setColorAt(1.0, QColor(100, 200, 255, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, 540, 100, 16, 16)
        
        # Mode title with glow
        painter.setPen(QPen(QColor(150, 220, 255, 255)))
        painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        painter.drawText(25, 45, f"⬡  {self.state_text}")
        
        # Info text
        painter.setPen(QPen(QColor(220, 220, 240, 200)))
        painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(25, 70, self.info_text)
        
        # Hand status with icon
        if self.hand_detected:
            depth_cm = self.depth_mm / 10.0
            status_color = QColor(100, 255, 150, 255)
            status_text = f"✓ Hand Detected  •  {depth_cm:.1f} cm"
        else:
            status_color = QColor(255, 120, 120, 255)
            status_text = "⚠ No Hand Detected"
        
        painter.setPen(QPen(status_color))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(25, 95, status_text)
    
    def _draw_depth_indicator(self, painter, W, H):
        """Elegant depth range indicator."""
        bar_x, bar_y = W - 220, 20
        bar_w, bar_h = 200, 12
        
        # Background track
        painter.setBrush(QBrush(QColor(30, 30, 50, 120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 6, 6)
        
        # Fill based on depth
        if self.hand_detected and self.depth_mm > 0:
            fill_ratio = min(1.0, max(0.0, (self.depth_mm - 150) / (1200 - 150)))
            fill_w = int(bar_w * fill_ratio)
            
            # Gradient fill
            gradient = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            gradient.setColorAt(0.0, QColor(100, 255, 150))
            gradient.setColorAt(0.5, QColor(100, 200, 255))
            gradient.setColorAt(1.0, QColor(255, 150, 100))
            
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 6, 6)
        
        # Label
        painter.setPen(QPen(QColor(200, 200, 220, 160)))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(bar_x, bar_y + bar_h + 16, "15cm ← Distance → 120cm")
    
    def _draw_back_button(self, painter, W, H):
        """Glassmorphic back button (non-HOME modes only)."""
        if self.state_text == "HOME MENU":
            return
        
        bw, bh = 200, 70
        bx = W // 2 - bw // 2
        by = 15
        
        is_hovered = (
            bx <= self.cursor_pos.x() <= bx + bw and
            by <= self.cursor_pos.y() <= by + bh
        )
        
        # Glassmorphic background
        if is_hovered:
            painter.setBrush(QBrush(QColor(255, 200, 100, 140)))
            painter.setPen(QPen(QColor(255, 220, 120, 200), 3))
        else:
            painter.setBrush(QBrush(QColor(200, 60, 60, 110)))
            painter.setPen(QPen(QColor(255, 100, 100, 180), 2))
        
        painter.drawRoundedRect(bx, by, bw, bh, 20, 20)
        
        # Text
        painter.setPen(QPen(QColor(255, 255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        painter.drawText(QRect(bx, by, bw, bh), 
                        Qt.AlignmentFlag.AlignCenter, "↩  BACK")
    
    def _draw_buttons(self, painter):
        """Draw all UI buttons with glassmorphic style."""
        for i, btn in enumerate(self.buttons):
            x, y, w, h = btn['rect']
            is_hovered = (i == self.hovered_button)
            
            # Glassmorphic button
            if is_hovered:
                # Bright glow on hover
                glow = QRadialGradient(x + w/2, y + h/2, max(w, h) * 0.7)
                glow.setColorAt(0.0, QColor(255, 230, 100, 80))
                glow.setColorAt(1.0, QColor(255, 230, 100, 0))
                painter.setBrush(QBrush(glow))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(x - 10, y - 10, w + 20, h + 20, 25, 25)
                
                painter.setBrush(QBrush(QColor(255, 230, 100, 160)))
                painter.setPen(QPen(QColor(255, 240, 150, 220), 4))
            else:
                painter.setBrush(QBrush(QColor(40, 80, 160, 100)))
                painter.setPen(QPen(QColor(100, 180, 255, 180), 2))
            
            painter.drawRoundedRect(x, y, w, h, 22, 22)
            
            # Button text
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
            painter.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            painter.drawText(QRect(x, y, w, h), 
                            Qt.AlignmentFlag.AlignCenter, btn['text'])
            
            # Circular dwell progress timer
            if is_hovered and self._dwell_progress > 0:
                self._draw_circular_dwell_timer(painter, x + w/2, y + h/2)
    
    def _draw_circular_dwell_timer(self, painter, cx, cy):
        """
        Premium circular progress timer for dwell-to-click.
        Fills up clockwise from top over 1.5 seconds.
        """
        radius = 50
        thickness = 6
        
        # Background circle
        painter.setPen(QPen(QColor(100, 100, 120, 100), thickness))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Progress arc (clockwise from top)
        if self._dwell_progress > 0:
            # Gradient for progress
            gradient = QLinearGradient(cx - radius, cy, cx + radius, cy)
            gradient.setColorAt(0.0, QColor(100, 255, 200))
            gradient.setColorAt(1.0, QColor(255, 230, 100))
            
            painter.setPen(QPen(QBrush(gradient), thickness + 2, 
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            
            # Draw arc (starts at 90°, goes clockwise)
            start_angle = 90 * 16  # Qt uses 1/16th degree units
            span_angle = int(-self._dwell_progress * 360 * 16)
            
            rect = QRect(int(cx - radius), int(cy - radius), 
                        int(radius * 2), int(radius * 2))
            painter.drawArc(rect, start_angle, span_angle)
            
            # Center dot
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 8, 8)
            
            # Progress percentage
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            percent_text = f"{int(self._dwell_progress * 100)}%"
            painter.drawText(QRect(int(cx - 30), int(cy + radius + 15), 60, 20),
                            Qt.AlignmentFlag.AlignCenter, percent_text)
    
    def _draw_ripples(self, painter):
        """Draw all active ripple animations."""
        for ripple in self._ripples:
            ripple.draw(painter)
    
    def _draw_energy_orb_cursor(self, painter, flashing):
        """
        Premium energy orb cursor with animated glow/halo.
        Pulsates smoothly and changes color based on state.
        """
        cx, cy = self.cursor_pos.x(), self.cursor_pos.y()
        
        # Pulsing effect (0.8 to 1.2 scale)
        pulse_scale = 1.0 + 0.2 * math.sin(self._orb_pulse)
        
        if flashing:
            # Explosive flash on click
            flash_radius = 35 * pulse_scale
            
            # Outer glow
            glow = QRadialGradient(cx, cy, flash_radius * 2)
            glow.setColorAt(0.0, QColor(255, 100, 100, 150))
            glow.setColorAt(0.5, QColor(255, 150, 100, 80))
            glow.setColorAt(1.0, QColor(255, 200, 100, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), flash_radius * 2, flash_radius * 2)
            
            # Core orb
            painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
            painter.drawEllipse(QPointF(cx, cy), flash_radius * 0.4, flash_radius * 0.4)
        
        else:
            # Normal energy orb
            base_radius = 28 * pulse_scale
            
            # Color based on hand detection
            if self.hand_detected:
                core_color = QColor(100, 255, 200)
                glow_color = QColor(100, 255, 200)
            else:
                core_color = QColor(150, 150, 180)
                glow_color = QColor(150, 150, 180)
            
            # Outer halo (large glow)
            halo = QRadialGradient(cx, cy, base_radius * 3)
            halo.setColorAt(0.0, QColor(glow_color.red(), glow_color.green(), 
                                       glow_color.blue(), 60))
            halo.setColorAt(0.5, QColor(glow_color.red(), glow_color.green(), 
                                       glow_color.blue(), 20))
            halo.setColorAt(1.0, QColor(glow_color.red(), glow_color.green(), 
                                       glow_color.blue(), 0))
            painter.setBrush(QBrush(halo))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), base_radius * 3, base_radius * 3)
            
            # Middle glow ring
            mid_glow = QRadialGradient(cx, cy, base_radius * 1.5)
            mid_glow.setColorAt(0.0, QColor(glow_color.red(), glow_color.green(), 
                                           glow_color.blue(), 120))
            mid_glow.setColorAt(1.0, QColor(glow_color.red(), glow_color.green(), 
                                           glow_color.blue(), 0))
            painter.setBrush(QBrush(mid_glow))
            painter.drawEllipse(QPointF(cx, cy), base_radius * 1.5, base_radius * 1.5)
            
            # Core orb with gradient
            core_gradient = QRadialGradient(cx - base_radius * 0.3, 
                                           cy - base_radius * 0.3, 
                                           base_radius)
            core_gradient.setColorAt(0.0, QColor(255, 255, 255, 220))
            core_gradient.setColorAt(0.6, core_color)
            core_gradient.setColorAt(1.0, QColor(core_color.red() - 50, 
                                                 core_color.green() - 50, 
                                                 core_color.blue() - 50))
            painter.setBrush(QBrush(core_gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
            painter.drawEllipse(QPointF(cx, cy), base_radius * 0.6, base_radius * 0.6)
            
            # Sparkle effect (small white dot)
            sparkle_offset = base_radius * 0.4
            sparkle_x = cx - sparkle_offset * math.cos(self._orb_pulse)
            sparkle_y = cy - sparkle_offset * math.sin(self._orb_pulse)
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(sparkle_x, sparkle_y), 3, 3)
    
    def _draw_no_hand_overlay(self, painter, W, H):
        """Semi-transparent overlay when no hand detected."""
        painter.setBrush(QBrush(QColor(0, 0, 20, 140)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, W, H)
        
        # Animated icon
        icon_y = H // 2 - 80
        painter.setPen(QPen(QColor(255, 150, 150, 255)))
        painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        painter.drawText(QRect(0, icon_y, W, 80),
                        Qt.AlignmentFlag.AlignCenter, "✋")
        
        # Message
        painter.setPen(QPen(QColor(255, 200, 200, 255)))
        painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        painter.drawText(QRect(0, icon_y + 90, W, 50),
                        Qt.AlignmentFlag.AlignCenter,
                        "Show Your Hand to Camera")
        
        # Hint
        painter.setPen(QPen(QColor(220, 220, 240, 200)))
        painter.setFont(QFont("Segoe UI", 14))
        painter.drawText(QRect(0, icon_y + 150, W, 40),
                        Qt.AlignmentFlag.AlignCenter,
                        "Position your hand 30-80 cm from the Orbbec camera")
    
    def _draw_click_flash(self, painter, W, H):
        """Full-screen flash on click."""
        # Radial gradient flash
        flash_center = QPointF(self.cursor_pos.x(), self.cursor_pos.y())
        flash_gradient = QRadialGradient(flash_center, max(W, H))
        flash_gradient.setColorAt(0.0, QColor(255, 230, 100, 120))
        flash_gradient.setColorAt(0.3, QColor(255, 200, 100, 40))
        flash_gradient.setColorAt(1.0, QColor(255, 200, 100, 0))
        
        painter.setBrush(QBrush(flash_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, W, H)
        
        # "CLICK!" text
        painter.setPen(QPen(QColor(255, 255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        painter.drawText(QRect(0, H // 2 - 50, W, 100),
                        Qt.AlignmentFlag.AlignCenter, "✓  CLICK!")
