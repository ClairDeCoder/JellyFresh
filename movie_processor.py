import os
import logging
from datetime import datetime
from utils import parse_nfo

def process_movies(media_path, new_releases_folder, time_period):
    """
    Process movies and link recent media to the new releases folder.

    Args:
        media_path (str): Path to the movies library.
        new_releases_folder (str): Path to the new releases folder.
        time_period (timedelta): Time period to filter recent movies.

    Returns:
        list: A list of clean movie titles that were linked.
    """
    cutoff_date = datetime.now() - time_period
    linked_movies = []  # Store clean titles of linked movies

    logging.info(f"Processing movies from: {media_path}")
    logging.info(f"Cutoff date for new releases: {cutoff_date}")

    for root, dirs, files in os.walk(media_path):
        logging.info(f"Scanning folder: {root}")
        
        for file in files:
            if file.lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv')):
                video_file = os.path.join(root, file)

                # Check for an .nfo file with the same name
                nfo_file = os.path.splitext(video_file)[0] + '.nfo'

                # If no matching NFO file, check for `movie.nfo` in the current folder
                if not os.path.exists(nfo_file):
                    nfo_file = os.path.join(root, 'movie.nfo')

                if os.path.exists(nfo_file):
                    movie_title = parse_nfo(nfo_file, 'title') or os.path.splitext(file)[0]
                    release_date_str = parse_nfo(nfo_file, 'releasedate')

                    try:
                        release_date = datetime.strptime(release_date_str, '%Y-%m-%d') if release_date_str else None
                        logging.info(f"Movie: {movie_title}, Release Date: {release_date}")
                    except ValueError:
                        logging.error(f"Invalid release date format in {nfo_file} for movie: {movie_title}")
                        continue  # Skip this movie

                    if release_date and release_date >= cutoff_date:
                        # Create a dedicated folder for the movie
                        movie_folder = os.path.join(new_releases_folder, movie_title)
                        os.makedirs(movie_folder, exist_ok=True)

                        # Create symbolic link in the movie folder
                        media_link = os.path.join(movie_folder, file)
                        if not os.path.exists(media_link):
                            os.symlink(video_file, media_link)
                            logging.info(f"Linked {video_file} to {media_link}")
                            linked_movies.append(movie_title)  # Append the clean title
                    else:
                        logging.info(f"Skipping {movie_title} - Release date not within range.")
                else:
                    logging.warning(f"No .nfo file found for {file}. Skipping.")

    logging.info(f"Total movies linked: {len(linked_movies)}")
    return linked_movies

