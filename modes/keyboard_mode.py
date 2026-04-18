import pyautogui

class KeyboardMode:
    def __init__(self):
        self.keyboard_layout = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['SPACE', 'BACKSPACE', 'ENTER']
        ]
        
        self.current_row = 0
        self.current_col = 0
    
    def get_keyboard_buttons(self, screen_width, screen_height):
        """
        Keyboard centered vertically in y=280..680 — the safe FOV zone for
        the Gemini 335.  Keys are 90×70 px so they are easy to hover over.
        """
        buttons    = []
        key_w      = 90
        key_h      = 70
        gap        = 10
        start_y    = screen_height // 2 - 200   # ~340 on 1080p

        for row_idx, row in enumerate(self.keyboard_layout):
            stride    = key_w + gap
            if row_idx == 3:                      # bottom row: wider special keys
                specs = [('SPACE', key_w * 4 + gap * 3),
                         ('BACKSPACE', key_w * 2 + gap),
                         ('ENTER', key_w * 2 + gap)]
                row_width = sum(w for _, w in specs) + gap * (len(specs) - 1)
                x = (screen_width - row_width) // 2
                y = start_y + row_idx * (key_h + gap)
                for kid, kw in specs:
                    buttons.append({'id': kid, 'text': kid,
                                    'rect': (x, y, kw, key_h)})
                    x += kw + gap
            else:
                row_width = len(row) * stride - gap
                x = (screen_width - row_width) // 2
                y = start_y + row_idx * (key_h + gap)
                for key in row:
                    buttons.append({'id': key, 'text': key,
                                    'rect': (x, y, key_w, key_h)})
                    x += stride

        return buttons
    
    def type_key(self, key):
        if key == 'SPACE':
            pyautogui.press('space')
            print("Keyboard: Space")
        elif key == 'BACKSPACE':
            pyautogui.press('backspace')
            print("Keyboard: Backspace")
        elif key == 'ENTER':
            pyautogui.press('enter')
            print("Keyboard: Enter")
        else:
            pyautogui.press(key.lower())
            print(f"Keyboard: {key}")
    
    def type_text(self, text):
        pyautogui.write(text, interval=0.05)
        print(f"Keyboard: Typed '{text}'")
