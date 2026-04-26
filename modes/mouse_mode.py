import pyautogui
import time
try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False


class MouseMode:
    def __init__(self):
        self.last_click_time = 0
        self.click_cooldown = 0.5
        
        # Text input detection
        self.last_click_position = None
        self.text_input_apps = ['chrome', 'edge', 'firefox', 'notepad', 'word', 
                                'outlook', 'code', 'sublime', 'atom', 'slack']
        
        # Extra cursor smoothing for mouse control removed
        # (Handled by 1 Euro Filter in DepthLock now)
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
    
    def move_cursor(self, hand_data, screen_width, screen_height):
        if hand_data is None:
            return
        norm_x = hand_data['index_tip']['normalized_x']
        norm_y = hand_data['index_tip']['normalized_y']
        screen_x = max(0, min(int(norm_x * screen_width),  screen_width  - 1))
        screen_y = max(0, min(int(norm_y * screen_height), screen_height - 1))
        pyautogui.moveTo(screen_x, screen_y)

    def move_cursor_screen(self, screen_x, screen_y):
        """Move cursor (coordinates already smoothed by 1 Euro Filter)."""
        pyautogui.moveTo(int(screen_x), int(screen_y))
    
    def click(self):
        current_time = time.time()
        if current_time - self.last_click_time >= self.click_cooldown:
            # Record click position for text input detection
            self.last_click_position = pyautogui.position()
            pyautogui.click()
            self.last_click_time = current_time
            print("Mouse: Click")
    
    def right_click(self):
        current_time = time.time()
        if current_time - self.last_click_time >= self.click_cooldown:
            pyautogui.rightClick()
            self.last_click_time = current_time
            print("Mouse: Right Click")
    
    def double_click(self):
        current_time = time.time()
        if current_time - self.last_click_time >= self.click_cooldown:
            pyautogui.doubleClick()
            self.last_click_time = current_time
            print("Mouse: Double Click")
    
    def scroll_up(self):
        pyautogui.scroll(3)
        print("Mouse: Scroll Up")
    
    def scroll_down(self):
        pyautogui.scroll(-3)
        print("Mouse: Scroll Down")
    
    def is_text_input_likely(self):
        """
        Context-aware text input detection.
        Simplified to avoid heavy OS API calls (like pygetwindow) which cause lag.
        """
        return self._simple_text_detection()
    
    def _simple_text_detection(self):
        """Simple fallback: detect based on click patterns."""
        # If user just double-clicked, likely selecting text
        return False  # Conservative default
