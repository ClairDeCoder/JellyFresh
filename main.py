from flask import Flask, request, jsonify, render_template
import os
import logging
from datetime import timedelta
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
NEW_RELEASES_BASE = '/newreleases'  # Default base path for new releases

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
        new_releases_base=NEW_RELEASES_BASE
    )


@app.route('/new_releases', methods=['POST'])
def new_releases():
    """Handle the form submission and process the libraries."""
    jellyfin_media_paths = get_jellyfin_media_paths(JELLYFIN_CONFIG_PATH)
    libraries = []
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
                libraries.append({
                    'media_type': 'movies',
                    'time_period': time_period,
                    'media_path': movie_path,
                    'new_releases_folder': new_releases_folder
                })

        if media_type in ['shows', 'both']:
            for show_path in jellyfin_media_paths['shows']:
                libraries.append({
                    'media_type': 'shows',
                    'time_period': time_period,
                    'media_path': show_path,
                    'new_releases_folder': new_releases_folder
                })

    # Process each library and collect results
    for library in libraries:
        media_type = library['media_type']
        time_period = library['time_period']
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
