# Beat Marker for Final Cut Pro (HPSS Enhanced)

Beat Marker is a Python-based tool designed to automatically detect beats in audio files and generate beat markers compatible with Final Cut Pro (FCP). It uses **Harmonic-Percussive Source Separation (HPSS)** to enhance beat detection accuracy. This README provides instructions on how to install, set up, and use the program on macOS.

---

## Table of Contents

1. [Features](#features)  
2. [Requirements](#requirements)  
3. [Installation](#installation)  
4. [Usage](#usage)  
5. [Troubleshooting](#troubleshooting)  
6. [License](#license)  

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
Download the ZIP file from this Github page

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

## Acknowledgments

- **[Librosa](https://librosa.org/)**: For audio analysis and beat tracking.  
- **Tkinter**: For creating the GUI.  
- **Final Cut Pro**: For compatibility with FCPXML format.  
