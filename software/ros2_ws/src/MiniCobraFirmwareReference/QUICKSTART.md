# Mini-Cobra Quick Start Guide

## Hardware Setup
- 8 Dynamixel motors (IDs 2-9)
- Connected via U2D2 on `/dev/ttyUSB0`
- Baudrate: 57600

## Running the Robot

### Main Control Interface
```bash
python3 main.py
```

This launches the keyboard interface with the following controls:

### Keyboard Commands

**Sidewinding (Locomotion)**
- `w` - Sidewind forward
- `a` - Sidewind left
- `d` - Sidewind right

**Transformations**
- `z` - Zero position (straight line)
- `x` - Hexagon toggle (transform to/from hex)
- `e` - Spiral toggle
- `t` - Tilt forward (from hex position)
- `y` - Tilt backward (from hex position)

**Crawling**
- `c` - Crawl forward
- `v` - Crawl backward
- `b` - Crawl counter-clockwise
- `n` - Crawl clockwise

**Survey Mode**
- `s` - Survey with major panning
- `f` - Survey with minor panning

**Control**
- `h` - Halt (stop all movement)
- `k` - Reboot all motors
- `j` - Force reboot (without halt)
- `ESC` - Quit program

## Testing Scripts

### Basic Motor Test
```bash
python3 simple_test.py
```
Quick test to verify all motors are connected and responsive.

### Sidewinding Test
```bash
python3 sidewind_test.py
```
Standalone sidewinding test (20 seconds).
- Amplitude: 500 pulses (adjusted for optimal motion)
- Frequency: 0.2 Hz

### Motor Scanner
```bash
python3 scan_motors.py
```
Scans and lists all connected motors with their IDs.

## Configuration

### Adjusting Sidewinding Parameters

Edit `controllers/SidewindController.py`:
```python
self.theta = 45  # Amplitude in degrees (currently optimized)
self.period = 2.5  # Period in seconds
```

### Motor Constants

See `constants/motor_constants.py`:
- `JOINT_IDS = [2, 3, 4, 5, 6, 7, 8, 9]` - Motor IDs
- `MIN_POSITION = 1000` - Minimum safe position
- `MAX_POSITION = 3000` - Maximum safe position
- `ZERO_POSITION = 2048` - Center position

## Troubleshooting

**Motors not responding:**
1. Check USB connection: `ls -la /dev/ttyUSB*`
2. Run motor scanner: `python3 scan_motors.py`
3. Verify motor IDs match configuration

**Sidewinding too aggressive:**
- Reduce `theta` in `SidewindController.py`
- Or reduce amplitude in `sidewind_test.py`

**Sidewinding too slow:**
- Increase `freq` parameter
- Adjust `prof_velo` in SidewindController

## Architecture

- `MotorDriver.py` - Low-level motor communication
- `controllers/CoreController.py` - Main controller coordinator
- `controllers/SidewindController.py` - Sidewinding motion
- `controllers/TransformController.py` - Shape transformations
- `controllers/CrawlController.py` - Crawling locomotion
- `controllers/SurveyController.py` - Survey/panning motions
- `KeypressInterface.py` - Keyboard input handler

See `CLAUDE.md` for detailed architecture documentation.
