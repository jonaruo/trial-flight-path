import json
from datetime import datetime, timedelta, timezone
import math

# --- Constants ---
CGK_AIRPORT_COORDS = {"lat": -6.12556, "lon": 106.65583}
ROCKET_RELEASE_ALTITUDE = 10000  # meters
FLIGHT_DURATION_MINUTES = 5
RETURN_DURATION_MINUTES = 5
ROCKET_BOOST_DURATION_MINUTES = 3
ROCKET_SPLASHDOWN_DURATION_MINUTES = 5

# Payload orbit parameters
EARTH_RADIUS = 6371000  # meters
apoapsis = 500000  # meters above surface
periapsis = 500000  # meters above surface
inclination = math.radians(28.5)
mu = 3.986004418e14  # Earth’s GM

# --- Time Setup ---
t0 = datetime.now(timezone.utc)

# --- Plane Trajectory ---
plane_points = []
for i in range(FLIGHT_DURATION_MINUTES + 1):
    point_time = t0 + timedelta(minutes=i)
    plane_points.append({
        "time": point_time.isoformat(),
        "lat": CGK_AIRPORT_COORDS["lat"] + i * 0.05,
        "lon": CGK_AIRPORT_COORDS["lon"] + i * 0.05,
        "alt": i * (ROCKET_RELEASE_ALTITUDE / FLIGHT_DURATION_MINUTES)
    })

release_point = plane_points[-1]
release_time = t0 + timedelta(minutes=FLIGHT_DURATION_MINUTES)

for i in range(1, RETURN_DURATION_MINUTES + 1):
    point_time = release_time + timedelta(minutes=i)
    plane_points.append({
        "time": point_time.isoformat(),
        "lat": release_point["lat"] - i * (release_point["lat"] - CGK_AIRPORT_COORDS["lat"]) / RETURN_DURATION_MINUTES,
        "lon": release_point["lon"] - i * (release_point["lon"] - CGK_AIRPORT_COORDS["lon"]) / RETURN_DURATION_MINUTES,
        "alt": release_point["alt"] - i * (release_point["alt"] / RETURN_DURATION_MINUTES)
    })

# --- Rocket Trajectory ---
rocket_points = []
for i in range(ROCKET_BOOST_DURATION_MINUTES + 1):
    point_time = release_time + timedelta(minutes=i)
    rocket_points.append({
        "time": point_time.isoformat(),
        "lat": release_point["lat"] + i * 0.1,
        "lon": release_point["lon"] + i * 0.1,
        "alt": release_point["alt"] + i * 30000
    })

apogee_point = rocket_points[-1]
apogee_time = release_time + timedelta(minutes=ROCKET_BOOST_DURATION_MINUTES)

for i in range(1, ROCKET_SPLASHDOWN_DURATION_MINUTES + 1):
    point_time = apogee_time + timedelta(minutes=i)
    rocket_points.append({
        "time": point_time.isoformat(),
        "lat": apogee_point["lat"] + i * 0.2,
        "lon": apogee_point["lon"] + i * 0.2,
        "alt": apogee_point["alt"] - i * (apogee_point["alt"] / ROCKET_SPLASHDOWN_DURATION_MINUTES)
    })
rocket_points[-1]["alt"] = 0

# --- Payload Orbit ---
payload_points = []
a = EARTH_RADIUS + (apoapsis + periapsis) / 2  # semi-major axis
period = 2 * math.pi * math.sqrt(a**3 / mu)    # orbital period in seconds
num_samples = 60  # 1 sample per minute
for i in range(num_samples):
    t = i * (period / num_samples)
    point_time = apogee_time + timedelta(seconds=t)

    # Simple circular orbit approximation
    mean_anomaly = 2 * math.pi * i / num_samples
    x = (EARTH_RADIUS + apoapsis) * math.cos(mean_anomaly)
    y = (EARTH_RADIUS + apoapsis) * math.sin(mean_anomaly)
    z = (EARTH_RADIUS + apoapsis) * math.sin(inclination) * math.sin(mean_anomaly)

    # Convert rough orbital coords to lat/lon/alt
    lon = math.degrees(math.atan2(y, x))
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    alt = math.sqrt(x**2 + y**2 + z**2) - EARTH_RADIUS

    payload_points.append({
        "time": point_time.isoformat(),
        "lat": lat,
        "lon": lon,
        "alt": alt
    })

# --- Final Data ---
data = {
    "plane": plane_points,
    "rocket": rocket_points,
    "payload": payload_points
}

with open("trajectory.json", "w") as f:
    json.dump(data, f, indent=2)

print("trajectory.json generated with plane, rocket, and satellite orbit.")
