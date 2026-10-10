<div align="center">

# AI Virtual Mouse 🖱️🤖

**Control your computer using real-time hand gestures — no physical mouse required.**

A Python computer-vision project using OpenCV, MediaPipe, NumPy, and PyAutoGUI.

</div>

---

## ✨ Features

- **Live hand tracking** through a webcam using MediaPipe.
- **Cursor movement** by moving the index fingertip inside the tracking rectangle.
- **Left click** using a thumb-and-index-finger pinch.
- **Right click** using an index-and-middle-finger pinch.
- **Scroll up/down** by pinching the thumb and middle finger, then moving the hand vertically.
- **Smoothed cursor movement** with adjustable responsiveness.
- **On-screen status and gesture-distance values** to help troubleshoot tracking.
- **PyAutoGUI failsafe** enabled for an emergency stop.

## 🖐️ Gesture Controls

| Action | Gesture | Instructions |
|---|---|---|
| Move cursor | Index fingertip movement | Keep your hand visible and move the index fingertip inside the rectangle shown in the camera window. |
| Left click | Thumb + index finger pinch | Bring the thumb and index fingertip together briefly. |
| Right click | Index + middle finger pinch | Bring the index and middle fingertips together briefly. |
| Scroll | Thumb + middle finger pinch | Keep the thumb and middle fingertip pinched and move your hand up or down. |
| Exit | Press `Q` | Click the camera window first if needed, then press `Q`. |

**Tip:** Keep your hand well-lit, fully visible, and within the rectangle. Avoid placing the hand too close to the camera.

## 🧰 Tech Stack

- **Python** — application logic
- **OpenCV** — webcam access and image processing
- **MediaPipe** — real-time hand landmark detection
- **NumPy** — coordinate mapping and distance calculations
- **PyAutoGUI** — operating-system cursor, click, and scroll control

## 💻 Requirements

- Windows 10/11 (the camera code tries the Windows DirectShow backend first)
- A working webcam
- Python compatible with the versions of MediaPipe and the other packages installed in your environment
- The packages listed in `requirements.txt`

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mira-Clouds/AI-Virtual-Mouse.git
cd AI-Virtual-Mouse
```

### 2. Create a virtual environment

In PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell does not allow activation, open Command Prompt and run:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the dependency installation fails, check that your Python version is supported by the MediaPipe version in your requirements file.

### 4. Run the application

```powershell
python hand_tracking.py
```

A webcam window named **AI Virtual Mouse** should open. Keep your hand inside the on-screen rectangle and use the gestures described above.

## ⚙️ Adjusting Cursor Movement

Open `hand_tracking.py` and look near the top for these settings:

| Setting | Purpose | Current value |
|---|---|---:|
| `SMOOTHING` | Higher values make the cursor respond faster; lower values make movement smoother but slower. | `0.60` |
| `MARGIN_X` | Horizontal margin of the camera tracking area. | `60` |
| `MARGIN_Y` | Vertical margin of the camera tracking area. | `45` |
| `LEFT_PINCH_ON` / `LEFT_PINCH_OFF` | Start/release thresholds for left-click detection. | `0.32` / `0.44` |
| `RIGHT_PINCH_ON` / `RIGHT_PINCH_OFF` | Start/release thresholds for right-click detection. | `0.32` / `0.44` |
| `SCROLL_PINCH_ON` / `SCROLL_PINCH_OFF` | Start/release thresholds for scroll mode. | `0.35` / `0.47` |
| `SCROLL_PIXELS_PER_STEP` | Lower values make scrolling more sensitive. | `16` |

### Cursor tuning

- If the cursor feels **slow**, increase `SMOOTHING` gradually, for example to `0.70`.
- If the cursor feels **jittery**, reduce `SMOOTHING`, for example to `0.40`.
- If the cursor cannot reach the edges of the screen, adjust `MARGIN_X` and `MARGIN_Y`.
- Change one setting at a time and test again.

The best values depend on your webcam, lighting, hand position, and screen resolution.

## 🛠️ Troubleshooting

### The camera does not open

- Close other applications that may be using the webcam.
- Check Windows camera permissions.
- Confirm that the webcam is connected and working.
- If you have multiple cameras, change `CAMERA_INDEX` in `hand_tracking.py` from `0` to `1` and try again.

### The hand is detected but the cursor does not move well

- Keep the index fingertip inside the tracking rectangle.
- Improve lighting and keep the hand fully visible.
- Adjust `SMOOTHING` and the tracking margins using the table above.
- Make sure the correct virtual environment is active before running the script.

### Gestures trigger incorrectly

- Keep the camera view clear and avoid overlapping fingertips.
- Adjust the pinch thresholds carefully in `hand_tracking.py`.
- The camera window displays `L`, `R`, and `S` distance values to help inspect the detected finger distances.

### Stop the application safely

- Press `Q` while the camera window is focused.
- PyAutoGUI's failsafe is enabled: moving the system cursor to the **top-left corner** triggers its emergency stop. Avoid disabling this safety feature.

## 🔒 Privacy and Safety

- The webcam is used locally for hand tracking while the application is running.
- Close the application when you finish.
- Test the controls carefully before using them around unsaved work or important system actions.
- Cursor movement and clicks are sent to your operating system, so keep your hand gestures controlled.

## 📁 Project Structure

```text
AI-Virtual-Mouse/
├── hand_tracking.py
├── requirements.txt
├── README.md
└── .venv/                 # Local virtual environment; do not commit to GitHub
```

Add other files or folders to this tree if they are present in your repository. Do not commit your local virtual environment or Python cache files.

## 🤝 Contributing

Suggestions, bug reports, and improvements are welcome. For significant changes, open an issue before submitting a pull request.

## 📜 License

No license is specified here. Add a `LICENSE` file and update this section if you decide to publish the project under a particular open-source license.

---

<div align="center">

Made with ❤️ using Python and Computer Vision

</div>
