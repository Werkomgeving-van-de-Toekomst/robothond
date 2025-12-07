# Unitree Go2 URDF Bestanden

Deze directory bevat de URDF (Unified Robot Description Format) bestanden voor de Unitree Go2 robot.

## Bron

Deze bestanden zijn afkomstig van de officiële Unitree Go2 URDF repository:
- Repository: https://github.com/Unitree-Go2-Robot/go2_description
- Licentie: Zie LICENSE bestand

## Structuur

```
urdf/
├── urdf/                    # URDF bestanden
│   ├── go2_description.urdf      # Hoofd URDF bestand
│   ├── go2_description.urdf.xacro  # Xacro versie
│   ├── gazebo.urdf.xacro          # Gazebo simulatie versie
│   ├── leg.urdf.xacro             # Been definitie
│   └── transmission.urdf.xacro    # Transmissie definitie
├── xacro/                  # Xacro macro's
│   ├── robot.xacro        # Robot hoofdstructuur
│   ├── leg.xacro          # Been macro's
│   ├── materials.xacro    # Materiaal definities
│   └── ...
├── meshes/                 # 3D mesh bestanden (DAE format)
│   ├── trunk.dae
│   ├── hip.dae
│   ├── thigh.dae
│   ├── calf.dae
│   └── foot.dae
├── dae/                    # Alternatieve mesh bestanden
├── config/                 # Configuratiebestanden
│   ├── go2_description.rviz  # RViz configuratie
│   └── ros_control/        # ROS control configuratie
└── launch/                 # ROS launch bestanden
    └── robot.launch.py
```

## Gebruik

### Met ROS/ROS2

```bash
# Laad robot model in RViz
ros2 launch urdf/launch/robot.launch.py

# Of gebruik het URDF bestand direct
ros2 run robot_state_publisher robot_state_publisher urdf/go2_description.urdf
```

### Met Python (pybullet, mujoco, etc.)

```python
import pybullet as p

# Laad URDF in PyBullet
robot_id = p.loadURDF("urdf/go2_description.urdf", [0, 0, 1])
```

### Met Gazebo

```bash
# Gebruik de Gazebo specifieke URDF
ros2 launch urdf/launch/robot.launch.py use_gazebo:=true
```

## Belangrijke Bestanden

- **go2_description.urdf**: Standaard URDF bestand voor visualisatie
- **gazebo.urdf.xacro**: Gazebo simulatie versie met physics properties
- **meshes/**: 3D modellen van robot onderdelen

## Updates

Om de URDF bestanden bij te werken:

```bash
cd urdf
git pull origin main
```

Of verwijder de directory en clone opnieuw:

```bash
rm -rf urdf
git clone https://github.com/Unitree-Go2-Robot/go2_description.git urdf
cd urdf
rm -rf .git .github
```

## Licentie

Zie het LICENSE bestand voor licentie informatie.
