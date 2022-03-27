from datetime import datetime


def get_device_enabled(client, device):
    result = client.query(f"SELECT LAST(enabled) from {device}")
    item = list(result.get_points(measurement=device))[0]
    if int(item["last"]) == 0:
        return False
    else:
        return True


def get_device_last_enabled_time(client, device):
    result = client.query(
        f"SELECT * FROM {device} WHERE enabled = '1' ORDER BY desc LIMIT 1"
    )
    item = list(result.get_points(measurement=device))[0]
    return item["time"]


def get_next_disabled_device(client, devices):
    for device in devices:
        if not get_device_enabled(client, device):
            return device
    return None


def set_device_state(client, device, state):
    # Do we really need tags? 
    json_body = [
        {"measurement": device, "tags": {"host": "default"}, "fields": {"enabled": state}}
    ]

    client.write_points(json_body)


def query_battery_voltage(client):
    result = client.query("SELECT * from battery_voltage ORDER BY desc LIMIT 1")
    item = list(result.get_points(measurement="battery_voltage"))[0]

    # TODO: I hope there's a better way to get a datetime obj instead of relying on the strptime
    last_time = datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    delta_seconds = (datetime.utcnow() - last_time).total_seconds()
    # only consider the battery voltage valid if it was uploaded in the last minute
    # TODO: Consider using a rolling average (probably SELECT AVG(battery_voltage) ...  LIMIT 5 )
    if delta_seconds > 60:
        return str(0)
    return str(item["voltage"])
