import pyautogui
import time


class WindowMode:
    """
    Window Switcher Mode — Navigate between open applications/windows
    using gestures (Chrome, Edge, Outlook, File Explorer, etc.).
    
    Gestures:
    - Swipe Right → Next window (Alt+Tab)
    - Swipe Left  → Previous window (Alt+Shift+Tab)
    - Air-Push    → Minimize current window (Win+Down)
    - Open Palm   → Show all windows (Win+Tab)
    """
    
    def __init__(self):
        self.last_action_time = 0
        self.action_cooldown = 0.5  # prevent rapid-fire window switching
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
    
    def next_window(self):
        """Switch to next window (Alt+Tab)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('alt', 'tab')
            self.last_action_time = current_time
            print("Window: Next (Alt+Tab)")
    
    def previous_window(self):
        """Switch to previous window (Alt+Shift+Tab)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('alt', 'shift', 'tab')
            self.last_action_time = current_time
            print("Window: Previous (Alt+Shift+Tab)")
    
    def minimize_window(self):
        """Minimize current window (Win+Down)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('win', 'down')
            self.last_action_time = current_time
            print("Window: Minimize (Win+Down)")
    
    def show_task_view(self):
        """Show Windows Task View (Win+Tab)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('win', 'tab')
            self.last_action_time = current_time
            print("Window: Task View (Win+Tab)")
    
    def maximize_window(self):
        """Maximize current window (Win+Up)."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_cooldown:
            pyautogui.hotkey('win', 'up')
            self.last_action_time = current_time
            print("Window: Maximize (Win+Up)")
