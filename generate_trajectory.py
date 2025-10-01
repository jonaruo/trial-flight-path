import json
from datetime import datetime, timedelta, timezone

# --- Constants ---
CGK_AIRPORT_COORDS = {"lat": -6.12556, "lon": 106.65583}
ROCKET_RELEASE_ALTITUDE = 10000  # meters
FLIGHT_DURATION_MINUTES = 5
RETURN_DURATION_MINUTES = 5
ROCKET_BOOST_DURATION_MINUTES = 3
ROCKET_SPLASHDOWN_DURATION_MINUTES = 5

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


# --- Rocket Trajectory ---
rocket_points = []

# 1. Boost phase
for i in range(ROCKET_BOOST_DURATION_MINUTES + 1):
    point_time = release_time + timedelta(minutes=i)
    rocket_points.append({
        "time": point_time.isoformat(),
        "lat": release_point["lat"] + i * 0.1,
        "lon": release_point["lon"] + i * 0.1,
        "alt": release_point["alt"] + i * 30000  # Climb to 100km
    })

apogee_point = rocket_points[-1]
apogee_time = release_time + timedelta(minutes=ROCKET_BOOST_DURATION_MINUTES)

# 2. Splashdown
for i in range(1, ROCKET_SPLASHDOWN_DURATION_MINUTES + 1):
    point_time = apogee_time + timedelta(minutes=i)
    rocket_points.append({
        "time": point_time.isoformat(),
        "lat": apogee_point["lat"] + i * 0.2,
        "lon": apogee_point["lon"] + i * 0.2,
        "alt": apogee_point["alt"] - i * (apogee_point["alt"] / ROCKET_SPLASHDOWN_DURATION_MINUTES)
    })
rocket_points[-1]["alt"] = 0 # Ensure it splashes down

# --- Payload ---
payload = {
    "orbit": {
        "apoapsis": 500000,
        "periapsis": 500000,
        "inclination": 28.5
    }
}

# --- Final Data ---
data = {
    "plane": plane_points,
    "rocket": rocket_points,
    "payload": payload
}

with open("trajectory.json", "w") as f:
    json.dump(data, f, indent=2)

print("trajectory.json generated with new flight paths.")