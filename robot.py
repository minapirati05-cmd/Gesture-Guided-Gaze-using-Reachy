
import threading
import pyttsx3
import time 

max_yaw = 30 
max_pitch = 20 

def pixel_head_angles(cx, cy, w, h): 
    offset_x = (cx - (w/2)) / (w/2)
    offset_y = (cy - (h/2)) / (h/2)

    yaw = offset_x * max_yaw
    pitch = offset_y * max_pitch


    return (yaw, pitch)

def _say(text, delay): 
    """Speak text and wait until finished. Runs inside a background thread."""
    time.sleep(delay)
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # words per minute slowed 
    engine.say(text)
    engine.runAndWait()


def speak(text, delay=0): 
    """Speak text in the background so the camera loop keeps running."""
    thread = threading.Thread(target=_say, args=(text, delay), daemon = True)
    thread.start()
    