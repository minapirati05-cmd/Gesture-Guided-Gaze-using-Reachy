
import math 

"""Hand-gesture helpers built on MediaPipe hand landmarks.

MediaPipe returns 21 landmarks per hand, with x and y normalized to [0, 1].
Indices follow the official MediaPipe hand landmark diagram.
"""
import math

# --- Landmark indices (MediaPipe hand model) ---
WRIST = 0

INDEX_MCP = 5       # base joint of the index finger
INDEX_PIP = 6       # middle joint of the index finger
INDEX_TIP = 8

MIDDLE_PIP = 10
MIDDLE_TIP = 12

RING_PIP = 14
RING_TIP = 16

PINKY_PIP = 18
PINKY_TIP = 20


def distance(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def is_extended(hand, tip: int, pip: int) -> bool:
    """
    A finger counts as extended when its tip is further from the wrist than
    its middle joint (PIP). Comparing distances (rather than y-coordinates)
    makes the test independent of which way the hand is pointing, and
    comparing two distances on the same hand makes it independent of how
    close the hand is to the camera.
    """
    wrist = hand[WRIST]
    distance_tip_wrist = distance(hand[tip], wrist)
    distance_pip_wrist = distance(hand[pip], wrist)
    return distance_tip_wrist > distance_pip_wrist


def is_pointing(hand) -> bool:
    """
    Pointing = index finger extended, middle/ring/pinky fingers curled.
    The thumb is ignored, since people hold it differently when pointing.
    """
    return (
        is_extended(hand, INDEX_TIP, INDEX_PIP)
        and not is_extended(hand, MIDDLE_TIP, MIDDLE_PIP)
        and not is_extended(hand, RING_TIP, RING_PIP)
        and not is_extended(hand, PINKY_TIP, PINKY_PIP)
    )


def pointing_ray(hand, w, h): 
    """
    Returns a 2D ray (origin, direction) in pixel coordinates, representing
    the pointing direction of the hand. The origin is the index finger tip,
    and the direction is from the PIP joint to the tip.
    """
    origin = hand[INDEX_TIP]
    mcp = hand[INDEX_MCP]
    origin_px = (int(origin.x * w), int(origin.y * h))
    direction_px = (int((origin.x - mcp.x) * w), int((origin.y - mcp.y) * h))
    return origin_px, direction_px
