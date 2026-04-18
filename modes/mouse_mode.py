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
        
        # Extra cursor smoothing for mouse control
        self._smooth_x = 960.0
        self._smooth_y = 540.0
        self.MOUSE_SMOOTH = 0.3  # 0 = raw (fast), 1 = frozen. 0.3 = 1.5x faster than 0.5
        
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
        """Move cursor with extra EMA smoothing for comfortable control."""
        a = self.MOUSE_SMOOTH
        self._smooth_x = a * self._smooth_x + (1 - a) * screen_x
        self._smooth_y = a * self._smooth_y + (1 - a) * screen_y
        pyautogui.moveTo(int(self._smooth_x), int(self._smooth_y))
    
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
        Returns True if the last click was likely in a text input field.
        
        Heuristics:
        1. Active window is a text-heavy app (browser, editor, email)
        2. Click position suggests text area (not top menu bar)
        3. Simple fallback: always show keyboard on double-click
        """
        if not HAS_PYGETWINDOW:
            # Fallback: assume text input in common scenarios
            return self._simple_text_detection()
        
        try:
            active_window = gw.getActiveWindow()
            if active_window is None:
                return False
            
            window_title = active_window.title.lower()
            
            # Check if it's a text-heavy application
            is_text_app = any(app in window_title for app in self.text_input_apps)
            
            # Check click position (avoid top 100px = menu bar)
            if self.last_click_position:
                _, y = self.last_click_position
                is_content_area = y > 100
            else:
                is_content_area = True
            
            return is_text_app and is_content_area
            
        except Exception as e:
            print(f"[Mouse] Text detection error: {e}")
            return self._simple_text_detection()
    
    def _simple_text_detection(self):
        """Simple fallback: detect based on click patterns."""
        # If user just double-clicked, likely selecting text
        return False  # Conservative default
