from flask import Flask, request, jsonify, render_template
import os
import logging
from datetime import timedelta, datetime
from logging_setup import setup_logging
from config_handler import load_config, save_config
from movie_processor import process_movies
from show_processor import process_shows
from utils import clean_new_releases_folder, get_jellyfin_media_paths
import glob
import schedule
import time
from threading import Thread
import requests

# Flask app setup
app = Flask(__name__)

# Paths
CONFIG_FILE = '/opt/jellyfresh/new_releases_config.json'
JELLYFIN_CONFIG_PATH = '/var/lib/jellyfin/root/default/'
LOG_DIR = '/var/log/jellyfin_new_releases'

# Define time periods
PERIODS = {
    '1_week': timedelta(weeks=1),
    '2_weeks': timedelta(weeks=2),
    '1_month': timedelta(days=30),
    '2_months': timedelta(days=60),
    '6_months': timedelta(days=182),
    '1_year': timedelta(days=365)
}

# Scheduler setup
def trigger_scan():
    """Trigger the /new_releases scan."""
    app.logger.info("Triggering scheduled scan...")
    try:
        response = requests.post("http://127.0.0.1:7007/new_releases")
        if response.status_code == 200:
            app.logger.info("Scheduled scan completed successfully.")
        else:
            app.logger.error(f"Scheduled scan failed with status code: {response.status_code}")
    except Exception as e:
        app.logger.error(f"Error during scheduled scan: {e}")

def setup_automation():
    """Set up automated scanning based on the configuration."""
    config = load_config(CONFIG_FILE)
    automation = config.get("automation", {})
    
    if automation.get("mode") == "automatic":
        frequency = automation.get("frequency", "daily").lower()
        time_str = automation.get("time", "02:00")

        # Clear existing jobs
        schedule.clear()

        # Helper function to calculate weekly or monthly intervals
        def conditional_trigger(interval_days):
            last_run_key = "last_run"
            last_run_date = automation.get(last_run_key)
            
            if last_run_date:
                last_run_date = datetime.fromisoformat(last_run_date)
                if datetime.now() < last_run_date + timedelta(days=interval_days):
                    return  # Skip this run
            
            # Run the scan and update the last run time
            trigger_scan()
            automation[last_run_key] = datetime.now().isoformat()
            save_config(CONFIG_FILE, config)

        # Schedule the job
        if frequency == "daily":
            schedule.every().day.at(time_str).do(trigger_scan)
        elif frequency == "weekly":
            schedule.every().day.at(time_str).do(lambda: conditional_trigger(7))
        elif frequency == "monthly":
            schedule.every().day.at(time_str).do(lambda: conditional_trigger(30))

        app.logger.info(f"Automation set to {frequency} at {time_str}.")


def run_scheduler():
    """Run the scheduler loop in a separate thread."""
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start scheduler thread
scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


@app.route('/')
def home():
    """Render the home page with current config values."""
    config = load_config(CONFIG_FILE)
    return render_template(
        'index.html',
        libraries=config.get('libraries', []),
        periods=PERIODS.keys(),
    )


@app.route('/scheduler', methods=['GET', 'POST'])
def scheduler():
    """Handle both fetching and updating scheduler settings."""
    config = load_config(CONFIG_FILE)

    if request.method == 'GET':
        # Fetch and return the current scheduler settings
        scheduler = config.get("automation", {
            "mode": "manual",
            "frequency": "weekly",
            "time": "02:00",
            "next_scan": None
        })
        return jsonify(scheduler)

    elif request.method == 'POST':
        # Update the scheduler settings
        mode = request.form.get("mode", "manual")
        frequency = request.form.get("frequency", "weekly")
        time = request.form.get("time", "02:00")

        # Calculate the next scan time if in automatic mode
        next_scan = None
        if mode == "automatic":
            now = datetime.now()
            if frequency == "daily":
                next_scan = now + timedelta(days=1)
            elif frequency == "weekly":
                next_scan = now + timedelta(weeks=1)
            elif frequency == "monthly":
                next_scan = now + timedelta(weeks=4)
            else:
                return jsonify({"error": "Invalid frequency"}), 400

            # Set the time for the next scan
            next_scan = next_scan.replace(hour=int(time.split(":")[0]), minute=int(time.split(":")[1]), second=0)

        # Update the configuration
        config["automation"] = {
            "mode": mode,
            "frequency": frequency,
            "time": time,
            "next_scan": next_scan.isoformat() if next_scan else None
        }
        save_config(CONFIG_FILE, config)

        # Reinitialize automation
        setup_automation()

        return jsonify({
            "message": "Settings saved successfully",
            "next_scan": next_scan.isoformat() if next_scan else None
        })


