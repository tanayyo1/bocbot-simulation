#!/usr/bin/env python3

import sys
import select
import termios
import tty
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gazebo_msgs.srv import SetEntityState

msg = """
BOCBOT - CINEMATIC ROVER CONTROLLER
-------------------------------------------
W/S : Smooth Acceleration (Forward/Reverse)
A/D : Smooth Steering (Left/Right)
Q/E : Pivot in Place (Left/Right)
R   : Reset Position
Ctrl-C : Quit
-------------------------------------------
"""

class Teleop(Node):
    def __init__(self):
        super().__init__('teleop_wasd')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.set_state_client = self.create_client(SetEntityState, '/gazebo/set_entity_state')

    def reset_robot(self):
        if self.set_state_client.service_is_ready():
            req = SetEntityState.Request()
            req.state.name = 'bocbot'
            req.state.pose.position.z = 0.8
            req.state.pose.orientation.w = 1.0
            self.set_state_client.call_async(req)

def getKeys(settings):
    """Read all currently buffered key presses as a set."""
    tty.setraw(sys.stdin.fileno())
    keys = set()
    rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
    if rlist:
        keys.add(sys.stdin.read(1))
        while True:
            rlist_inner, _, _ = select.select([sys.stdin], [], [], 0.0)
            if rlist_inner:
                keys.add(sys.stdin.read(1))
            else:
                break
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return keys

def main(args=None):
    rclpy.init(args=args)
    settings = termios.tcgetattr(sys.stdin)
    node = Teleop()

    # --- TUNING PARAMETERS ---
    MAX_SPEED = 4.0          # m/s maximum linear velocity
    MAX_TURN  = 3.5          # rad/s maximum angular velocity

    # Acceleration rates (per second, time-based for frame-rate independence)
    LIN_ACCEL = 3.0          # How fast the rover accelerates
    LIN_DECEL = 4.0          # How fast the rover brakes to stop
    ANG_ACCEL = 5.0          # How fast steering ramps up
    ANG_DECEL = 8.0          # How fast steering centers back

    # At MAX_SPEED, turning power is reduced to this fraction to prevent flipping
    TURN_SCALE_AT_MAX = 0.4

    # Auto-repeat debounce: keys are considered "held" for this long after last seen.
    # Bridges the gap between initial keypress and OS auto-repeat kicking in (~250-660ms).
    KEY_HOLD_WINDOW = 0.5

    # --- STATE ---
    current_speed = 0.0
    current_turn  = 0.0
    key_last_seen = {}       # key -> monotonic timestamp of last detection
    last_time = time.monotonic()

    try:
        print(msg)
        while True:
            now = time.monotonic()
            dt = min(now - last_time, 0.1)   # clamp to prevent huge jumps
            last_time = now

            # --- KEY INPUT WITH DEBOUNCE ---
            raw_keys = getKeys(settings)

            # Update timestamps for every key detected this frame
            for k in raw_keys:
                key_last_seen[k] = now

            # Build effective key set: includes keys within hold window
            keys = set()
            expired = []
            for k, t in key_last_seen.items():
                if now - t < KEY_HOLD_WINDOW:
                    keys.add(k)
                else:
                    expired.append(k)
            for k in expired:
                del key_last_seen[k]

            # --- QUIT / RESET ---
            if '\x03' in keys:
                break
            if 'r' in raw_keys:    # only trigger on actual press, not hold
                node.reset_robot()

            # --- DETERMINE TARGETS ---
            target_speed = 0.0
            if 'w' in keys:
                target_speed = MAX_SPEED
            elif 's' in keys:
                target_speed = -MAX_SPEED

            target_turn = 0.0
            pivoting = False

            if 'q' in keys:
                target_turn = MAX_TURN
                target_speed = 0.0
                pivoting = True
            elif 'e' in keys:
                target_turn = -MAX_TURN
                target_speed = 0.0
                pivoting = True
            elif 'a' in keys:
                target_turn = MAX_TURN
            elif 'd' in keys:
                target_turn = -MAX_TURN

            # Speed-dependent turn reduction: less turning at higher speeds
            if not pivoting and abs(current_speed) > 0.1:
                speed_ratio = abs(current_speed) / MAX_SPEED
                turn_scale = 1.0 - speed_ratio * (1.0 - TURN_SCALE_AT_MAX)
                target_turn *= turn_scale

            # --- SMOOTH LINEAR RAMP ---
            if pivoting:
                # Instant zero for clean pivot
                current_speed = 0.0
            else:
                if current_speed < target_speed:
                    rate = LIN_ACCEL if target_speed > 0 else LIN_DECEL
                    current_speed = min(target_speed, current_speed + rate * dt)
                elif current_speed > target_speed:
                    rate = LIN_ACCEL if target_speed < 0 else LIN_DECEL
                    current_speed = max(target_speed, current_speed - rate * dt)

            # --- SMOOTH ANGULAR RAMP ---
            if current_turn < target_turn:
                ang_rate = ANG_ACCEL if abs(target_turn) >= abs(current_turn) else ANG_DECEL
                current_turn = min(target_turn, current_turn + ang_rate * dt)
            elif current_turn > target_turn:
                ang_rate = ANG_ACCEL if abs(target_turn) >= abs(current_turn) else ANG_DECEL
                current_turn = max(target_turn, current_turn - ang_rate * dt)

            # --- PUBLISH ---
            twist = Twist()
            twist.linear.x = current_speed
            twist.angular.z = current_turn
            node.publisher_.publish(twist)

            rclpy.spin_once(node, timeout_sec=0)

    except Exception as e:
        print(e)
    finally:
        # Send zero velocity on exit
        node.publisher_.publish(Twist())
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        rclpy.shutdown()

if __name__ == '__main__':
    main()
