# Point, Look, and Name — Reachy Mini

The user points at an object in front of a webcam. Reachy Mini (full MuJoCo simulation) turns its head towards that object, displays its name and says it out loud. When the pointing direction is unclear, the system says so instead of guessing.

## How it works

1. **Pointing gesture** — MediaPipe Hand Landmarker finds 21 hand landmarks. A hand counts as pointing when the index finger is extended and the middle, ring and little fingers are curled (fingertip vs. middle-joint distance to the wrist).
2. **Object detection** — Ultralytics YOLO11n (COCO classes) detects objects; low-confidence boxes and the `person` class are ignored.
3. **Target selection (rule-based)** — the pointing ray runs from the index knuckle through the fingertip. For each object, the angle between this ray and the line from the fingertip to the object's box centre is computed. The smallest angle wins if it is within a maximum angle and clearly better than the runner-up. Otherwise the result is *no target* or *ambiguous*.
4. **Stability** — the robot only acts once the same target has been selected for several consecutive frames and differs from the last one it named.
5. **Robot** — the target's position in the image is mapped linearly to head yaw/pitch. Reachy turns its head, then says the object's name.

## Requirements

- Windows (tested), Python **3.12**
- A webcam
- Packages listed in `requirements.txt` (Reachy Mini SDK with MuJoCo, MediaPipe, Ultralytics, OpenCV, pyttsx3)

## Setup

Run in PowerShell from the project folder:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If activation is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` first.

Download the MediaPipe hand model into `models/`:

```powershell
mkdir models
curl.exe -L -o models/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

The YOLO weights (`yolo11n.pt`) download automatically on the first run.

## Running

**Terminal 1** — start the full MuJoCo simulation (venv activated):

```powershell
reachy-mini-daemon --sim --no-media --no-wake-up-on-start
```

Wait until the MuJoCo window with the robot is open.

**Terminal 2** — start the application (venv activated):

```powershell
python main.py
```

Place at least two everyday objects (e.g. cup, bottle, phone, book) in view of the webcam and point at one of them. Press **q** in the camera window to quit. The head will return to the centre.

### Why not the Reachy Mini Control app?

Control's *Simulation* button starts the mockup simulator (no MuJoCo physics), and its media pipeline takes over the laptop webcam. Starting the daemon with `--sim --no-media` gives the full MuJoCo simulation while leaving the webcam free for OpenCV. The script then connects with `ReachyMini(media_backend="no_media")`. Control can still be opened afterwards and connected to this daemon if wanted; however, it would not have access to the webcam. 

## Camera preview

| Element | Meaning |
| --- | --- |
| Green dots | Hand landmarks |
| Red line | Pointing ray |
| Blue boxes | Detected objects with confidence |
| Thick green box + "Target: …" | Selected object |
| "Unclear – point more precisely" | Two objects are similarly aligned; no guess is made |
| "No target" | No object close enough to the pointing direction |

The preview is mirrored so it feels natural to the user.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Main loop: camera, detection, selection, stability rule, robot actions, preview |
| `hand.py` | Pointing-gesture detection and pointing ray |
| `objects.py` | YOLO object detection and filtering |
| `selector.py` | Rule-based target selection (angle test, thresholds, ambiguity) |
| `robot.py` | Pixel-to-head-angle mapping and background text-to-speech |
| `head_test.py` | Standalone check that the simulated head moves |
| `camera_test.py` | Standalone webcam + hand landmark check |

Thresholds (confidence, maximum angle, minimum angle gap, stability frames, head/speech timing, maximum yaw/pitch) are constants at the top of the relevant file.

## Known limitations

- Pointing straight at the camera is not detected. The finger is foreshortened in the 2D image, so there is no usable direction.
- Only COCO object classes are recognised, and may not always be accurate. 
- The MuJoCo simulation runs slower than real time on a laptop CPU. The speech delay compensates so the name is spoken after the head arrives.
- The video briefly pauses during each head movement (`goto_target` blocks), which happens only once per new target.
- Objects lined up behind each other along the pointing direction get similar angles and are usually reported as ambiguous. The selection does not use distance to prefer the nearer object.

## Troubleshooting (Problems I encountered and how I resolved them) 

- **Webcam error / "camera busy"**: close the Control app, Teams, Zoom or any other program using the camera; make sure the daemon was started with `--no-media`.
- **MuJoCo window closes on start**: start the daemon with `--no-media`.
