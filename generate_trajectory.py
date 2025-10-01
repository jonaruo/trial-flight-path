import json
from datetime import datetime, timedelta, timezone

# Start time
t0 = datetime.now(timezone.utc)

# Generate plane trajectory (5 min climb)
plane_points = []
for i in range(6):
    point_time = t0 + timedelta(minutes=i)
    plane_points.append({
        "time": point_time.isoformat() + "Z",
        "lat": -6.2 + i * 0.05,  # move north-east
        "lon": 106.8 + i * 0.05,
        "alt": i * 2000  # climb 0 → 10 km
    })

# Rocket trajectory (2 min boost)
rocket_points = []
for i in range(3):
    point_time = t0 + timedelta(minutes=6+i)
    rocket_points.append({
        "time": point_time.isoformat() + "Z",
        "lat": -5.95 + i * 0.05,
        "lon": 107.05 + i * 0.1,
        "alt": 10000 + i * 15000  # 10km → 40km
    })

# Payload orbit (just static orbital params for now)
payload = {
    "orbit": {
        "apoapsis": 500000,  # 500 km
        "periapsis": 500000,
        "inclination": 28.5
    }
}

data = {
    "plane": plane_points,
    "rocket": rocket_points,
    "payload": payload
}

with open("trajectory.json", "w") as f:
    json.dump(data, f, indent=2)

print("trajectory.json generated")
