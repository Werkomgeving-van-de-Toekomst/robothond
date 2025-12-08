# Unitree Go2 SDK GitHub Repositories

Overzicht van alle officiële GitHub repositories voor de Unitree Go2 SDK.

## Officiële Repositories

### 1. unitree_sdk2

**Repository**: https://github.com/unitreerobotics/unitree_sdk2

**Beschrijving**: 
De officiële SDK voor Unitree robots (Go2, B2, H1). Bevat de core SDK functionaliteit in C++.

**Gebruik**:
- Basis SDK voor alle Unitree robots
- C++ implementatie
- Low-level robot controle

**Clone**:
```bash
git clone https://github.com/unitreerobotics/unitree_sdk2.git
```

### 2. unitree_sdk2_python

**Repository**: https://github.com/unitreerobotics/unitree_sdk2_python

**Beschrijving**: 
Python interface voor unitree_sdk2. Bedoeld voor ontwikkeling van Go2, B2, H1 en G1 robots in echte omgevingen.

**Gebruik**:
- Python wrapper voor de SDK
- Eenvoudiger te gebruiken dan C++ versie
- Geschikt voor rapid prototyping

**Clone**:
```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
```

**Installatie**:
```bash
cd unitree_sdk2_python
pip install -r requirements.txt
# Of
pip install unitree_sdk2_python
```

### 3. unitree_ros2

**Repository**: https://github.com/unitreerobotics/unitree_ros2

**Beschrijving**: 
ROS2 pakket voor ontwikkeling van Go2 en B2 robots. Interfaces zijn consistent met unitree_sdk2.

**Gebruik**:
- ROS2 integratie
- Robot state publishers
- Commando subscribers
- Geschikt voor ROS2 workflows

**Clone**:
```bash
git clone https://github.com/unitreerobotics/unitree_ros2.git
```

### 4. go2_description (URDF)

**Repository**: https://github.com/Unitree-Go2-Robot/go2_description

**Beschrijving**: 
URDF (Unified Robot Description Format) bestanden voor de Go2 robot. Bevat robot model definities voor simulatie en visualisatie.

**Gebruik**:
- Robot model voor simulatie (Gazebo, PyBullet, MuJoCo)
- Visualisatie in RViz
- 3D mesh bestanden

**Clone**:
```bash
git clone https://github.com/Unitree-Go2-Robot/go2_description.git
```

## Unitree Robotics GitHub Organisatie

Alle officiële repositories zijn te vinden onder:
**https://github.com/unitreerobotics**

## Welke Repository Gebruiken?

### Voor Python Ontwikkeling

Gebruik **unitree_sdk2_python**:
```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -r requirements.txt
```

### Voor C++ Ontwikkeling

Gebruik **unitree_sdk2**:
```bash
git clone https://github.com/unitreerobotics/unitree_sdk2.git
cd unitree_sdk2
# Volg build instructies in README
```

### Voor ROS2 Ontwikkeling

Gebruik **unitree_ros2**:
```bash
git clone https://github.com/unitreerobotics/unitree_ros2.git
cd unitree_ros2
# Volg ROS2 installatie instructies
```

### Voor Simulatie

Gebruik **go2_description**:
```bash
git clone https://github.com/Unitree-Go2-Robot/go2_description.git
```

## Documentatie Links

- **Officiële Developer Documentation**: https://support.unitree.com/home/en/developer
- **Unitree Website**: https://www.unitree.com
- **Go2 Product Pagina**: https://www.unitree.com/en/go2

## Dit Project

Dit project (`unitreego2`) is een **custom Python wrapper** gebaseerd op de officiële SDK's, met extra functionaliteit zoals:
- Flow executor voor geautomatiseerde actiesequenties
- Voice control integratie
- Web search en display functionaliteit
- Reinforcement learning ondersteuning
- PyBullet simulatie integratie

## Referenties

- [Go2 Handleiding](./GO2_HANDLEIDING.md)
- [Go2 SDK Referentie](./GO2_SDK_REFERENTIE.md)
- [Project README](../README.md)

