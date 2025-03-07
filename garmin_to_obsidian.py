from datetime import datetime, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin
import os

# --- Load environment variables ---
load_dotenv()

OBS_PATH = os.getenv("OBS_PATH")  # Path to Obsidian Journal
email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")
print(OBS_PATH,email,password)

# --- Authenticate Garmin API ---
client = Garmin(email, password)
client.login()

# --- Set date variables for yesterday ---
today = datetime.today()
yesterday = today - timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")
year = yesterday.strftime("%Y")
month = yesterday.strftime("%m")

# --- Define Obsidian daily note path ---
note_path = os.path.expanduser(f"{OBS_PATH}/{year}/{month}/{date_str}.md")


# --- Helper Functions ---
def format_time(timestamp):
    """Convert Garmin timestamp (milliseconds) to HH:MM format."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M")


def format_hours(seconds):
    """Convert seconds to hours with 2 decimal places."""
    return f"{seconds / 3600:.2f}h"


def format_obsidian_tag(value):
    """Ensure numbers in Obsidian tags have no decimals or commas."""
    if isinstance(value, float):
        return str(int(round(value)))  # Convert float to int
    return str(value)


def format_timestamp(timestamp):
    """Convert ISO 8601 timestamps (YYYY-MM-DDTHH:MM:SS.sss) to HH:MM format."""
    try:
        parsed_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        return parsed_time.strftime("%H:%M")
    except (ValueError, TypeError):
        return "N/A"


# --- Fetch Sleep Data ---
print(f"🤖 Fetching Garmin Sleep Data for {date_str}")
sleep_data = client.get_sleep_data(date_str).get("dailySleepDTO", {})

quality = sleep_data.get("sleepScores", {}).get("overall", {}).get("qualifierKey", "N/A")

sleep_logs = [
    f"log-sleep-hours:: {format_hours(sleep_data.get('sleepTimeSeconds', 0))}",
    f"log-sleep-score:: {sleep_data.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')} ({quality})",
    f"log-sleep-deep:: {format_hours(sleep_data.get('deepSleepSeconds', 0))}",
    f"log-sleep-light:: {format_hours(sleep_data.get('lightSleepSeconds', 0))}",
    f"log-sleep-rem:: {format_hours(sleep_data.get('remSleepSeconds', 0))}",
    f"log-bed-time:: {format_time(sleep_data.get('sleepStartTimestampLocal', None))}",
    f"log-wake-up-time:: {format_time(sleep_data.get('sleepEndTimestampLocal', None))}"
]

print("🤖 Sleep logs:")
for log in sleep_logs:
    print(log)


# --- Fetch Activity Data ---
print(f"\n🤖 Fetching Garmin activities for {date_str}")
activities = client.get_activities_fordate(date_str)

exercise_logs = []
for activity in activities["ActivitiesForDay"]["payload"]:
    activity_type = activity.get("activityType", {}).get("typeKey", "unknown").lower()
    name = activity.get("activityName", "Unnamed Activity")
    distance = format_obsidian_tag(activity.get("distance", 0) / 1000)  # Convert meters to km
    duration = format_obsidian_tag(activity.get("duration", 0) / 60)  # Convert seconds to minutes
    start_time = format_timestamp(activity.get("startTimeGMT", None))
    avg_hr = format_obsidian_tag(activity.get("averageHR", "N/A"))
    calories = format_obsidian_tag(activity.get("calories", "N/A"))

    # Handle activity-specific metrics
    if activity_type == "running":
        avg_pace = activity.get("averageSpeed", 0)
        avg_pace = format_obsidian_tag(1000 / (avg_pace * 60)) if avg_pace > 0 else "N/A"  # Convert m/s to min/km
        log_entry = f"{start_time}\n- [ ] {name} #log/exercise/{activity_type} #distance/{distance}km #duration/{duration}min #avgPace/{avg_pace}min/km #avgHR/{avg_hr}bpm #calories/{calories}"

    elif activity_type == "lacrosse":
        log_entry = f"{start_time}\n- [ ] {name} #log/exercise/{activity_type} #distance/{distance}km #duration/{duration}min #avgHR/{avg_hr}bpm #calories/{calories}"

    elif activity_type == "yoga":
        log_entry = f"{start_time}\n- [ ] {name} #log/exercise/{activity_type} #duration/{duration}min #avgHR/{avg_hr}bpm #calories/{calories}"

    elif activity_type == "strength_training":
        sets = format_obsidian_tag(activity.get("activeSets", "N/A"))
        log_entry = f"{start_time}\n- [ ] {name} #log/exercise/{activity_type} #sets/{sets} #duration/{duration}min #avgHR/{avg_hr}bpm #calories/{calories}"

    else:
        log_entry = f"{start_time}\n- [ ] {name} #log/exercise/{activity_type} #duration/{duration}min #calories/{calories}"

    exercise_logs.append(log_entry)

print("🤖 Exercise logs:")
for exercise in exercise_logs:
    print(exercise)


# --- Append Data to Obsidian Note ---
if exercise_logs or sleep_logs:
    print(f"🤖 Checking if daily note exists: {note_path}")

    # Read existing note content (or create new)
    if os.path.exists(note_path):
        with open(note_path, "r", encoding="utf-8") as file:
            note_content = file.readlines()
    else:
        note_content = []

    # --- Insert Sleep Logs ---
    try:
        log_index = note_content.index("### Log morning\n") + 1
    except ValueError:
        note_content.append("\n### Log morning\n")
        log_index = len(note_content)

    print("🤖 Adding sleep logs to daily note")
    note_content.insert(log_index, "\n".join(sleep_logs) + "\n")

    # --- Insert Exercise Logs ---
    try:
        exercise_index = note_content.index("### 👟 Exercise\n") + 1
    except ValueError:
        note_content.append("\n### 👟 Exercise\n")
        exercise_index = len(note_content)

    print("🤖 Adding exercise logs to daily note")
    note_content.insert(exercise_index, "\n".join(exercise_logs) + "\n")

    # --- Write Back to File ---
    with open(note_path, "w", encoding="utf-8") as file:
        file.writelines(note_content)

    print(f"🤖 ✅ Workout and sleep data added to {note_path}")
else:
    print(f"🤖 ❌ No data found for {date_str}.")
