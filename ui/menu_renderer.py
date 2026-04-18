from utils.config import Config


class MenuRenderer:
    def __init__(self, screen_width, screen_height):
        self.screen_width  = screen_width
        self.screen_height = screen_height

    # ── Persistent BACK button (shown in all non-HOME modes) ───────────
    def get_back_button_rect(self):
        """Top-center of screen, well within reliable camera FOV (not a corner)."""
        W = self.screen_width
        bw, bh = 200, 70
        return (W // 2 - bw // 2, 15, bw, bh)   # centered, y=15

    # ── HOME mode ─────────────────────────────────────────────────────
    def get_home_menu_buttons(self):
        """
        6 buttons: 2×3 grid (Media, Mouse, Tab, Window, Keyboard, Exit).
        Safe zone: y 320–680 (never goes near top/bottom 20% where FOV is poor).
        Each button: 240×120 px with 30 px gap.
        """
        W, H = self.screen_width, self.screen_height
        bw, bh = 240, 120
        gap     = 30
        # grid top-left so the 2×3 block is centered
        gw = 2 * bw + gap
        gh = 3 * bh + 2 * gap
        x0 = W // 2 - gw // 2
        y0 = H // 2 - gh // 2

        return [
            {'id': 'media',    'text': '🎵  Media Control',
             'rect': (x0,          y0,              bw, bh)},
            {'id': 'mouse',    'text': '🖱️  Air Mouse',
             'rect': (x0 + bw + gap, y0,             bw, bh)},
            {'id': 'tab',      'text': '🔄  Tab Switcher',
             'rect': (x0,          y0 + bh + gap,    bw, bh)},
            {'id': 'window',   'text': '🪟  Window Switcher',
             'rect': (x0 + bw + gap, y0 + bh + gap,  bw, bh)},
            {'id': 'keyboard', 'text': '⌨️  Keyboard',
             'rect': (x0,          y0 + 2*(bh + gap), bw, bh)},
            {'id': 'exit',     'text': '❌  Exit',
             'rect': (x0 + bw + gap, y0 + 2*(bh + gap), bw, bh)},
        ]

    # ── MEDIA mode ────────────────────────────────────────────────────
    def get_media_menu_buttons(self):
        """3 gesture-hint labels centered vertically in the safe zone."""
        W, H = self.screen_width, self.screen_height
        bw, bh = 320, 100
        cx = W // 2 - bw // 2
        return [
            {'id': 'play_pause',   'text': '⏯  Open Palm → Play/Pause',
             'rect': (cx, H // 2 - 160, bw, bh)},
            {'id': 'volume_up',    'text': '🔊  Swipe UP → Volume Up',
             'rect': (cx, H // 2 - 40,  bw, bh)},
            {'id': 'volume_down',  'text': '🔉  Swipe DOWN → Volume Down',
             'rect': (cx, H // 2 + 80,  bw, bh)},
        ]

    # ── TAB mode ──────────────────────────────────────────────────────
    def get_tab_menu_buttons(self):
        """Tab switching gesture hints centered in safe zone."""
        W, H = self.screen_width, self.screen_height
        bw, bh = 340, 100
        cx = W // 2 - bw // 2
        return [
            {'id': 'next_tab',     'text': '➡️  Swipe RIGHT → Next Tab',
             'rect': (cx, H // 2 - 160, bw, bh)},
            {'id': 'prev_tab',     'text': '⬅️  Swipe LEFT → Previous Tab',
             'rect': (cx, H // 2 - 40,  bw, bh)},
            {'id': 'close_tab',    'text': '❌  Air-Push → Close Tab',
             'rect': (cx, H // 2 + 80,  bw, bh)},
        ]

    # ── WINDOW mode ───────────────────────────────────────────────────
    def get_window_menu_buttons(self):
        """Window switching gesture hints centered in safe zone."""
        W, H = self.screen_width, self.screen_height
        bw, bh = 360, 100
        cx = W // 2 - bw // 2
        return [
            {'id': 'next_window',  'text': '➡️  Swipe RIGHT → Next Window',
             'rect': (cx, H // 2 - 200, bw, bh)},
            {'id': 'prev_window',  'text': '⬅️  Swipe LEFT → Previous Window',
             'rect': (cx, H // 2 - 80,  bw, bh)},
            {'id': 'minimize',     'text': '⬇️  Air-Push → Minimize Window',
             'rect': (cx, H // 2 + 40,  bw, bh)},
            {'id': 'task_view',    'text': '👁️  Open Palm → Task View',
             'rect': (cx, H // 2 + 160, bw, bh)},
        ]

    # ── Helpers ───────────────────────────────────────────────────────
    def check_button_hover(self, buttons, x, y):
        for i, btn in enumerate(buttons):
            bx, by, bw, bh = btn['rect']
            if bx <= x <= bx + bw and by <= y <= by + bh:
                return i
        return None

    def get_button_at_position(self, buttons, x, y):
        for btn in buttons:
            bx, by, bw, bh = btn['rect']
            if bx <= x <= bx + bw and by <= y <= by + bh:
                return btn['id']
        return None
