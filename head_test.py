from reachy_mini import ReachyMini
import time 
from reachy_mini.utils import create_head_pose

with ReachyMini() as mini:
    print("yaw +25")
    mini.goto_target(head = create_head_pose(yaw=25, degrees = True), duration=2)
    time.sleep(2)
    print("yaw -25")
    mini.goto_target(head = create_head_pose(yaw=-25, degrees = True), duration=2)
    time.sleep(2)
    print("pitch +15")
    mini.goto_target(head = create_head_pose(pitch=15, degrees = True), duration=2)
    time.sleep(2)
    print("centre")
    mini.goto_target(head=create_head_pose(), duration=1.0)


