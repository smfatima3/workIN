# What the robot simulations measure

The experiments test a planner decision after the source of a stored observation disconnects. The matched conditions share a physical scene, controller, task and decision seed. The recorded model chooses an action, and the simulator determines the outcome. This design can attribute a difference within the tested setup to changing the stored observation.

| Task | Implementation | Measured endpoint | Available view |
| --- | --- | --- | --- |
| Conveyor handoff | MuJoCo 3.17.0. A weld holds a free parcel at a fixed release point. A velocity-controlled carrier moves on a rail. The planner can inspect, hold, or enter a belt speed that determines release time. | Parcel-floor contact; delivery requires sustained support on the carrier. | Native 3D geometry and a 2D trace. The weld has no gripper mesh. |
| Earlier pedestrian route | MuJoCo. A mobile robot box follows its commanded route past a stationary pedestrian capsule with local avoidance active. | Contact between robot and pedestrian geometry. | Native 3D retained/corrected pair and the original five-condition schematic. |
| Stationary and moving trays | Godot 2D. The gantry executes a placement onto one of the trays. | Settled supported load above the simulated 5 kg rating. | Logged 2D trajectories. |
| Glass and bath | Geometric stream overlap and water-volume accounting for the glass; a metered flow model for the bath. | Water escaping secondary containment and task completion. | Schematics of recorded volumes. |

The native 3D videos run the archived MuJoCo physics functions with the recorded actions and original scene geometry. The renderer captures the full solver state, checks the archived trajectories and outcomes, and changes the camera, colors, lighting and playback speed for visibility. No new planner decisions enter the videos. The video manifests identify the source records and the selection rule.

**Scope for the paper.** The results establish a memory effect on high-level control choices and their consequences in these simulations. Arm reachability, grasp acquisition, joint-level motion planning, actuator error, physical injury and transfer to hardware remain untested. Rendering the same state in 3D adds a way to inspect the evidence; it adds no experimental observations.
