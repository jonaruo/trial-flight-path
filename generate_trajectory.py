import json
import math
from datetime import datetime, timedelta, timezone

# --- Constants ---
CGK_AIRPORT_COORDS = {"lat": -6.12556, "lon": 106.65583}
ROCKET_RELEASE_ALTITUDE = 10000  # meters
FLIGHT_DURATION_MINUTES = 5
RETURN_DURATION_MINUTES = 5

# Rocket parameters
ROCKET_LAUNCH_ANGLE = math.radians(45)  # launch at 45 degrees
ROCKET_INITIAL_VELOCITY = 3000  # m/s (demo scale)
G = 9.81  # gravity

# Orbit parameters (LEO demo)
EARTH_RADIUS = 6371000  # meters
ORBIT_ALTITUDE = 500000  # meters
ORBIT_PERIOD_MINUTES = 90  # typical LEO orbit
ORBIT_INCLINATION = math.radians(28.5)  # demo inclination

# --- Time Setup ---
t0 = datetime.now(timezone.utc)

# --- Plane Trajectory ---
plane_points = []

# 1. Takeoff from CGK and climb to release point
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

# 2. Return to CGK
for i in range(1, RETURN_DURATION_MINUTES + 1):
    point_time = release_time + timedelta(minutes=i)
    plane_points.append({
        "time": point_time.isoformat(),
        "lat": release_point["lat"] - i * (release_point["lat"] - CGK_AIRPORT_COORDS["lat"]) / RETURN_DURATION_MINUTES,
        "lon": release_point["lon"] - i * (release_point["lon"] - CGK_AIRPORT_COORDS["lon"]) / RETURN_DURATION_MINUTES,
        "alt": release_point["alt"] - i * (release_point["alt"] / RETURN_DURATION_MINUTES)
    })

# --- Rocket Trajectory (parabolic) ---
rocket_points = []
rocket_duration_sec = 300  # simulate for 5 minutes

for t in range(0, rocket_duration_sec + 1, 10):  # sample every 10s
    time = release_time + timedelta(seconds=t)
    x = ROCKET_INITIAL_VELOCITY * t * math.cos(ROCKET_LAUNCH_ANGLE)
    y = ROCKET_INITIAL_VELOCITY * t * math.sin(ROCKET_LAUNCH_ANGLE) - 0.5 * G * t**2
    alt = release_point["alt"] + max(y, 0)

    # project x distance into lat/lon offset (simplified flat Earth)
    dlat = (x / 111000.0)  # 1 degree ~111 km
    dlon = (x / (111000.0 * math.cos(math.radians(release_point["lat"]))))
    
    rocket_points.append({
        "time": time.isoformat(),
        "lat": release_point["lat"] + dlat,
        "lon": release_point["lon"] + dlon,
        "alt": alt
    })

# --- Payload Orbit ---
payload_points = []
orbit_period_sec = ORBIT_PERIOD_MINUTES * 60
num_samples = 180  # 1.5 hours of orbit with 30s step

for i in range(num_samples):
    t = i * 30  # seconds
    time = release_time + timedelta(seconds=t)

    # Angular velocity
    theta = 2 * math.pi * (t / orbit_period_sec)

    # Orbital coordinates (simplified circular orbit)
    r = EARTH_RADIUS + ORBIT_ALTITUDE
    lat = ORBIT_INCLINATION * math.sin(theta)  # vary with inclination
    lon = (release_point["lon"] + math.degrees(theta)) % 360
    alt = ORBIT_ALTITUDE

    payload_points.append({
        "time": time.isoformat(),
        "lat": float(lat),
        "lon": float(lon),
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

print("trajectory.json generated with parabolic rocket and orbital payload.")
