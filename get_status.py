import requests
import json
from datetime import datetime
import os
import time
import sys

STATUS_FILE = "pnr_status_history.json"
MAX_RETRIES = 5
RETRY_DELAY = 1  # seconds

# List of PNR numbers to check
PNR_LIST = [
    "8439632790",
    "8239524689"
    # Add more PNR numbers here
]

# Google Chat Webhook URL from environment variable
# To set it up:
# 1. Get webhook URL from Google Chat (see SETUP_NOTIFICATIONS.md)
# 2. Set environment variable:
#    export GOOGLE_CHAT_WEBHOOK="your_webhook_url_here"
# 3. Or add to ~/.bashrc or ~/.zshrc to make it permanent
GOOGLE_CHAT_WEBHOOK = os.environ.get("GOOGLE_CHAT_WEBHOOK", "")
def send_google_chat_notification(pnr_number, old_status, new_status, status_entry):
    """Send notification to Google Chat when status changes"""
    if not GOOGLE_CHAT_WEBHOOK:
        print("  No Google Chat webhook configured, skipping notification")
        return False

    try:
        # Prepare the message
        old_current = old_status['passenger_status'][0]['current_status'] if old_status else "N/A"
        new_current = new_status['passenger_status'][0]['current_status']

        message = {
            "text": f"🚂 *PNR Status Change Alert*\n\n"
                    f"*PNR:* {pnr_number}\n"
                    f"*Train:* {status_entry['train']}\n"
                    f"*Journey Date:* {status_entry['doj']}\n"
                    f"*Route:* {status_entry['route']}\n\n"
                    f"*Status Changed:*\n"
                    f"  Previous: {old_current}\n"
                    f"  Current: {new_current}\n\n"
                    f"*Prediction:* {new_status['passenger_status'][0]['prediction']} "
                    f"({new_status['passenger_status'][0]['prediction_percentage']}%)\n"
                    f"*Updated:* {status_entry['timestamp']}"
        }

        response = requests.post(
            GOOGLE_CHAT_WEBHOOK,
            json=message,
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            timeout=10
        )
        response.raise_for_status()
        print("  ✓ Google Chat notification sent")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to send Google Chat notification: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error preparing notification: {e}")
        return False

def has_status_changed(old_entry, new_entry):
    """Check if the status has changed between two entries"""
    if not old_entry:
        return False  # First check, no change to report

    if not old_entry.get('passenger_status') or not new_entry.get('passenger_status'):
        return False

    old_status = old_entry['passenger_status'][0]['current_status']
    new_status = new_entry['passenger_status'][0]['current_status']

    return old_status != new_status

