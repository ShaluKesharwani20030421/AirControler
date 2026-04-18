# Aether-Link Technical Documentation

## Architecture Overview

Aether-Link is built on a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                      (main.py)                          │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│     Core     │  │      UI      │  │    Modes     │
│   Modules    │  │  Components  │  │  Controllers │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Core Components

### 1. Depth-Lock System (`core/depth_lock.py`)

**Purpose**: Maps 2D MediaPipe hand landmarks to 3D depth coordinates.

**Key Algorithm**:
```
For each frame:
  1. Get IR frame from Orbbec camera
  2. Process with MediaPipe to get (x, y) coordinates
  3. Look up depth value at (x, y) in depth map
  4. Return 3D coordinate (x, y, z) where z = depth in mm
```

**Implementation Details**:
- Uses MediaPipe Hands with single hand tracking
- Smoothing factor: 0.7 (exponential moving average)
- Tracks index finger tip, thumb tip, and wrist
- Returns normalized coordinates for screen mapping

**Key Methods**:
```python
process_frame(ir_frame, depth_data) -> hand_data
is_in_interaction_box(hand_data) -> bool
draw_hand_landmarks(frame, hand_data) -> frame
```

### 2. Gesture Detection (`core/gesture_detector.py`)

**Purpose**: Detect meaningful gestures from hand movement data.

#### Air-Push Detection

**Algorithm**:
```
Maintain depth_history queue (200ms window)
For each frame:
  1. Add current depth to history
  2. Remove entries older than 200ms
  3. Calculate: depth_change = oldest_z - newest_z
  4. If depth_change >= 50mm AND time_diff <= 200ms:
     → Trigger air-push event
  5. Clear history and set cooldown (300ms)
```

**Mathematical Model**:
```
ΔZ = Z(t₀) - Z(t₁)
Δt = t₁ - t₀

Air-Push Detected ⟺ (ΔZ ≥ 50mm) ∧ (Δt ≤ 0.2s)
```

#### Swipe Detection

**Vertical Swipe**:
```python
swipe_up: Δy < -30 pixels
swipe_down: Δy > 30 pixels
```

#### Open Palm Detection

**Algorithm**:
```
For each finger (index, middle, ring, pinky):
  If finger_tip.y < finger_pip.y:
    extended_count++

Open Palm ⟺ extended_count >= 3
```

### 3. State Machine (`core/state_machine.py`)

**States**:
- `HOME (0)`: Main menu with 4 options
- `MEDIA (1)`: Media control mode
- `MOUSE (2)`: Air mouse mode
- `KEYBOARD (3)`: Virtual keyboard mode

**State Transitions**:
```
HOME ──[select media]──> MEDIA
     ──[select mouse]──> MOUSE
     ──[select keyboard]──> KEYBOARD

ANY_STATE ──[back zone air-push]──> HOME
```

## UI System

### 1. HUD Overlay (`ui/hud_overlay.py`)

**Technology**: PyQt6 with transparent window

**Features**:
- Always-on-top transparent overlay
- Ghost cursor (follows hand position)
- Button highlighting on hover
- State indicator
- Back zone visualization

**Rendering Pipeline**:
```
QPainter.begin()
  1. Draw ghost cursor (green circle)
  2. Draw buttons (with hover effects)
  3. Draw state text
  4. Draw info text
  5. Draw back zone indicator
QPainter.end()
```

**Transparency Settings**:
```python
WindowFlags: FramelessWindowHint | WindowStaysOnTopHint
Attributes: WA_TranslucentBackground | WA_TransparentForMouseEvents
```

### 2. Menu Renderer (`ui/menu_renderer.py`)

**Coordinate System**:
```
Screen Space: (0, 0) to (SCREEN_WIDTH, SCREEN_HEIGHT)
Hand Space: (0.0, 0.0) to (1.0, 1.0) normalized

Mapping: screen_x = hand_normalized_x × SCREEN_WIDTH
         screen_y = hand_normalized_y × SCREEN_HEIGHT
```

**Button Layout Algorithm**:
```python
# Home Menu (2x2 grid)
center_x = SCREEN_WIDTH / 2
center_y = SCREEN_HEIGHT / 2

button_positions = [
  (center_x - size - spacing, center_y - size - spacing),  # Top-left
  (center_x + spacing, center_y - size - spacing),         # Top-right
  (center_x - size - spacing, center_y + spacing),         # Bottom-left
  (center_x + spacing, center_y + spacing)                 # Bottom-right
]
```

## Control Modes

### 1. Media Mode (`modes/media_mode.py`)

**Gesture Mapping**:
- Swipe Up → Volume Up (2 steps)
- Swipe Down → Volume Down (2 steps)
- Open Palm → Play/Pause
- (Future) Swipe Left → Previous Track
- (Future) Swipe Right → Next Track

**Implementation**:
```python
pyautogui.press('volumeup')  # Windows media key
pyautogui.press('playpause')  # Windows media key
```

### 2. Mouse Mode (`modes/mouse_mode.py`)

**Coordinate Mapping**:
```
Hand Position (normalized) → Screen Position (pixels)

screen_x = clamp(hand_x × SCREEN_WIDTH, 0, SCREEN_WIDTH-1)
screen_y = clamp(hand_y × SCREEN_HEIGHT, 0, SCREEN_HEIGHT-1)
```

**Click Cooldown**: 500ms to prevent accidental double-clicks

