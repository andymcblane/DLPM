from flask import Flask
import time
import time
from influxdb import InfluxDBClient
from tasks import (
    http_battery_voltage,
    force_disable_solar_devices,
    enable_solar_devices,
    disable_solar_devices,
)
import _thread
import toml
from queries import query_battery_voltage, set_device_state

app = Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return ""


# Device can check if they should be running. 0 or 1
# TODO: maybe consider handling if device does not exist
@app.route("/<device>")
def get_device_state(device):
    result = client.query(f"SELECT LAST(enabled) from {device}")
    item = list(result.get_points(measurement=device))[0]
    print(item["last"])
    return str(item["last"])


if __name__ == "__main__":
    # TODO: handle this better
    f = open("config.toml", "r")
    config = toml.loads(f.read())
    f.close()

    # TODO: handle this better too, what if can't connect? 
    client = InfluxDBClient(host=config["influx_host"], port=config["influx_port"])

    print(client.get_list_database())

    # TODO: create if doesn't exist
    client.switch_database("solar")

    # Disable all devices, also ensures the InfluxDB measurement exists
    for device in config["devices"]:
        set_device_state(client, device, "0")
    time.sleep(5)

    # Get battery voltage
    _thread.start_new_thread(http_battery_voltage, (client, config["BATTERY_VOLTAGE_SENSOR_WEBSERVER"]))

    # 'Force' shut everything off if voltage gets far too low
    _thread.start_new_thread(force_disable_solar_devices, (client, config))

    # Enable devices when we have excess solar
    _thread.start_new_thread(enable_solar_devices, (client, config))

    # Disable devices when solar drops below cutoff
    _thread.start_new_thread(disable_solar_devices, (client, config))

    # Start webserver, devices will hit their endpoint (e.g pump) to see if they should run.
    # This way all logic is controlled here, requring less in-field device flashes.
    app.run(debug=False, host="0.0.0.0")
