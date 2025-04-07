import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import librosa
import xml.etree.ElementTree as ET
import os
import pathlib  # Use pathlib for better path handling
import numpy as np  # Needed for checking numpy types
from PIL import Image, ImageTk  # For loading GIF

# Utility functions for FCP time conversion
def duration_to_fcp_time(duration_seconds, fps):
    """Convert duration in seconds to FCP time format."""
    total_frames = int(round(duration_seconds * fps))
    return f"{total_frames}/{fps}s"

def seconds_to_fcp_time(seconds, fps):
    """Convert seconds to FCP time format."""
    frames = int(round(seconds * fps))
    return f"{frames}/{fps}s"

# --- Beat Detection (with HPSS Enhancement) ---
def detect_beats(audio_file):
    """Detect beats using HPSS for potentially better precision."""
    print(f"Loading audio file: {audio_file}")
    if not os.path.isfile(audio_file):
        raise FileNotFoundError(f"Audio file not found during librosa load: {audio_file}")
    try:
        # 1. Load audio with native sample rate
        y, sr = librosa.load(audio_file, sr=None)
        print(f"Audio loaded. Sample rate: {sr}, Duration: {len(y)/sr:.2f}s")
        # 2. Apply Harmonic-Percussive Source Separation (HPSS)
        print("Performing Harmonic-Percussive Source Separation (this may take a moment)...")
        y_percussive = librosa.effects.percussive(y, margin=3.0)
        print("HPSS complete.")
        # 3. Run beat tracking on the percussive component
        tempo_array, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, units='frames')
        # Extract tempo value correctly
        tempo_float = float(tempo_array.item()) if isinstance(tempo_array, np.ndarray) and tempo_array.size == 1 else float(tempo_array)
        # Convert beat frames to timestamps
        beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
        print(f"Detected {len(beat_times)} beats at {tempo_float:.2f} BPM (using HPSS)")
        return beat_times, tempo_float, sr
    except Exception as e:
        print(f"Error during beat detection for {audio_file}: {e}")
        raise


# --- FCPXML Generation ---
def create_fcp_xml(beats, audio_file_path, output_file, fps=30, audio_sr=48000):
    """Create an FCP-compatible XML file with markers"""
    audio_file = pathlib.Path(audio_file_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    audio_duration_seconds = librosa.get_duration(path=str(audio_file))
    clip_duration_fcp = duration_to_fcp_time(audio_duration_seconds, fps)
    audio_file_uri = audio_file.absolute().as_uri()

    fcpxml = ET.Element("fcpxml", version="1.10")
    resources = ET.SubElement(fcpxml, "resources")
    format_elem = ET.SubElement(resources, "format", {
        "id": "BMXRefTimelineFormat",
        "name": f"FFVideoFormat{fps}p",
        "frameDuration": f"1/{fps}s",  # Corrected frameDuration
        "width": "1920",
        "height": "1080"
    })
    asset = ET.SubElement(resources, "asset", {
        "id": "ASSET_BMXRefBetmarkedClip",
        "name": audio_file.stem,
        "start": "0/1s",
        "duration": f"{int(round(audio_duration_seconds * audio_sr))}/{audio_sr}s",
        "hasAudio": "1",
        "audioSources": "1",
        "audioChannels": "2",
        "audioRate": str(audio_sr)
    })
    media_rep = ET.SubElement(asset, "media-rep", {
        "kind": "original-media",
        "src": audio_file_uri
    })

    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", {"name": "BeatMarked Clips"})
    asset_clip = ET.SubElement(event, "asset-clip", {
        "name": audio_file.name,
        "ref": "ASSET_BMXRefBetmarkedClip",
        "offset": "0/1s",
        "duration": clip_duration_fcp,
        "format": "BMXRefTimelineFormat",
        "audioRole": "music",
        "tcFormat": "NDF"
    })

    for i, beat_time_sec in enumerate(beats):
        marker_start_fcp = seconds_to_fcp_time(beat_time_sec, fps)
        marker_duration_fcp = f"1/{fps}s"
        marker = ET.SubElement(asset_clip, "marker", {
            "start": marker_start_fcp,
            "duration": marker_duration_fcp,
            "value": f"Beat {i+1}",
            "completed": "0",
            "note": f"Beat detected at {beat_time_sec:.3f}s (HPSS)"
        })

    tree = ET.ElementTree(fcpxml)
    try:
        ET.indent(tree, space="\t", level=0)
    except AttributeError:
        pass
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"FCPXML successfully written to: {output_file}")