**PyAutoGUI Settings**:
```python
FAILSAFE = False  # Allow cursor to reach screen edges
PAUSE = 0.01      # Minimal delay for smooth movement
```

### 3. Keyboard Mode (`modes/keyboard_mode.py`)

**Layout**:
```
Row 0: Q W E R T Y U I O P
Row 1: A S D F G H J K L
Row 2: Z X C V B N M
Row 3: SPACE BACKSPACE ENTER
```

**Button Dimensions**:
- Standard key: 60×60 pixels
- Space: 180×60 pixels (3× width)
- Backspace/Enter: 120×60 pixels (2× width)

## Camera Integration

### Orbbec Gemini 335 Configuration

**Streams Used**:
1. **Depth Stream**: Y16 format, default resolution
2. **IR Left Stream**: Y8/Y16 format, default resolution

**Frame Synchronization**:
```python
pipeline.enable_frame_sync()  # Align depth and IR frames
```

**Processing Pipeline**:
```
Orbbec Camera
    ↓
Pipeline.wait_for_frames(100ms timeout)
    ↓
Extract: depth_frame, ir_frame
    ↓
Process: depth_colormap, depth_data (mm)
         ir_image (grayscale → BGR)
    ↓
MediaPipe + Depth Lookup
    ↓
Hand Data (x, y, z)
```

### Depth Processing

**Conversion**:
```python
raw_depth (uint16) × depth_scale = depth_mm (float32)
```

**Normalization for Visualization**:
```python
normalized = (depth_mm - MIN_DEPTH) / (MAX_DEPTH - MIN_DEPTH) × 255
colormap = cv2.applyColorMap(normalized, COLORMAP_JET)
```

## Configuration System

### `utils/config.py`

**Critical Parameters**:

| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| INTERACTION_BOX_MIN | 300 | mm | Minimum hand distance |
| INTERACTION_BOX_MAX | 600 | mm | Maximum hand distance |
| AIR_CLICK_THRESHOLD | 50 | mm | Depth change for click |
| AIR_CLICK_TIME_WINDOW | 0.2 | s | Time window for click |
| SMOOTHING_FACTOR | 0.7 | - | EMA smoothing (0-1) |
| BACK_BUTTON_ZONE_SIZE | 100 | px | Back zone size |

**Smoothing Formula**:
```
smoothed_value = α × prev_value + (1-α) × current_value
where α = SMOOTHING_FACTOR = 0.7
```

## Performance Considerations

### Frame Rate

**Target**: 30 FPS
**Actual**: Depends on:
- Camera frame rate
- MediaPipe processing time (~10-20ms)
- Depth processing time (~5-10ms)
- UI rendering time (~5ms)

**Optimization Strategies**:
1. Single hand tracking (not multi-hand)
2. Reduced MediaPipe confidence thresholds
3. Minimal UI redraws (only on state change)
4. Efficient depth lookup (direct array indexing)

### Memory Usage

**Typical**:
- Depth frame: 640×480×2 bytes = ~600KB
- IR frame: 640×480×1 byte = ~300KB
- MediaPipe model: ~10MB
- Total: ~50-100MB

## Error Handling

### Camera Errors

```python
try:
    frames = pipeline.wait_for_frames(100)
    if frames is None:
        return  # Skip frame
except Exception as e:
    print(f"Frame error: {e}")
    # Continue to next frame
```

### Gesture Detection Errors

```python
if hand_data is None:
    depth_history.clear()  # Reset state
    return False
```

### State Machine Safety

```python
# Always allow return to HOME
if back_zone_click:
    state_machine.go_to_home()
```

## Extension Points

### Adding New Gestures

1. **Define Detection Logic** (`core/gesture_detector.py`):
```python
def detect_pinch(self, hand_data):
    thumb = hand_data['thumb_tip']
    index = hand_data['index_tip']
    distance = sqrt((thumb['x']-index['x'])**2 + (thumb['y']-index['y'])**2)
    return distance < PINCH_THRESHOLD
```

2. **Handle in Main Loop** (`main.py`):
```python
if self.gesture_detector.detect_pinch(self.current_hand_data):
    self.handle_pinch_gesture()
```

### Adding New Modes

1. **Create Mode Class** (`modes/new_mode.py`):
```python
class NewMode:
    def __init__(self):
        pass
    
    def handle_action(self):
        pass
```

2. **Add State** (`core/state_machine.py`):
```python
class AppState(Enum):
    NEW_MODE = 4
```

3. **Integrate** (`main.py`):
```python
elif self.state_machine.is_new_mode():
    self.handle_new_mode()
```

## Testing Recommendations

### Unit Tests
- Gesture detection with synthetic hand data
- State machine transitions
- Coordinate mapping accuracy

### Integration Tests
- Camera initialization
- Frame processing pipeline
- UI rendering

### User Testing
- Gesture recognition accuracy
- Response time
- User comfort and fatigue

## Known Limitations

1. **Single Hand**: Only tracks one hand at a time
2. **Lighting**: Requires adequate IR illumination
3. **Distance**: Limited to 30-60cm range
4. **Occlusion**: Cannot handle hand occlusion
5. **Speed**: Fast movements may lose tracking

## Future Enhancements

1. **Two-Hand Gestures**: Pinch-to-zoom, rotate
2. **Custom Gesture Training**: User-defined gestures
3. **Voice Commands**: Hybrid voice + gesture control
4. **Haptic Feedback**: Visual/audio feedback for actions
5. **Gesture Recording**: Macro recording and playback
6. **Multi-Monitor Support**: Extended desktop control
