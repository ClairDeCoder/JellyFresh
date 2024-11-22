# JellyFresh

**JellyFresh** is a companion tool for automating and managing media organization for your Jellyfin server. It's main focus is to find the latest released movies and recently aired show episodes so they can be easily displayed on your Jellyfin homepage, within their own library. JellyFresh uses symbolic links, so no data is duplicated.
![Screenshot from 2024-11-20 00-37-43](https://github.com/user-attachments/assets/0e7224db-7358-4cce-b530-4b497d192003)

---

## 🚨 Warnings

1. **Do NOT set JellyFresh spotlight folders to the same location as your Jellyfin media folders.**
   - Doing so will result in **deletion of your entire media library**.
   - Always use a separate folder for spotlight output to avoid accidental data loss.

2. **Use JellyFresh at your own risk.**
   - While this tool is designed to simplify your media management, it performs **deletions** as part of its operations.
   - Double-check your folder configurations before running scans and enabling automation.

---

## Features

- Scan your media libraries and find newly released media for spotlighting in Jellyfin.
- Automates spotlight library updates for displaying new releases.
- Customizable scheduling (daily, weekly, or monthly).
- Supports multiple spotlight libraries and folders.
- Lightweight and easy to deploy.

---

## Installation

### Prerequisites

- Ubuntu or Debian server.
- JellyFresh needs to be able to see Jellyfin's configuration files; by sitting on the same server (recommended), OR if you share them over the network [/var/lib/jellyfin/root/default] (Not Recommended).  
**Jellyfresh looks for the full path /var/lib/jellyfin/root/default, if you're going to have it shared over the network, you must mount it to that same path on the server that JellyFresh resides.**
- Dependencies are installed using the installer.
- A Jellyfin server instance.
- The paths for your media in your Jellyfin Server configuration must be the same paths seen by JellyFresh, this is because JellyFresh reads the folder paths from Jellyfin's configuration files.  
**For Example: If Jellyfin has a Movies library at /my/media/Movies, then the viewable path by JellyFresh must also be located at /my/media/Movies. This will only be truly applicable if you're running JellyFresh on a different server, or in a different container.**  
- If the Spotlight folders you are creating are located on a CIFS drive (Windows network share), you must add mfsymlinks to the Linux server entry to allow symbolic link creation.  
An example fstab entry:  
//my-windows-IP/share-name /local/path cifs username={username},password={password},**mfsymlinks**

### High Level Steps

1. Install JellyFresh (see **Installation Methods** below), do not configure yet.
2. Create your new JellyFresh (spotlight) folder(s) **These must not be your Jellyfin media folders!**
3. Create your new library within Jellyfin: Menu > Dashboard > Libraries > "Add Media Library"
4. Select whether the library is Movies, Shows, or both.
5. Input the path to the Spotlight folder you created.
6. Repeat from steps 2-5 if you want Movies and Shows separated into their own Spotlight folders
7. Configure JellyFresh! (see **Access the Dashboard** and **Configure Spotlight Libraries** below)

### Installation Methods

#### Docker Run

**Note: The Docker set up may be more complicated to get running if you're not familiar with Docker, this is due to the nature of the application.**
**Again: If Jellyfin has a Movies library at /my/media/Movies, then the viewable path by JellyFresh must also be located at /my/media/Movies. This will only be truly applicable if you're running JellyFresh on a different server, or in a container.** 

1. Docker run command. **NOTE** For Docker, it may be best to place your spotlight folders in the same parent folder as your Jellyfin Media folders **NOT THE SAME FOLDER AS YOUR MEDIA**. This is because of volume mounting, this way it is easy for JellyFresh to see all folders with 1 volume mount. Take the example tree below:
   ```bash
   /some/folders/JellyfinMedia/
                  ├── Movies/
                  ├── Shows/
                  ├── Music/
                  ├── SpotlightMovies/
                  └── SpotlightShows/

2. This Docker run command uses the example path provided above for the spotlight libraries. Change your folder paths accordingly. **Do not** change the /var/lib folder for Jellyfin, this is used to read Jellyfin's configuration file.
   ```bash
   docker run -d \
      --name jellyfresh \
      -p 7007:7007 \
      -v /var/lib/jellyfin/root/default:/var/lib/jellyfin/root/default:ro \
      -v /some/folders/JellyfinMedia:/some/folders/JellyfinMedia \
      clairdecoder/jellyfresh:latest

3. If you do not wish to place your spotlight folders in the same parent folder as your Jellyfin Media, then you will need an extra volume mount. 1 will be for JellyFresh to read your Jellyfin Media, and the other will be used to create the links for your Spotlight media.
   ```bash
   docker run -d \
      --name jellyfresh \
      -p 7007:7007 \
      -v /var/lib/jellyfin/root/default:/var/lib/jellyfin/root/default:ro \
      -v /some/folders/JellyfinMedia:/some/folders/JellyfinMedia \
      -v /another/folder/spotlights:/another/folder/spotlights \
      clairdecoder/jellyfresh:latest

#### Docker Compose

**Please read through the instruction for Docker Run to edit the compose file as needed. Folder paths are important and depending on your setup you may need an extra volume mount!**

1. Copy the docker-compose.yml file to your server. Edit the file to suit your needs (based on the extra info provided in the Docker Run section, specifically for folder paths and/or an extra volume mount).

2. When done configuring the Volumes within the compose file, issue the compose command:
   ```bash
   docker compose up -d

#### Ubuntu/Debian Install

1. Clone the repository:
   ```bash
    git clone https://github.com/ClairDeCoder/JellyFresh.git

2. Navigate into the JellyFresh directory:
   ```bash
    cd JellyFresh

3. Make the installer executable:
   ```bash
    sudo chmod +x install.sh

4. Run the installer:
   ```bash
    sudo ./install.sh

### This Script Will

- Install necessary dependencies
- Create a no-login jellyfresh user
- Set up the jellyfresh service with systemd
- Start the JellyFresh server on port 7007

---

## Usage

## 🚨 Warnings

1. **Do NOT set JellyFresh spotlight folders to the same location as your Jellyfin media folders.**
   - Doing so will result in **deletion of your entire media library**.
   - Always use a separate folder for spotlight output to avoid accidental data loss.

2. **Use JellyFresh at your own risk.**
   - While this tool is designed to simplify your media management, it performs **deletions** as part of its operations.
   - Double-check your folder configurations before running scans and enabling automation.

### Access the Dashboard

Once installed, you can access the JellyFresh dashboard at:
- http://your-server-ip:7007
**Replace your-server-ip with the IP address of your JellyFresh server.**

### Configure Spotlight Libraries

- **DO NOT REFRESH THE PAGE WHILE THE SCAN IS BEING RAN**
- Set an automation schedule if desired, or leave as manual. Manual requires new scans to be conducted within the web interface in order to keep Spotlights updated, else they will remain (e.g. an old movie will stay within your spotlights unless deleted manually)
- Select what type of library you want to Spotlight, Movies, Shows, or both.  
**Please do not set the Spotlight library for Movies if you are linking shows and vice-versa, this can cause strange behavior and will not work, selecting "Both" works for both**
- Select the timeframe of your scan. e.g. If you only want to display movies that have been released within the past 6 months, select 6 months.  
**Note that Shows work slightly different. When scanning shows, it will look for any episodes that have aired within the timeframe. If an episode match is found, it will link the ENTIRE season that the episode is contained within, not just the episode itself.**
- Input the full path to the new Spotlight directory (this is where JellyFresh will create links, and also cleanup **[see: delete]** current links when rescanned!)  
**The Spotlight folders must exist before running the scan!**
- Add a new library if you are planning to create multiple Spotlight libraries, e.g. 1 for Movies and 1 for Shows
- Select **Save and Scan Libraries** to save the library configuration and begin a scan. If you remove a library from the web interface because you want 1 less library, you need to again select **Save and Scan Libraries** to remove the extra library from the backend configuration. The removed library will not delete the associated Spotlight folder.
- Once the scan is completed it will display which media was linked.
- You can view the most recent logs at anytime by selecting "View Logs", this will always view the most recent logs.  
**"Find" in webpage works to search the logs displayed. "Linked" will find what's been linked, "Warning" will show missing NFO files or scans on media with no NFO files, "Error" will find .NFO parsing issues.**

## 🚨 Warnings

1. **Do NOT set JellyFresh spotlight folders to the same location as your Jellyfin media folders.**  
   - Doing so will result in **deletion of your entire media library**.
   - Always use a separate folder for spotlight output to avoid accidental data loss.

2. **Use JellyFresh at your own risk.**  
   - While this tool is designed to simplify your media management, it performs **deletions** as part of its operations.
   - Double-check your folder configurations before running scans and enabling automation.

### View Logs

- The latest log is present within the web interface by selecting "View Logs"
- Logs can be viewed on the server with:
   ```bash
    journalctl -u jellyfresh
- All log files can be viewed within the log folder:
   ```bash
    /var/log/jellyfresh

### Uninstall JellyFresh

- JellyFresh comes with a built-in uninstaller:
   ```bash
    sudo chmod +x /opt/jellyfresh/uninstall.sh
    sudo /opt/jellyfresh/uninstall.sh

---

## Troubleshooting

- First check the logs for the service:
   ```bash
    journalctl -u jellyfresh

- Verify dependencies are installed on the server:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

- Verify no port conflicts, JellyFresh uses port 7007.
- Uninstall and re-install [you never know ;)]

---

## Planned Features

- Improved web UI
- Additional QOL features

---

## Contributing

Feel free to issue a PR, submit feature requests, or submit issues.

---

## Licensing

This project is licensed under the GNU General Public License V3

---

## Disclaimer

**Use at your own risk!**
- JellyFresh performs **deletions** as part of its operations. Improper configurations may result in data loss.
- Ensure all folder paths are configured correctly to avoid unintended consequences.
- **Again, DO NOT set your Spotlight libraries [see: folders] to the same as your Jellyfin media folders**

---

## Author

Developed by ClairDeCoder. For questions or support, please submit here to the repo.
