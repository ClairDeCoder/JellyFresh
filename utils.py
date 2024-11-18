import os
import xml.etree.ElementTree as ET
import logging
import shutil


def get_jellyfin_media_paths(base_config_path):
    """
    Parse Jellyfin's configuration files to dynamically retrieve media library paths.
    
    Args:
        base_config_path (str): Base path to the Jellyfin configuration, e.g., /var/lib/jellyfin/root/default/

    Returns:
        dict: A dictionary with keys 'movies' and 'shows', containing lists of paths.
    """
    media_paths = {"movies": [], "shows": []}

    # Define the directories to look for options.xml
    categories = {"movies": "Movies", "shows": "Shows"}
    for category, subfolder in categories.items():
        options_file = os.path.join(base_config_path, subfolder, "options.xml")

        if not os.path.exists(options_file):
            logging.warning(f"Missing options.xml for {category}: {options_file}")
            continue

        try:
            tree = ET.parse(options_file)
            root = tree.getroot()

            # Extract all paths under <PathInfos>/<MediaPathInfo>/<Path>
            for path_element in root.findall(".//PathInfos/MediaPathInfo/Path"):
                if path_element.text:
                    media_paths[category].append(path_element.text)
                    logging.info(f"Found {category} path: {path_element.text}")
        except (ET.ParseError, FileNotFoundError) as e:
            logging.error(f"Error reading {options_file}: {e}")

    return media_paths

def parse_nfo(nfo_path, tag):
    """
    Parse an .nfo file and extract the value of a specific XML tag.
    
    Args:
        nfo_path (str): Path to the .nfo file.
        tag (str): The XML tag to search for (e.g., 'title', 'releasedate').
    
    Returns:
        str: The text content of the specified tag, or None if not found.
    """
    try:
        # Parse the .nfo file as XML
        tree = ET.parse(nfo_path)
        root = tree.getroot()

        # Find the tag and return its text content
        element = root.find(tag)
        if element is not None:
            return element.text.strip()
        else:
            logging.warning(f"Tag <{tag}> not found in {nfo_path}.")
            return None
    except ET.ParseError as e:
        logging.error(f"Error parsing {nfo_path}: {e}")
        return None
    except FileNotFoundError:
        logging.error(f".nfo file not found: {nfo_path}")
        return None

def clean_new_releases_folder(folder_path):
    """
    Clean the specified folder by removing all its contents.
    
    Args:
        folder_path (str): Path to the folder to clean.
    """
    if not os.path.exists(folder_path):
        logging.warning(f"Folder {folder_path} does not exist. Skipping cleanup.")
        return

    logging.info(f"Cleaning folder: {folder_path}")
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories
                logging.info(f"Removed directory: {item_path}")
            else:
                os.remove(item_path)  # Remove files
                logging.info(f"Removed file: {item_path}")
        except Exception as e:
            logging.error(f"Failed to remove {item_path}: {e}")

