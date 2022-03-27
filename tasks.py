import requests
import time
import threading
from datetime import datetime
from queries import (
    get_next_disabled_device,
    set_device_state,
    query_battery_voltage,
    get_device_last_enabled_time,
    get_device_enabled,
)



# Arduino is attached to the battery, which publishes the current voltage on
# an HTTP server :80. Grab it and push to influx.
def http_battery_voltage(client, VOLTAGE_SENSOR_IP):
    while True:
        try:
            resp = requests.get(VOLTAGE_SENSOR_IP, timeout=10)
            voltage = float(resp.content)
            json_body = [
                {
                    "measurement": "battery_voltage",
                    "tags": {"host": "default"},
                    "fields": {"voltage": voltage},
                }
            ]

            client.write_points(json_body)

        except Exception as e:
            pass
        time.sleep(10)


# If the current voltage is above the threshold, get the next device (in order)
# and turn it on.
def enable_solar_devices(client, config):
    while True:
        try:
            if query_battery_voltage(client) > config["excess_solar_threshold"]:
                device = get_next_disabled_device(client, config["devices"])
                print(f"Enabling {device}")
                if device == "pump":
                    # TODO: check if tank can take water
                    set_device_state(client, device, "1")
                elif device == "water_heater":
                    # This has it's own thermostat, we'll just let it regulate itself.
                    set_device_state(client, device, "1")
                elif device == "air_con":
                    # TODO: check room temp
                    set_device_state(client, device, "1")
                elif device == "crypto":
                    set_device_state(client, device, "1")
                elif device == None and config["log_when_excess_solar"]:
                    set_device_state(client, "log_when_excess_solar", "1")
        except:
            pass
        time.sleep(60)


# If the current voltage is lower than the cutoff, disable devices from lower to higher priority
def disable_solar_devices(client, config):
    while True:
        try:
            if query_battery_voltage(client) < config["excess_solar_cutoff"]:
                if config["log_when_excess_solar"]:
                    set_device_state(client, "log_when_excess_solar", "0")
                # Loop through priority backwards
                devices = []
                for device in config["devices"]:
                    devices.append(device)
                for device in reversed(devices):
                    print(f"Is {device} enabled?")
                    if get_device_enabled(client, str(device)):
                        print(f"yes")
                        on_time = get_device_last_enabled_time(client, device)
                        on_time = datetime.strptime(on_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                        delta_seconds = (datetime.utcnow() - on_time).total_seconds()
                        # Device has run for sufficient time
                        if (
                            delta_seconds
                            > config["devices"][device]["minimum_enabled_seconds"]
                        ):
                            print(f"disable {device}")
                            set_device_state(client, device, "0")
                            # Only disable one device per loop
                            break
        except Exception as e:
            print(str(e))
            pass
        time.sleep(60)


# If voltage is low, disable everything
# TODO: what happens if we want the device running for another reason?
def force_disable_solar_devices(client, config):
    while True:
        try:
            if query_battery_voltage(client) < config["force_disable_solar_devices"]:
                for device in config["devices"]:
                    if device == "pump":
                        set_device_state(client, device, "0")
                    elif device == "water_heater":
                        set_device_state(client, device, "0")
                    elif device == "air_con":
                        set_device_state(client, device, "0")
                    elif device == "crypto":
                        set_device_state(client, device, "0")
        except:
            pass
        time.sleep(60)
