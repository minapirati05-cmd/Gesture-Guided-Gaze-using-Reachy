

max_yaw = 30 
max_pitch = 20 

def pixel_head_angles(cx, cy, w, h): 
    offset_x = (cx - (w/2)) / (w/2)
    offset_y = (cy - (h/2)) / (h/2)

    yaw = offset_x * max_yaw
    pitch = offset_y * max_pitch


    return (yaw, pitch)