@app.route('/logs/recent', methods=['GET'])
def get_recent_log():
    """Serve the most recent log file's content."""
    try:
        # Find the most recent log file
        log_files = sorted(glob.glob(os.path.join(LOG_DIR, "jellyfin_new_releases_*.log")), reverse=True)
        if not log_files:
            return jsonify({"error": "No log files found."}), 404

        most_recent_log = log_files[0]

        # Read and return the log content
        with open(most_recent_log, 'r') as log_file:
            log_content = log_file.read()

        return log_content, 200

    except Exception as e:
        app.logger.error(f"Error fetching logs: {e}")
        return jsonify({"error": "Failed to fetch logs."}), 500


@app.route('/libraries', methods=['GET'])
def get_libraries():
    """Return the existing libraries from the configuration file."""
    config = load_config(CONFIG_FILE)
    return jsonify(config.get('libraries', []))


@app.route('/new_releases', methods=['POST'])
def new_releases():
    """Handle the form submission and process the libraries."""
    config = load_config(CONFIG_FILE)
    jellyfin_media_paths = get_jellyfin_media_paths(JELLYFIN_CONFIG_PATH)
    setup_logging(LOG_DIR)
    new_libraries = []  # Temporarily store the updated library list
    linked_movies = []  # Collect movie titles
    linked_shows = []   # Collect show titles

    library_count = int(request.form.get('library_count', 1))

    for i in range(1, library_count + 1):
        media_type = request.form.get(f'media_type-{i}')
        period_key = request.form.get(f'period-{i}')
        time_period = PERIODS.get(period_key, timedelta(days=30))
        new_releases_folder = request.form.get(f'new_releases_folder-{i}')

        if not os.path.exists(new_releases_folder):
            return jsonify({"error": f"New releases folder '{new_releases_folder}' does not exist."}), 400

        if media_type in ['movies', 'both']:
            for movie_path in jellyfin_media_paths['movies']:
                new_libraries.append({
                    'media_type': 'movies',
                    'time_period': time_period.total_seconds(),
                    'media_path': movie_path,
                    'new_releases_folder': new_releases_folder
                })

        if media_type in ['shows', 'both']:
            for show_path in jellyfin_media_paths['shows']:
                new_libraries.append({
                    'media_type': 'shows',
                    'time_period': time_period.total_seconds(),
                    'media_path': show_path,
                    'new_releases_folder': new_releases_folder
                })

    # Update configuration with new libraries
    config['libraries'] = new_libraries
    save_config(CONFIG_FILE, config)

    # Process each library and collect results
    for library in new_libraries:
        media_type = library['media_type']
        time_period = timedelta(seconds=library['time_period'])
        media_path = library['media_path']
        new_releases_folder = library['new_releases_folder']

        clean_new_releases_folder(new_releases_folder)
        if media_type == 'movies':
            linked = process_movies(media_path, new_releases_folder, time_period)
            linked_movies.extend(linked)
        elif media_type == 'shows':
            linked = process_shows(media_path, new_releases_folder, time_period)
            linked_shows.extend(linked)

    app.logger.info(f"Linked movies: {linked_movies}")
    app.logger.info(f"Linked shows: {linked_shows}")

    if not linked_movies and not linked_shows:
        return jsonify({"results": {"movies": [], "shows": []}, "message": "No new media linked."})

    return jsonify({
        "results": {
            "movies": linked_movies,
            "shows": linked_shows
        },
        "message": "Scan completed successfully."
    })


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred."}), 500


if __name__ == '__main__':
    setup_automation()
    app.run(host='0.0.0.0', port=7007, debug=True) #### REMOVE
