# IITS - Industrial IoT Threat Simulator

IITS - Industrial IoT Threat Simulator is a python project that simulates an industrial environment with several IoT devices.

It includes an IoT-MQTT attack environment simulated through a docker mosquitto. It is possible to simulate brute force and DDoS attacks.

The simulator was projected by Diogo Rocha de Araujo.

**Disclamer**: The IITS - Industrial IoT Threat Simulator its destined only for research and controlled enviroment tests.

# Functionalities

    - MQTT data publish within IoT simulated devices
    - Authentication attempt brute-force attack
    - DDoS attack simulation
    - Logging for detailed analises

# Project structure

```
camed_iits/
├── iits.py                                 # Simulator main script
├── Dockerfile                              # Container configuration
├── docker-compose.yml                      # Docker enviroment configuration
├── logs/
│   └── iits.log                            # IITS log file
├── mosquitto/                              # Broker configuration
│   └── config/
│       └── mosquitto.conf                  # Mosquitto configuration
├── run.sh                                  # Shell script for quick environment initialization
├── requirements.txt                        # Python required libraries
├── README.md                               # This file
```

# Installation

## How to install the software for python use?
```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## Dependences

    - Python 3.12 or higher
    - Docker and Docker Compose (to execution by containers)

# How to execute

## Quick Use

### Method 1: Using Python directly

Run the simulator:
```bash
python iits.py --broker localhost --devices 5 --bruteforce --ddos
```

### Method 2: Using Docker Compose

1. Create the directory structure for Mosquitto:
```bash
mkdir -p mosquitto/config mosquitto/data mosquitto/log
```

2. Copy the `mosquitto.conf` file to `mosquitto/config/`.

3. Start the containers:
```bash
docker-compose up
```

4. Access the MQTT Explorer at `http://localhost:4000` to view the messages.

## Configuration Options

```
--broker BROKER             MQTT broker address (default: localhost)
--port PORT                 MQTT broker port (default: 1883)
--duration DURATION         Simulation duration in seconds (default: 300)
--devices DEVICES           Number of IoT devices (default: 5)
--bruteforce                Enable brute force attack
--bruteforce-rate N         Rate of brute force attempts per second (default: 10)
--ddos                      Enable DDoS attack
--ddos-type TYPE            DDoS attack type: connection or publish (default: connection)
--ddos-rate N               DDoS attack rate (default: 50)
--log-level LEVEL           og level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

## Usage Examples

### Basic Simulation
```bash
python iits.py --devices 3 --duration 120
```

### Brute Force Attack
```bash
python iits.py --devices 3 --bruteforce --bruteforce-rate 20
```

### Publishing DDoS Attack
```bash
python iits.py --devices 3 --ddos --ddos-type publish --ddos-rate 100
```

### Full Scenario
```bash
python iits.py --devices 5 --bruteforce --ddos --duration 600
```

## Research Notes

- Logs are saved in `iits.log` for later analysis
- Brute force attack starts after 25% of simulation time
- DDoS attack starts after 50% of simulation time
- Devices are distributed among different types: temperature, humidity and brightness