def check_pnr_status(pnr_number):
    """Check status for a single PNR number"""
    url = f"https://cttrainsapi.confirmtkt.com/api/v2/ctpro/mweb/{pnr_number}?querysource=ct-web&locale=en&getHighChanceText=true&livePnr=false"

    payload = json.dumps({
      "proPlanName": "CP7",
      "emailId": "",
      "tempToken": ""
    })
    headers = {
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      'ApiKey': 'ct-web!2$',
      'CT-Token': '',
      'CT-Userkey': '',
      'Cache-Control': 'no-cache',
      'ClientId': 'ct-web',
      'Connection': 'keep-alive',
      'Content-Type': 'application/json',
      'DeviceId': 'd7369386-46dc-4e87-830c-f7653b2b8551',
      'Origin': 'https://www.confirmtkt.com',
      'Pragma': 'no-cache',
      'Referer': 'https://www.confirmtkt.com/',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-site',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
      'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'Cookie': '__cf_bm=LRL94MCRJlZ9moqk9e4CEW51fJlty0vi5cZ7a6EMJk8-1761294260-1.0.1.1-HH2636_qIb67Vt746QM1RwUorAbKIDwA7Z7rIcv6hvBa9ixJ0_Q5HMx4_S4hLg6U3QW.QIl3bz9.9o5_cyi.IGkDhgHlmQ6YrfsZ2CX8Xok; _cfuvid=NXzs5SlOUseH4IU0Jo.xVzHIM9RnlvUqUb6YOrwKnSE-1761292980783-0.0.1.1-604800000'
    }

    # Retry logic to handle API inconsistency
    data = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  Attempt {attempt}/{MAX_RETRIES}...", end=" ")
            response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors

            data = response.json()
            pnr_response = data.get('data', {}).get('pnrResponse', {})

            # Check if we got a valid response (not "Invalid PNR" error)
            if not pnr_response.get('error'):
                print("Success!")
                return data
            else:
                print(f"Got error: {pnr_response.get('error')}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"  Failed after {MAX_RETRIES} attempts: {pnr_response.get('error')}")
                    return None

        except requests.exceptions.Timeout:
            print("Request timed out")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  Failed after {MAX_RETRIES} attempts due to timeout")
                return None

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  Failed after {MAX_RETRIES} attempts due to connection error")
                return None

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None

        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  Failed after {MAX_RETRIES} attempts due to invalid JSON")
                return None

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    return None

# Load existing data
try:
    status_data = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status_data = json.load(f)
except json.JSONDecodeError as e:
    print(f"Warning: Could not parse existing status file: {e}")
    print("Starting with empty data")
    status_data = {}
except Exception as e:
    print(f"Error reading status file: {e}")
    sys.exit(1)

# Check status for each PNR
print(f"Checking {len(PNR_LIST)} PNR(s)...\n")
successful_checks = 0
failed_checks = 0

for pnr_number in PNR_LIST:
    print(f"Checking PNR: {pnr_number}")
    data = check_pnr_status(pnr_number)

    if not data:
        print(f"  Failed to fetch status for PNR {pnr_number}\n")
        failed_checks += 1
        continue

    # Extract status information
    pnr_response = data.get('data', {}).get('pnrResponse', {})

    try:
        status_entry = {
            "timestamp": datetime.now().isoformat(),
            "train": f"{pnr_response.get('trainNo')} {pnr_response.get('trainName')}",
            "doj": pnr_response.get('doj'),
            "route": f"{pnr_response.get('sourceName')} → {pnr_response.get('destinationName')}",
            "departure": pnr_response.get('departureTime'),
            "passenger_status": []
        }

        passenger_list = pnr_response.get('passengerStatus', [])
        if not passenger_list:
            print("  Warning: No passenger status information available")

        for passenger in passenger_list:
            status_entry["passenger_status"].append({
                "number": passenger.get('number'),
                "booking_status": passenger.get('bookingStatus'),
                "current_status": passenger.get('currentStatus'),
                "prediction": passenger.get('prediction'),
                "prediction_percentage": passenger.get('predictionPercentage')
            })

        # Check if status has changed
        old_entry = status_data.get(pnr_number)
        status_changed = has_status_changed(old_entry, status_entry)

        # Update status for this PNR (overwrites previous entry)
        status_data[pnr_number] = status_entry

        print(f"  Status updated at {status_entry['timestamp']}")
        if status_entry['passenger_status']:
            print(f"  Current Status: {status_entry['passenger_status'][0]['current_status']}")
            print(f"  Prediction: {status_entry['passenger_status'][0]['prediction']} ({status_entry['passenger_status'][0]['prediction_percentage']}%)")

        # Send notification if status changed
        if status_changed:
            print("  🔔 Status has changed!")
            send_google_chat_notification(pnr_number, old_entry, status_entry, status_entry)
        else:
            print("  No change in status")

        print()
        successful_checks += 1

    except Exception as e:
        print(f"  Error processing status for PNR {pnr_number}: {e}\n")
        failed_checks += 1
        continue

# Save updated data
try:
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_data, f, indent=2)
    print(f"Summary: {successful_checks} successful, {failed_checks} failed")
    print(f"Status saved to {STATUS_FILE}")
except Exception as e:
    print(f"Error saving status file: {e}")
    sys.exit(1)

