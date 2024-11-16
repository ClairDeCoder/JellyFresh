import os
import logging
from datetime import datetime
from utils import parse_nfo

def process_shows(media_path, new_releases_folder, time_period):
    """
    Process TV shows and link recent seasons to the new releases folder.

    Args:
        media_path (str): Path to the TV shows library.
        new_releases_folder (str): Path to the new releases folder.
        time_period (timedelta): Time period to filter recent shows.
    """
    cutoff_date = datetime.now() - time_period
    linked_shows = set()  # To avoid duplicates

    logging.info(f"Processing TV shows from: {media_path}")
    logging.info(f"Cutoff date for new releases: {cutoff_date}")

    for root, dirs, files in os.walk(media_path):
        logging.info(f"Scanning folder: {root}")

        # Check for a TV show folder by locating tvshow.nfo
        if 'tvshow.nfo' in files:
            show_title = parse_nfo(os.path.join(root, 'tvshow.nfo'), 'title') or os.path.basename(root)
            logging.info(f"Found TV show: {show_title}")

            for season_dir in dirs:
                season_path = os.path.join(root, season_dir)

                # Check for a season.nfo in the season directory
                if 'season.nfo' in os.listdir(season_path):
                    season_title = parse_nfo(os.path.join(season_path, 'season.nfo'), 'seasonnumber') or season_dir

                    # Check all episodes in the season for aired dates
                    add_season = False
                    for episode_file in os.listdir(season_path):
                        if episode_file.lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv')):
                            episode_nfo = os.path.splitext(os.path.join(season_path, episode_file))[0] + '.nfo'
                            if os.path.exists(episode_nfo):
                                aired_date_str = parse_nfo(episode_nfo, 'aired')
                                try:
                                    aired_date = datetime.strptime(aired_date_str, '%Y-%m-%d') if aired_date_str else None
                                    if aired_date and aired_date >= cutoff_date:
                                        add_season = True
                                        break  # Stop checking after one valid episode
                                except ValueError:
                                    logging.error(f"Invalid aired date in {episode_nfo}. Skipping episode.")
                                    continue

                    if add_season:
                        # Add entire season to new releases
                        season_folder = os.path.join(new_releases_folder, show_title, f"Season {season_title}")
                        os.makedirs(season_folder, exist_ok=True)

                        for episode in os.listdir(season_path):
                            if episode.lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv')):
                                episode_file_path = os.path.join(season_path, episode)
                                episode_link = os.path.join(season_folder, episode)

                                if not os.path.exists(episode_link):
                                    os.symlink(episode_file_path, episode_link)
                                    logging.info(f"Linked {episode_file_path} to {episode_link}")

                        # Record the show and season to avoid duplicates
                        linked_shows.add(f"{show_title} - Season {season_title}")

    logging.info(f"Total shows/seasons linked: {len(linked_shows)}")
    return list(linked_shows)  # Return linked shows/seasons for the results



