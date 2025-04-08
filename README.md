---

# Beat Marker for Final Cut Pro (HPSS Enhanced)

Beat Marker is a Python-based tool designed to automatically detect beats in audio files and generate beat markers compatible with Final Cut Pro (FCP). It uses **Harmonic-Percussive Source Separation (HPSS)** to enhance beat detection accuracy. This README provides instructions on how to install, set up, and use the program on macOS.

[![Release v1.0](https://img.shields.io/badge/Release-v1.0-blue)](https://github.com/spider2008/BeatMarkerFCP/releases/tag/v1.0)  
[![License](https://img.shields.io/badge/License-MIT-green)](#notice)

---

## Table of Contents

1. [Features](#features)  
2. [Requirements](#requirements)  
3. [Installation](#installation)  
4. [Usage](#usage)  
5. [Releases](#releases)  
6. [Troubleshooting](#troubleshooting)  
7. [Notice](#notice)  

---

## Features

- **Automatic Beat Detection**: Detects beats in WAV, MP3, AIFF, and other supported audio formats.  
- **HPSS Enhancement**: Improves beat detection accuracy using Harmonic-Percussive Source Separation.  
- **FCPXML Export**: Generates FCP-compatible XML files with beat markers.  
- **Dark Mode Support**: Toggle between light and dark themes for the GUI.  
- **User-Friendly Interface**: Simple and intuitive graphical interface.  

---

## Requirements

To run this program, you need the following:

- **macOS**: Tested on macOS 10.15 (Catalina) or later.  
- **Python 3.8+**: Ensure Python is installed on your system.  
- **Librosa**: For audio analysis and beat detection.  
- **Tkinter**: For the graphical user interface (usually included with Python on macOS).  
- **Pillow**: For loading GIF animations.  
- **NumPy**: Required by Librosa for numerical operations.  

---

## Installation

### Step 1: Install Python
1. Check if Python is already installed:
   ```bash
   python3 --version
   ```
   If Python is not installed, download it from the [official website](https://www.python.org/downloads/) or use Homebrew:
   ```bash
   brew install python
   ```

### Step 2: Download the Python Script
Download the ZIP file from this GitHub page:  
[Download Source Code](https://github.com/spider2008/BeatMarkerFCP/archive/refs/tags/v1.0.zip)

### Step 3: Install Dependencies
Install the required Python packages using `pip`:
```bash
pip install librosa numpy pillow tk
```

---

## Usage

### Step 1: Launch the Application
Run the program using the following command:
```bash
python BeatGridDetectFCP.py
```
A graphical window will appear.

### Step 2: Select an Audio File
1. Click the **"Select Audio & Generate Markers"** button.  
2. Choose an audio file (WAV, MP3, AIFF, etc.) from the file dialog.  

### Step 3: Review Detected Beats
Once the beats are detected:
- The **File**, **Duration**, **BPM**, and **Sample Rate** details will be displayed.  
- A loading animation will indicate progress.  

### Step 4: Save the FCPXML File
1. Choose a location and filename to save the generated `.fcpxml` file.  
2. Open the file in Final Cut Pro to view the beat markers.  

### Step 5: Toggle Dark Mode (Optional)
Click the **"Toggle Dark Mode"** button at the bottom of the window to switch between light and dark themes.  

---

## Releases

The latest stable release of **Beat Marker for FCP** is available here:

[![Release v1.0](https://img.shields.io/badge/Release-v1.0-blue)](https://github.com/spider2008/BeatMarkerFCP/releases/tag/v1.0)

### Download Links

- **macOS (.dmg)**: [Download BeatMarkerFCP_v1.0.dmg](https://github.com/spider2008/BeatMarkerFCP/releases/download/v1.0/BeatFCP.dmg)  

---

## Troubleshooting

### Issue: Missing Dependencies
If you encounter errors related to missing modules, ensure all dependencies are installed:
```bash
pip install librosa numpy pillow tk
```

### Issue: Loading GIF Not Found
If the loading animation is missing, ensure you have a `loading.gif` file in the same directory as the script. You can replace it with any GIF of your choice.

### Issue: Beat Detection Fails
- Ensure the audio file is not corrupted.  
- Try converting the file to WAV format using tools like [Audacity](https://www.audacityteam.org/).  

### Issue: FCPXML Not Compatible
Verify that the project frame rate matches the one specified in the program (default is **30 fps**).

---

### Notice

This application is provided as-is, and users are encouraged to review the following important information:

1. **Copyright and Usage**  
   - This tool is intended for personal and educational use. Users are responsible for ensuring they have the necessary rights to process any audio files uploaded to this application.  
   - The app does not redistribute or store copyrighted material. It only processes user-provided audio files temporarily for beat detection.

2. **Third-Party Libraries**  
   This project uses the following third-party libraries under their respective licenses:  
   - **[Librosa](https://librosa.org/)** (ISC License)  
   - **NumPy** (BSD License)  
   - **Pillow** (HPND License)  
   - **Tkinter** (Python Software Foundation License)  
   - Proper attribution and license details are included in the repository.

3. **Final Cut Pro Compatibility**  
   - This tool generates `.fcpxml` files compatible with Final Cut Pro. It is not affiliated with or endorsed by Apple Inc.  
   - Use of `.fcpxml` files is subject to Final Cut Pro's terms of service.

4. **Disclaimer**  
   > **Disclaimer**: This application is provided without warranty of any kind. The author(s) are not liable for any damages or issues arising from its use. Users are solely responsible for ensuring compliance with applicable laws and regulations.

5. **License**  
   This project is licensed under the [MIT License](https://github.com/spider2008/BeatMarkerFCP?tab=MIT-1-ov-file). Feel free to modify and distribute it as needed, but please include the original license and attribution.

---
