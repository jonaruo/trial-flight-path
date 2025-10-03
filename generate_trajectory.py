import json
import math
from datetime import datetime, timedelta, timezone

# --- Constants ---
STARTING_AIRPORT_COORDS = {"lat": 1.12103, "lon": 104.11900}
ROCKET_RELEASE_ALTITUDE = 10000  # meters
FLIGHT_DURATION_MINUTES = 5
RETURN_DURATION_MINUTES = 5

# Rocket parameters
ROCKET_LAUNCH_ANGLE = math.radians(25)  # steep launch
ROCKET_INITIAL_VELOCITY = 5000  # m/s
G = 9.81  # gravity
ROCKET_ALTITUDE_CEILING = 200000  # meters (200 km)

# Orbit parameters (LEO demo)
EARTH_RADIUS = 6371000  # meters
ORBIT_ALTITUDE = 200000  # meters
ORBIT_PERIOD_MINUTES = 90  # typical LEO orbit
ORBIT_INCLINATION = math.radians(28.5)  # demo inclination

# --- Time Setup ---
t0 = datetime.now(timezone.utc)

# --- Plane Trajectory ---
plane_points = []
for i in range(FLIGHT_DURATION_MINUTES + 1):
    point_time = t0 + timedelta(minutes=i)
    plane_points.append({
        "time": point_time.isoformat(),
        "lat": STARTING_AIRPORT_COORDS["lat"],
        "lon": STARTING_AIRPORT_COORDS["lon"] + i * 0.05,
        "alt": i * (ROCKET_RELEASE_ALTITUDE / FLIGHT_DURATION_MINUTES)
    })

release_point = plane_points[-1]
release_time = t0 + timedelta(minutes=FLIGHT_DURATION_MINUTES)

for i in range(1, RETURN_DURATION_MINUTES + 1):
    point_time = release_time + timedelta(minutes=i)
    plane_points.append({
        "time": point_time.isoformat(),
        "lat": release_point["lat"] - i * (release_point["lat"] - STARTING_AIRPORT_COORDS["lat"]) / RETURN_DURATION_MINUTES,
        "lon": release_point["lon"] - i * (release_point["lon"] - STARTING_AIRPORT_COORDS["lon"]) / RETURN_DURATION_MINUTES,
        "alt": release_point["alt"] - i * (release_point["alt"] / RETURN_DURATION_MINUTES)
    })

# --- Rocket Trajectory with ceiling ---
rocket_points = []
payload_points = []
payload_released = False
payload_start_time = None
payload_insertion_coords = None

rocket_duration_sec = 1200  # simulate up to 20 minutes

for t in range(0, rocket_duration_sec + 1, 10):  # sample every 10s
    time = release_time + timedelta(seconds=t)
    x = ROCKET_INITIAL_VELOCITY * t * math.cos(ROCKET_LAUNCH_ANGLE)
    y = ROCKET_INITIAL_VELOCITY * t * math.sin(ROCKET_LAUNCH_ANGLE) - 0.5 * G * t**2
    alt = release_point["alt"] + y

    # Apply ceiling
    if alt > ROCKET_ALTITUDE_CEILING:
        alt = ROCKET_ALTITUDE_CEILING

    # Stop when rocket splashes down
    if alt <= 0:
        alt = 0
        break

    # Approximate lat/lon shift
    dlon = (x / (111000.0 * math.cos(math.radians(release_point["lat"])))) 

    rocket_lat = release_point["lat"]
    rocket_lon = release_point["lon"] + dlon

    rocket_points.append({
        "time": time.isoformat(),
        "lat": rocket_lat,
        "lon": rocket_lon,
        "alt": alt
    })

    # --- Trigger payload release exactly at ceiling ---
    if not payload_released and alt >= ROCKET_ALTITUDE_CEILING:
        payload_released = True
        payload_start_time = time
        payload_insertion_coords = (rocket_lat, rocket_lon)

        # Generate orbit path starting at rocket position
        orbit_period_sec = ORBIT_PERIOD_MINUTES * 60
        num_samples = 180  # 1.5 hours of orbit with 30s step
        for i in range(num_samples):
            tt = i * 30
            t_payload = payload_start_time + timedelta(seconds=tt)
            theta = 2 * math.pi * (tt / orbit_period_sec)

            r = EARTH_RADIUS + ORBIT_ALTITUDE
            lon = (payload_insertion_coords[1] + math.degrees(theta)) % 360

            payload_points.append({
                "time": t_payload.isoformat(),
                "lat": payload_insertion_coords[0],
                "lon": float(lon),
                "alt": ORBIT_ALTITUDE
            })

# --- Final Data ---
data = {
    "plane": plane_points,
    "rocket": rocket_points,
    "payload": {
        "track": payload_points,
        "orbit": {
            "inclination": math.degrees(ORBIT_INCLINATION),
            "altitude": ORBIT_ALTITUDE
        },
        "insertion_point": {
            "lat": payload_insertion_coords[0] if payload_insertion_coords else None,
            "lon": payload_insertion_coords[1] if payload_insertion_coords else None,
            "time": payload_start_time.isoformat() if payload_start_time else None
        }
    }
}

with open("trajectory.json", "w") as f:
    json.dump(data, f, indent=2)

print("trajectory.json generated.")
