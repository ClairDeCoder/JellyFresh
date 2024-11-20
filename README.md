# JellyFresh

**JellyFresh** is a companion tool for automating and managing media organization for your Jellyfin server. It's main focus is to find latest the released movies and recently aired show episodes so they can be easily displayed on your Jellyfin homepage, within their own library. JellyFresh uses symbolic links, so no data is duplicated.

---

## 🚨 Warnings

1. **Do NOT set JellyFresh spotlight folders to the same location as your Jellyfin media folders.**
   - Doing so will result in **deletion of your entire media library**.
   - Always use a separate folder for spotlight output to avoid accidental data loss.

2. **Use JellyFresh at your own risk.**
   - While this tool is designed to simplify your media management, it performs **deletions** as part of its operations.
   - Double-check your folder configurations before enabling running scans and enabling automation.

---

## Features

- Scan your media libraries and find newly released media for spotlighting in Jellyfin.
- Automates media library updates for displaying new releases.
- Customizable scheduling (daily, weekly, or monthly).
- Supports multiple media libraries and folders.
- Lightweight and easy to deploy.

---

## Installation

### Prerequisites

- Ubuntu or Debian server.
- JellyFresh needs to be able to see Jellyfin's configuration files; by sitting on the same server (Recommended), OR if you share them over the network [/var/lib/jellyfin/root/default] (Not Recommended).
- Dependencies are installed using the installer.
- A Jellyfin server instance.

### Steps to Install

1. Clone the repository:
   ```bash
   git clone https://github.com/ClairDeCoder/JellyFresh.git
