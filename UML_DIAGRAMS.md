# Aether-Link UML Diagrams (Mermaid)

This file contains all major UML diagrams for the Aether-Link project, written in Mermaid syntax.

---

## 1. Class Diagram

This diagram shows the main classes and their relationships, giving a complete overview of the system architecture.

```mermaid
classDiagram
    class AetherLink {
        +run()
        -app
        -pipeline
        -depth_lock
        -gesture_detector
        -state_machine
        -hud
        -menu_renderer
        -media_mode
        -mouse_mode
        -tab_mode
        -window_mode
        -keyboard_mode
        -sig_verifier
        -handle_home_mode()
        -handle_media_mode()
        -handle_mouse_mode()
        -handle_tab_mode()
        -handle_window_mode()
        -handle_keyboard_overlay()
        -update_hud()
    }

    class DepthLock {
        +process_frames()
        +get_hand_data()
        -ema_depth
        -ema_norm_x
        -ema_norm_y
    }

    class GestureDetector {
        +detect_air_push()
        +detect_pinch()
        +detect_peace_sign()
        +detect_open_palm()
        +detect_swipe_up()
        +detect_swipe_down()
        +detect_swipe_left()
        +detect_swipe_right()
    }

    class StateMachine {
        +current_state
        +go_to_home()
        +go_to_mouse()
        +toggle_keyboard_overlay()
        +has_keyboard_overlay
    }

    class HUDOverlay {
        +set_state_text()
        +set_info_text()
        +set_buttons()
        +set_cursor_position()
        +flash_click()
    }

    class MenuRenderer {
        +get_home_menu_buttons()
        +get_media_menu_buttons()
        +get_tab_menu_buttons()
        +get_window_menu_buttons()
        +check_button_hover()
    }

    class SignatureVerifier {
        +verify()
        -reference_signature
        -dtw_threshold
    }
    
    class ModeBase {
        <<Abstract>>
    }
    class MediaMode
    class MouseMode
    class TabMode
    class WindowMode
    class KeyboardMode

    AetherLink o-- DepthLock : uses
    AetherLink o-- GestureDetector : uses
    AetherLink o-- StateMachine : uses
    AetherLink o-- HUDOverlay : uses
    AetherLink o-- MenuRenderer : uses
    AetherLink o-- SignatureVerifier : uses
    
    AetherLink o-- MediaMode : uses
    AetherLink o-- MouseMode : uses
    AetherLink o-- TabMode : uses
    AetherLink o-- WindowMode : uses
    AetherLink o-- KeyboardMode : uses

    ModeBase <|-- MediaMode
    ModeBase <|-- MouseMode
    ModeBase <|-- TabMode
    ModeBase <|-- WindowMode
    ModeBase <|-- KeyboardMode

    HUDOverlay ..> MenuRenderer : uses
    AetherLink ..> DepthLock : gets hand data
    AetherLink ..> GestureDetector : detects gestures
```

---

## 2. Use Case Diagram

This diagram shows the actions (use cases) available to the end-user.

```mermaid
flowchart TD
    subgraph Aether-Link System
        uc1(Control Mouse Cursor)
        uc2(Perform Left Click)
        uc3(Switch Modes)
        uc4(Control Media Playback)
        uc5(Manage Browser Tabs)
        uc6(Manage App Windows)
        uc7(Toggle Virtual Keyboard)
        uc8(Type on Keyboard)
        uc9(Take Screenshot)
        uc10(Unlock System via Signature)
    end

    User --> uc1
    User --> uc2
    User --> uc3
    User --> uc4
    User --> uc5
    User --> uc6
    User --> uc7
    User --> uc8
    User --> uc9
    User --> uc10

    uc7 -.-> uc8 : <<includes>>
    uc3 -.-> uc1 : <<extends>>
    uc3 -.-> uc4 : <<extends>>
    uc3 -.-> uc5 : <<extends>>
    uc3 -.-> uc6 : <<extends>>
```

---

## 3. Sequence Diagram: Toggling the Keyboard

This diagram shows the sequence of interactions between objects when the user performs a **Pinch gesture** to toggle the keyboard.

```mermaid
sequenceDiagram
    actor User
    participant AetherLink
    participant GestureDetector
    participant StateMachine
    participant HUDOverlay

    User->>AetherLink: Performs Pinch Gesture
    activate AetherLink

    AetherLink->>GestureDetector: detect_pinch(hand_data)
    activate GestureDetector
    GestureDetector-->>AetherLink: returns true
    deactivate GestureDetector

    AetherLink->>StateMachine: toggle_keyboard_overlay()
    activate StateMachine
    StateMachine->>StateMachine: keyboard_overlay = not keyboard_overlay
    StateMachine-->>AetherLink: 
    deactivate StateMachine

    AetherLink->>HUDOverlay: update_hud()
    activate HUDOverlay
    alt Keyboard is now ON
        HUDOverlay->>AetherLink: Renders keyboard buttons
    else Keyboard is now OFF
        HUDOverlay->>AetherLink: Renders mode buttons
    end
    deactivate HUDOverlay

    AetherLink-->>User: Display is updated
    deactivate AetherLink
```

---

## 4. Activity Diagram: Main Application Loop

This diagram shows the flow of activities from starting the app to handling user input in different states.

```mermaid
flowchart TD
    A[Start] --> B{Initialize Hardware & UI};
    B --> C{System Locked?};
    C -- Yes --> D[Handle Lock Mode];
    D --> E{Unlock Successful?};
    E -- No --> D;
    C -- No --> F;
    E -- Yes --> F[Enter HOME Mode];
    
    F --> G[Process Camera Frames & Detect Hand];
    G --> H{Hand Detected?};
    H -- No --> G;
    H -- Yes --> I[Detect Gestures (Push, Pinch, Swipe)];
    
    I --> J{Current State?};
    J -- HOME --> K[Handle Home Mode Logic];
    J -- MOUSE --> L[Handle Mouse Mode Logic];
    J -- MEDIA --> M[Handle Media Mode Logic];
    J -- TAB --> N[Handle Tab Mode Logic];
    J -- WINDOW --> O[Handle Window Mode Logic];
    
    subgraph Mode Handlers
        K; L; M; N; O;
    end
    
    K --> P[Update HUD];
    L --> P;
    M --> P;
    N --> P;
    O --> P;
    
    P --> Q{Keyboard Overlay Active?};
    Q -- Yes --> R[Handle Keyboard Input];
    R --> S[Update HUD with Keyboard];
    S --> G
    Q -- No --> G;
```

---

## 5. Component Diagram

This diagram shows the high-level components and their dependencies.

```mermaid
flowchart TD
    subgraph User Interface
        C[ui.hud_overlay_premium]
        D[ui.menu_renderer]
    end

    subgraph Core Logic
        E[main.AetherLink]
        F[core.state_machine]
        G[core.gesture_detector]
    end

    subgraph Hardware Abstraction
        H[core.depth_lock]
        I[pyorbbecsdk]
    end
    
    subgraph Modes
        J[modes.mouse_mode]
        K[modes.media_mode]
        L[modes.tab_mode]
        M[modes.window_mode]
    end

    subgraph Security
        N[security.signature_verifier]
        O[security.signature_recorder]
    end

    E --> F; E --> G; E --> H; E --> C; E --> D;
    E --> J; E --> K; E --> L; E --> M;
    E --> N; E --> O;
    
    G --> H; 
    H --> I;
    C --> D;
```