# --- GUI and Processing Logic ---
def process_audio():
    """Handles file selection, processing, and XML generation"""
    global is_dark_mode
    audio_file = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("Audio Files", "*.wav *.mp3 *.aif *.aiff"), ("All Files", "*.*")]
    )
    if not audio_file:
        print("No audio file selected.")
        return

    # Show loading animation
    try:
        loading_label.config(image=loading_image)
    except NameError:
        print("Loading GIF not found. Skipping animation.")
    root.update_idletasks()

    try:
        project_fps = 30.0
        beats, tempo, audio_sr = detect_beats(audio_file)
        if not beats:
            messagebox.showwarning("No Beats Found", "Beat detection did not return any beats for this file.")
            loading_label.config(image="")
            return

        # Update song info labels
        file_name_label.config(text=f"File: {pathlib.Path(audio_file).name}")
        duration_label.config(text=f"Duration: {librosa.get_duration(path=audio_file):.2f}s")
        bpm_label.config(text=f"BPM: {tempo:.1f}")
        sample_rate_label.config(text=f"Sample Rate: {audio_sr} Hz")

        output_file = filedialog.asksaveasfilename(
            title="Save FCP XML File",
            defaultextension=".fcpxml",
            initialfile=f"{pathlib.Path(audio_file).stem}_beatmap.fcpxml",
            filetypes=[("Final Cut Pro XML", "*.fcpxml"), ("All Files", "*.*")]
        )
        if not output_file:
            print("No output file selected.")
            loading_label.config(image="")
            return

        create_fcp_xml(beats, audio_file, output_file, fps=project_fps, audio_sr=audio_sr)
        messagebox.showinfo("Success", f"✅ Created {output_file}\nwith {len(beats)} markers for {project_fps}fps.")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to process audio:\n{e}")
        print(f"An unexpected error occurred during processing: {e}")
    finally:
        # Stop loading animation
        loading_label.config(image="")


def toggle_dark_mode():
    """Toggle between light and dark mode"""
    global is_dark_mode
    if is_dark_mode:
        root.configure(bg="#F5F5F7")
        label.config(bg="#F5F5F7", fg="#000000")
        subtitle.config(bg="#F5F5F7", fg="#6E6E73")
        file_name_label.config(bg="#F5F5F7", fg="#000000")
        duration_label.config(bg="#F5F5F7", fg="#000000")
        bpm_label.config(bg="#F5F5F7", fg="#000000")
        sample_rate_label.config(bg="#F5F5F7", fg="#000000")
        footer.config(bg="#F5F5F7", fg="#6E6E73")
        style.configure("Modern.TButton", background="#007AFF", foreground="white")
        is_dark_mode = False
    else:
        root.configure(bg="#1C1C1E")
        label.config(bg="#1C1C1E", fg="#FFFFFF")
        subtitle.config(bg="#1C1C1E", fg="#A5A5A7")
        file_name_label.config(bg="#1C1C1E", fg="#FFFFFF")
        duration_label.config(bg="#1C1C1E", fg="#FFFFFF")
        bpm_label.config(bg="#1C1C1E", fg="#FFFFFF")
        sample_rate_label.config(bg="#1C1C1E", fg="#FFFFFF")
        footer.config(bg="#1C1C1E", fg="#A5A5A7")
        style.configure("Modern.TButton", background="#0A84FF", foreground="white")
        is_dark_mode = True


# --- Create the GUI ---
root = tk.Tk()
root.title("Beat Marker for FCP (HPSS Enhanced)")
root.geometry("600x500")
root.configure(bg="#F5F5F7")  # Light mode background

# Custom Fonts
title_font = ("Helvetica Neue", 18, "bold")
subtitle_font = ("Helvetica Neue", 12)
label_font = ("Helvetica Neue", 10)

# Title Label
label = tk.Label(root, text="Generate Beat Markers for FCP", font=title_font, bg="#F5F5F7", fg="#000000")
label.pack(pady=20)

# Subtitle Label
subtitle = tk.Label(root, text="(HPSS Enhanced Accuracy)", font=subtitle_font, bg="#F5F5F7", fg="#6E6E73")
subtitle.pack()

# Loading Animation
try:
    loading_image = ImageTk.PhotoImage(Image.open("loading.gif"))  # Replace with your GIF file
except FileNotFoundError:
    loading_image = None
    print("Loading GIF not found. Skipping animation.")
loading_label = tk.Label(root, bg="#F5F5F7")
loading_label.pack()

# Song Info Labels
file_name_label = tk.Label(root, text="File: ", font=label_font, bg="#F5F5F7", fg="#000000")
file_name_label.pack(pady=5)
duration_label = tk.Label(root, text="Duration: ", font=label_font, bg="#F5F5F7", fg="#000000")
duration_label.pack(pady=5)
bpm_label = tk.Label(root, text="BPM: ", font=label_font, bg="#F5F5F7", fg="#000000")
bpm_label.pack(pady=5)
sample_rate_label = tk.Label(root, text="Sample Rate: ", font=label_font, bg="#F5F5F7", fg="#000000")
sample_rate_label.pack(pady=5)

# Button Style
style = ttk.Style()
style.configure("Modern.TButton", font=("Helvetica Neue", 14), background="#007AFF", foreground="white", padding=10, relief="flat")

# Main Action Button
button = ttk.Button(root, text="Select Audio & Generate Markers", style="Modern.TButton", command=process_audio)
button.pack(pady=20)

# Dark Mode Switch
is_dark_mode = False
dark_mode_button = ttk.Button(root, text="Toggle Dark Mode", style="Modern.TButton", command=toggle_dark_mode)
dark_mode_button.pack(side="bottom", pady=10)

# Footer Label
footer = tk.Label(root, text="© 2025 Beat Marker App", font=("Helvetica Neue", 10), bg="#F5F5F7", fg="#6E6E73")
footer.pack(side="bottom", pady=5)

root.mainloop()
