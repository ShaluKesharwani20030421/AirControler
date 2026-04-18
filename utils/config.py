class Config:
    # Interaction zone: hand must be within this depth range (mm)
    # Wide range so natural hand positions always work
    INTERACTION_BOX_MIN = 150    # 15 cm minimum
    INTERACTION_BOX_MAX = 1200   # 120 cm maximum

    # Air-push: finger must move this many mm closer in TIME_WINDOW seconds
    AIR_CLICK_THRESHOLD = 50     # 5 cm push — eliminates false triggers from tremor
    AIR_CLICK_TIME_WINDOW = 0.35 # 350 ms window

    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080

    HUD_OPACITY = 0.8
    HUD_BUTTON_SIZE = 180        # Bigger buttons
    HUD_BUTTON_SPACING = 40

    DEPTH_MIN = 20
    DEPTH_MAX = 10000

    SMOOTHING_FACTOR = 0.6       # Less smoothing = more responsive

    BACK_BUTTON_ZONE_SIZE = 120  # Bigger back zone

    VOLUME_STEP = 2

    FPS_TARGET = 30
