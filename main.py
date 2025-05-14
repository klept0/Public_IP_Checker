import requests
import datetime
import json
import os
import sys
import time
from apprise import Apprise

def get_public_ip():
    try:
        # Primary source: ipify
        response = requests.get("https://api.ipify.org", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except Exception:
        try:
            # Backup source: ifconfig.me
            response = requests.get("https://ifconfig.me/ip", timeout=5)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            print(f"[ERROR] Unable to retrieve public IP: {e}")
            return None

def load_heartbeat(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    now = time.time()
    return {
        "start_time": now,
        "last_ip_change": now,
        "ip_change_count": 0
    }

def save_heartbeat(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

def main(verbose=False):
    # Load config from JSON file
    with open("apprise_config.json", "r") as f:
        config = json.load(f)

    # Initialize Apprise with all URLs from config
    apobj = Apprise()
    for url in config["apprise_urls"]:
        apobj.add(url)

    # Store PreviousIP.txt and heartbeat.json in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_ip_path = os.path.join(script_dir, "PreviousIP.txt")
    heartbeat_path = os.path.join(script_dir, "heartbeat.json")

    heartbeat = load_heartbeat(heartbeat_path)
    now = time.time()

    # Heartbeat check: 30 days = 2592000 seconds
    days_since_start = (now - heartbeat["start_time"]) / 86400
    days_since_last_change = (now - heartbeat["last_ip_change"]) / 86400

    if days_since_start >= 30:
        heartbeat_message = (
            f"Heartbeat: Script has been running for {int(days_since_start)} days.\n"
            f"No IP change in {int(days_since_last_change)} days.\n"
            f"Total IP changes: {heartbeat['ip_change_count']}"
        )
        apobj.notify(
            title="Spectrum_PubIP Heartbeat",
            body=heartbeat_message
        )
        print("[HEARTBEAT] Heartbeat notification sent to Apprise URLs.")
        # Reset start_time after sending heartbeat
        heartbeat["start_time"] = now
        save_heartbeat(heartbeat_path, heartbeat)

    if verbose:
        start_time = time.time()
        elapsed = 0
        while elapsed < 300:  # 5 minutes = 300 seconds
            public_ip = get_public_ip()
            if public_ip is not None:
                print(f"[VERBOSE] Current Public IP: {public_ip}")
            else:
                print("[VERBOSE] Could not retrieve public IP.")
            time.sleep(90)
            elapsed = time.time() - start_time
        # After 5 minutes, send test message
        test_message = "Apprise Test: 5 minutes elapsed in verbose mode."
        apobj.notify(
            title="Spectrum_PubIP Test",
            body=test_message
        )
        print("[VERBOSE] Test notification sent to Apprise URLs.")
    else:
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        public_ip = get_public_ip()
        if public_ip is None:
            print("[ERROR] Could not retrieve public IP. No notification sent.")
            return
        # Read previous IP from file
        if os.path.exists(prev_ip_path):
            with open(prev_ip_path, "r") as file:
                previous_ip = file.read().strip()
        else:
            previous_ip = ""
        # If IP has changed, send notification and update file
        if public_ip != previous_ip:
            message = f"Public IP Check-In - {date}\n\n{public_ip}"
            apobj.notify(
                title="Spectrum_PubIP",
                body=message
            )
            with open(prev_ip_path, "w") as file:
                file.write(public_ip)
            # Update heartbeat info
            heartbeat["last_ip_change"] = now
            heartbeat["ip_change_count"] += 1
            save_heartbeat(heartbeat_path, heartbeat)

if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    main(verbose)