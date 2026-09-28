import os
import subprocess
import time
import sys
from datetime import datetime, timezone
from suntime import Sun

# --- CONFIGURATION FALLBACKS ---
DEFAULT_LATITUDE = 49.7333
DEFAULT_LONGITUDE = 11.1500
CHECK_INTERVAL_SECONDS = 300
# -------------------------------

def set_theme(mode):
    """Modes: 'prefer-dark' or 'prefer-light'"""
    try:
        cmd = ["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", mode]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Failed to set theme: {e}", file=sys.stderr)

def main():
    # Read environment variables and safely convert to float
    try:
        latitude = float(os.environ.get("LOCATION_LATITUDE", DEFAULT_LATITUDE))
        longitude = float(os.environ.get("LOCATION_LONGITUDE", DEFAULT_LONGITUDE))
    except ValueError:
        print("Invalid coordinates in environment variables. Falling back to defaults.", file=sys.stderr)
        latitude = DEFAULT_LATITUDE
        longitude = DEFAULT_LONGITUDE

    sun = Sun(latitude, longitude)
    
    while True:
        now_utc = datetime.now(timezone.utc)
        try:
            sunrise = sun.get_local_sunrise_time(now_utc).astimezone(timezone.utc)
            sunset = sun.get_local_sunset_time(now_utc).astimezone(timezone.utc)
            
            if sunrise <= now_utc < sunset:
                set_theme("prefer-light")
            else:
                set_theme("prefer-dark")
        except Exception as e:
            print(f"Error calculating sun times: {e}", file=sys.stderr)
            
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
