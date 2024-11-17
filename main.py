from flask import Flask, request, jsonify, render_template
import os
import logging
from datetime import timedelta, datetime
from logging_setup import setup_logging
from config_handler import load_config, save_config
from movie_processor import process_movies
from show_processor import process_shows
from utils import clean_new_releases_folder, get_jellyfin_media_paths

# Flask app setup
app = Flask(__name__)

# Paths
CONFIG_FILE = '/var/lib/jellyfin/new_releases_config.json'
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


@app.route('/')
def home():
    """Render the home page with current config values."""
    setup_logging(LOG_DIR)

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
        })
        return jsonify(scheduler)

    elif request.method == 'POST':
        # Update the scheduler settings
        mode = request.form.get("mode", "manual")
        frequency = request.form.get("frequency", "weekly")
        time = request.form.get("time", "02:00")

        # Update the configuration
        config["automation"] = {
            "mode": mode,
            "frequency": frequency,
            "time": time,
        }
        save_config(CONFIG_FILE, config)

        # Calculate and return the next scheduled scan time (if in automatic mode)
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

            next_scan = next_scan.replace(hour=int(time.split(":")[0]), minute=int(time.split(":")[1]), second=0)
            return jsonify({"message": "Settings saved successfully", "next_scan": next_scan.isoformat()})

        return jsonify({"message": "Settings saved successfully", "next_scan": None})



@app.route('/libraries', methods=['GET'])
def get_libraries():
    """Return the existing libraries from the configuration file."""
    config = load_config(CONFIG_FILE)
    return jsonify(config.get('libraries', []))



@app.route('/new_releases', methods=['POST'])
def new_releases():
    """Handle the form submission and process the libraries."""
    config = load_config(CONFIG_FILE)  # Load existing config
    jellyfin_media_paths = get_jellyfin_media_paths(JELLYFIN_CONFIG_PATH)
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

    # Debugging logs for movies and shows
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
    app.run(host='0.0.0.0', port=5000, debug=True)
