import math 

max_angle = 25 
min_gap = 10 

def angle_between(v1, v2): 
    """Calculate the angle in degrees between two vectors."""
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude_v1 = (v1[0]**2 + v1[1]**2) ** 0.5
    magnitude_v2 = (v2[0]**2 + v2[1]**2) ** 0.5
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return None
    cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
    # Clamp the cosine value to the range [-1, 1] to avoid numerical issues
    cos_angle = max(-1, min(1, cos_angle))
    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)
    return angle_deg


def box_center(bbox):
    x1, y1, x2, y2 = bbox 
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def select_target(origin, direction, objects): 
    candidates = []
    for obj in objects:
        cx, cy = box_center(obj['bbox'])
        vector_to_object = (cx - origin[0], cy - origin[1])
        angle = angle_between(direction, vector_to_object)
        if angle is None: 
            continue 
        candidates.append((angle, obj))

    candidates.sort(key=lambda c: c[0])  # Sort by angle
    if not candidates or candidates[0][0] > max_angle:
        return None, "none"

    if len(candidates) > 1 and candidates[1][0] - candidates[0][0] < min_gap:
        return None, "ambiguous"

    # Select the object with the smallest angle
    return candidates[0][1], "target"
