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

    # ── Z-Based Dynamic Cursor Gain (C-D Gain) ────────────────────
    # Cursor speed adapts to hand distance from camera:
    #   Close (30cm) → precise, slow cursor for small targets
    #   Far (1.5m+)  → fast cursor, small wrist flick = full screen
    Z_GAIN_REF_DISTANCE = 500.0   # mm — "ideal" desk distance (50cm)
    Z_GAIN_POWER        = 0.6     # Sub-linear scaling exponent
    Z_GAIN_MIN           = 0.7    # Floor — never slower than 70%
    Z_GAIN_MAX           = 2.5    # Cap — never faster than 250%

    # ── Hand Identity Tracking ────────────────────────────────────
    # Max pixel jump between frames before rejecting as a different hand
    HAND_JUMP_THRESHOLD  = 200    # pixels — impossibly fast for same hand
