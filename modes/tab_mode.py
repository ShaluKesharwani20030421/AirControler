import pyautogui
import time


class TabMode:
    """
    Tab Switching Mode — Navigate between browser tabs or application windows
    using horizontal swipe gestures.
    
    Gestures:
    - Swipe Left  → Previous tab (Ctrl+Shift+Tab)
    - Swipe Right → Next tab (Ctrl+Tab)
    - Air-Push    → Close current tab (Ctrl+W)
    """
    
    def __init__(self):
        self.last_action_time = 0
        self.action_cooldown = 0.4  # prevent rapid-fire tab switching
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
    
    def next_tab(self):
        """Switch to next tab (Ctrl+Tab)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('ctrl', 'tab')
            self.last_action_time = current_time
            print("Tab: Next (Ctrl+Tab)")
    
    def previous_tab(self):
        """Switch to previous tab (Ctrl+Shift+Tab)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            self.last_action_time = current_time
            print("Tab: Previous (Ctrl+Shift+Tab)")
    
    def close_tab(self):
        """Close current tab (Ctrl+W)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('ctrl', 'w')
            self.last_action_time = current_time
            print("Tab: Close (Ctrl+W)")
    
    def new_tab(self):
        """Open new tab (Ctrl+T)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('ctrl', 't')
            self.last_action_time = current_time
            print("Tab: New (Ctrl+T)")
    
    def reopen_tab(self):
        """Reopen last closed tab (Ctrl+Shift+T)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('ctrl', 'shift', 't')
            self.last_action_time = current_time
            print("Tab: Reopen (Ctrl+Shift+T)")
