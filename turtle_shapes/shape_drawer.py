"""Drive the turtlesim turtle along a circle, square or spiral.

Publishes geometry_msgs/Twist on /turtle1/cmd_vel and uses turtlesim/Pose
feedback on /turtle1/pose to know when a shape is finished.

Parameters:
  shape  (string) circle | square | spiral   (default: circle)
  size   (double) circle radius / square side length [m]   (default: 2.0)
  speed  (double) linear speed [m/s]                        (default: 1.0)
  reset  (bool)   call /reset before drawing                (default: true)
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.msg import Pose

WALL_MIN = 0.5
WALL_MAX = 10.5


def angle_diff(a, b):
    """Smallest signed difference a - b, wrapped to [-pi, pi]."""
    return math.atan2(math.sin(a - b), math.cos(a - b))


class ShapeDrawer(Node):

    def __init__(self):
        super().__init__('shape_drawer')
        self.shape = self.declare_parameter('shape', 'circle').value
        self.size = self.declare_parameter('size', 2.0).value
        self.speed = self.declare_parameter('speed', 1.0).value
        do_reset = self.declare_parameter('reset', True).value

        if self.shape not in ('circle', 'square', 'spiral'):
            raise ValueError(f"unknown shape '{self.shape}', use circle, square or spiral")

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.pose = None
        self.done = False

        # Shape state
        self.start_pose = None    # pose at the start of the current segment
        self.turned = 0.0         # accumulated rotation for the circle [rad]
        self.prev_theta = None
        self.side = 0             # square: sides completed
        self.turning = False      # square: driving straight or rotating
        self.spiral_v = 0.2       # spiral: growing linear speed

        if do_reset:
            self.reset_sim()

        self.timer = self.create_timer(0.02, self.control_loop)
        self.get_logger().info(f'Drawing a {self.shape} (size={self.size}, speed={self.speed})')

    def reset_sim(self):
        client = self.create_client(Empty, '/reset')
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().warn('/reset not available, drawing from current position')
            return
        future = client.call_async(Empty.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

    def pose_callback(self, msg):
        self.pose = msg

    def publish(self, linear, angular):
        twist = Twist()
        twist.linear.x = float(linear)
        twist.angular.z = float(angular)
        self.cmd_pub.publish(twist)

    def finish(self, reason):
        self.publish(0.0, 0.0)
        self.done = True
        self.timer.cancel()
        self.get_logger().info(f'{self.shape} finished: {reason}')

    def control_loop(self):
        if self.pose is None or self.done:
            return
        if self.start_pose is None:
            self.start_pose = self.pose
            self.prev_theta = self.pose.theta
        getattr(self, f'step_{self.shape}')()

    def step_circle(self):
        # v = w * r  ->  w = v / r
        self.publish(self.speed, self.speed / self.size)
        self.turned += abs(angle_diff(self.pose.theta, self.prev_theta))
        self.prev_theta = self.pose.theta
        if self.turned >= 2 * math.pi:
            self.finish('one full revolution')

    def step_square(self):
        p, s = self.pose, self.start_pose
        if not self.turning:
            dist = math.hypot(p.x - s.x, p.y - s.y)
            remaining = self.size - dist
            if remaining <= 0.01:
                self.turning, self.start_pose = True, p
                self.publish(0.0, 0.0)
            else:
                # slow down near the corner for a sharper result
                self.publish(min(self.speed, 2.0 * remaining + 0.05), 0.0)
        else:
            remaining = math.pi / 2 - abs(angle_diff(p.theta, s.theta))
            if remaining <= 0.005:
                self.side += 1
                self.turning, self.start_pose = False, p
                self.publish(0.0, 0.0)
                if self.side == 4:
                    self.finish('4 sides drawn')
            else:
                self.publish(0.0, min(1.5, 3.0 * remaining + 0.05))

    def step_spiral(self):
        # constant turn rate with a growing forward speed -> radius grows outward
        p = self.pose
        if not (WALL_MIN < p.x < WALL_MAX and WALL_MIN < p.y < WALL_MAX):
            self.finish('reached the wall')
            return
        self.publish(self.spiral_v, 2.0)
        self.spiral_v += 0.005 * self.speed


def main(args=None):
    rclpy.init(args=args)
    node = ShapeDrawer()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        node.publish(0.0, 0.0)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
