import pyautogui
from utils.config import Config

class MediaMode:
    def __init__(self):
        self.last_volume_change = 0
        
    def play_pause(self):
        pyautogui.press('playpause')
        print("Media: Play/Pause toggled")
    
    def volume_up(self):
        for _ in range(Config.VOLUME_STEP):
            pyautogui.press('volumeup')
        print(f"Media: Volume increased by {Config.VOLUME_STEP}")
    
    def volume_down(self):
        for _ in range(Config.VOLUME_STEP):
            pyautogui.press('volumedown')
        print(f"Media: Volume decreased by {Config.VOLUME_STEP}")
    
    def next_track(self):
        pyautogui.press('nexttrack')
        print("Media: Next track")
    
    def previous_track(self):
        pyautogui.press('prevtrack')
        print("Media: Previous track")
    
    def mute(self):
        pyautogui.press('volumemute')
        print("Media: Mute toggled")
