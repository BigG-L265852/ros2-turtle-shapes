# turtle_shapes — ROS 2 Level 1

Beginner application for Minor Adaptive Robotics, **Level 1**: *"Follow ROS.org tutorials and implement a beginner application."*
It covers the Week 1 practice (publisher/subscriber) and the homework (drive turtlesim in a **circle, square and spiral**).

ROS 2 Jazzy, Python (`ament_python`).

## ROS.org tutorials used

| Tutorial (docs.ros.org/en/jazzy/Tutorials) | Where it shows up |
|---|---|
| Using turtlesim, ros2, and rqt | turtlesim as the simulated robot |
| Understanding nodes / topics | `shape_drawer` publishes `/turtle1/cmd_vel`, subscribes to `/turtle1/pose` |
| Understanding services | `shape_drawer` calls `/reset` (std_srvs/Empty) before drawing |
| Understanding parameters | `shape`, `size`, `speed`, `reset` parameters |
| Creating a workspace / Creating a package | `ros2_ws`, `ros2 pkg create --build-type ament_python` |
| Writing a simple publisher and subscriber (Python) | `talker` / `listener` on `/chatter` |
| Launching nodes / Creating a launch file | `launch/shapes.launch.py` |

## Nodes

```
             /turtle1/cmd_vel (geometry_msgs/Twist)
shape_drawer ───────────────────────────────▶ turtlesim
             ◀───────────────────────────────
             /turtle1/pose (turtlesim/Pose)
             ── /reset (service) ───────────▶

talker ── /chatter (std_msgs/String) ──▶ listener
```

**shape_drawer** uses pose feedback (closed loop) instead of timing, so the shapes close properly:

- **circle** — constant `v` and `ω = v / r`; stops after a full 2π of accumulated rotation.
- **square** — drive straight until the travelled distance equals `size`, then rotate 90° in place; repeat 4×. Slows down near corners/end of turn for sharper corners.
- **spiral** — constant `ω`, linearly increasing `v`, so the radius (`r = v/ω`) grows; stops when the turtle reaches the wall.

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select turtle_shapes
source install/setup.bash
```

## Run

All-in-one (starts turtlesim + draws):

```bash
ros2 launch turtle_shapes shapes.launch.py shape:=circle
ros2 launch turtle_shapes shapes.launch.py shape:=square size:=3.0
ros2 launch turtle_shapes shapes.launch.py shape:=spiral
```

Or step by step:

```bash
ros2 run turtlesim turtlesim_node                                   # terminal 1
ros2 run turtle_shapes shape_drawer --ros-args -p shape:=square     # terminal 2
```

Publisher / subscriber:

```bash
ros2 run turtle_shapes talker      # terminal 1
ros2 run turtle_shapes listener    # terminal 2
```

## Useful CLI checks

```bash
ros2 node list
ros2 topic list
ros2 topic echo /turtle1/pose
ros2 topic hz /chatter
ros2 param list /shape_drawer
rqt_graph
```

## Tested

- circle (r=2): finishes back at start, ~3 cm error
- square (side 2): finishes back at start, ~3 cm error
- spiral: reaches the wall after ~40 s
- talker → listener: messages received at 2 Hz
