from enum import Enum


class AppState(Enum):
    """
    Primary application states - user-selected modes.
    KEYBOARD removed as primary state; now context-aware overlay.
    LOCKED state for biometric authentication.
    """
    LOCKED = 0   # Biometric authentication required
    HOME = 1
    MEDIA = 2
    MOUSE = 3
    TAB = 4
    WINDOW = 5


class StateMachine:
    """
    Human-centric state machine with overlay support.
    
    Architecture:
    - Primary State: The main mode (HOME, MEDIA, MOUSE, TAB, WINDOW)
    - Keyboard Overlay: Context-aware, appears automatically when needed
    
    The keyboard is no longer a standalone mode - it's a tool that
    appears contextually (e.g., when user clicks a text input in Mouse mode).
    """
    
    def __init__(self, require_auth=False):
        # Security: Start in LOCKED state if authentication required
        self.current_state = AppState.LOCKED if require_auth else AppState.HOME
        self.previous_state = None
        self.authentication_required = require_auth
        
        # Overlay system - keyboard can appear over any primary state
        self.keyboard_overlay_active = False
        self.overlay_trigger_reason = None  # 'text_input_click', 'manual', etc.
        
    # ── State Management ──────────────────────────────────────────────
    def get_state(self):
        return self.current_state
    
    def set_state(self, new_state):
        if isinstance(new_state, AppState):
            self.previous_state = self.current_state
            self.current_state = new_state
            # When changing primary state, dismiss keyboard overlay
            self.dismiss_keyboard_overlay()
            print(f"State changed: {self.previous_state} -> {self.current_state}")
    
    # ── Primary State Transitions ─────────────────────────────────────
    def go_to_home(self):
        self.set_state(AppState.HOME)
    
    def go_to_media(self):
        self.set_state(AppState.MEDIA)
    
    def go_to_mouse(self):
        self.set_state(AppState.MOUSE)
    
    def go_to_tab(self):
        self.set_state(AppState.TAB)
    
    def go_to_window(self):
        self.set_state(AppState.WINDOW)
    
    # ── Overlay Management ────────────────────────────────────────────
    def show_keyboard_overlay(self, reason='manual'):
        """
        Activate keyboard overlay over current primary state.
        Reason can be: 'text_input_click', 'manual', 'hover_text_field'
        """
        if not self.keyboard_overlay_active:
            self.keyboard_overlay_active = True
            self.overlay_trigger_reason = reason
            print(f"[Overlay] Keyboard activated ({reason}) over {self.current_state.name}")
    
    def dismiss_keyboard_overlay(self):
        """Deactivate keyboard overlay, return to primary state."""
        if self.keyboard_overlay_active:
            self.keyboard_overlay_active = False
            print(f"[Overlay] Keyboard dismissed, returning to {self.current_state.name}")
            self.overlay_trigger_reason = None
    
    def toggle_keyboard_overlay(self):
        """Toggle keyboard overlay on/off."""
        if self.keyboard_overlay_active:
            self.dismiss_keyboard_overlay()
        else:
            self.show_keyboard_overlay('manual')
    
    # ── State Queries ─────────────────────────────────────────────────
    def is_home(self):
        return self.current_state == AppState.HOME
    
    def is_media(self):
        return self.current_state == AppState.MEDIA
    
    def is_mouse(self):
        return self.current_state == AppState.MOUSE
    
    def is_tab(self):
        return self.current_state == AppState.TAB
    
    def is_window(self):
        return self.current_state == AppState.WINDOW
    
    def is_locked(self):
        """Check if system is in LOCKED state (authentication required)."""
        return self.current_state == AppState.LOCKED
    
    def unlock(self):
        """Unlock system after successful biometric authentication."""
        if self.current_state == AppState.LOCKED:
            self.set_state(AppState.HOME)
            print("[Security] System unlocked - biometric verified")
    
    def lock(self):
        """Lock system (require re-authentication)."""
        self.set_state(AppState.LOCKED)
        print("[Security] System locked")
    
    def has_keyboard_overlay(self):
        """Check if keyboard overlay is currently active."""
        return self.keyboard_overlay_active
    
    def get_state_name(self):
        """Get display name including overlay status."""
        base = self.current_state.name
        if self.keyboard_overlay_active:
            return f"{base} + KEYBOARD"
        return base
    
    def get_effective_mode(self):
        """
        Returns what the user is actually interacting with.
        If keyboard overlay is active, keyboard takes priority for input.
        """
        if self.keyboard_overlay_active:
            return 'KEYBOARD_OVERLAY'
        return self.current_state.name
