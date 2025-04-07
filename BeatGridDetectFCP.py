import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
#import librosa.display  Keep this if you plan to add plotting later
import xml.etree.ElementTree as ET
import os
import pathlib # Use pathlib for better path handling
import numpy as np # Needed for checking numpy types

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
        # This separates rhythmic (percussive) elements from tonal (harmonic) ones.
        # Beat tracking on the percussive component is often more accurate.
        print("Performing Harmonic-Percussive Source Separation (this may take a moment)...")
        # Adjust 'margin' if needed: higher values enforce stricter separation.
        y_percussive = librosa.effects.percussive(y, margin=3.0)
        print("HPSS complete.")

        # 3. Run beat tracking on the percussive component
        print("Tracking beats on percussive component...")
        # Parameters like 'tightness' or 'hop_length' could be adjusted here for further tuning:
        # e.g., tightness=150, hop_length=256
        tempo_array, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, units='frames')

        # 4. Extract the tempo value correctly
        if isinstance(tempo_array, np.ndarray) and tempo_array.size == 1:
            tempo_float = tempo_array.item()
        elif isinstance(tempo_array, (float, int)): # Handle if it's already a scalar
            tempo_float = float(tempo_array)
        else: # Fallback for unexpected format
            print(f"Warning: Unexpected tempo format: {tempo_array}. Using first element.")
            tempo_float = float(tempo_array[0]) if isinstance(tempo_array, np.ndarray) and tempo_array.size > 0 else 0.0

        # 5. Convert beat frames (indices) to timestamps (seconds)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

        print(f"Detected {len(beat_times)} beats at {tempo_float:.2f} BPM (using HPSS)")

        return beat_times, tempo_float, sr

    except Exception as e:
        print(f"Error during beat detection for {audio_file}: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        # Re-raise the exception to be caught in process_audio
        raise

# --- Time Conversion Helpers ---
def seconds_to_fcp_time(seconds, timebase=30):
    """Convert seconds to FCPXML fractional time string (e.g., '3600/30s')"""
    frames = int(round(seconds * timebase))
    return f"{frames}/{timebase}s"

def duration_to_fcp_time(duration_seconds, timebase=30):
    """Convert duration in seconds to FCPXML fractional time string"""
    total_frames = int(round(duration_seconds * timebase))
    return f"{total_frames}/{timebase}s"

# --- FCPXML Generation ---
def create_fcp_xml(beats, audio_file_path, output_file, fps=30, audio_sr=48000):
    """Create an FCP-compatible XML file with markers"""
    audio_file = pathlib.Path(audio_file_path) # Use pathlib

    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Get audio file details
    audio_name = audio_file.name
    audio_duration_seconds = librosa.get_duration(path=str(audio_file))
    audio_duration_samples = int(round(audio_duration_seconds * audio_sr))
    clip_duration_fcp = duration_to_fcp_time(audio_duration_seconds, fps)
    audio_file_uri = audio_file.absolute().as_uri()

    # --- FCPXML Structure ---
    fcpxml = ET.Element("fcpxml", version="1.10")
    resources = ET.SubElement(fcpxml, "resources")

    # Format definition
    format_elem = ET.SubElement(resources, "format", {
        "id": "BMXRefTimelineFormat",
        "name": f"FFVideoFormat{fps}p",
        "frameDuration": f"{int(1000)}/{int(fps*1000)}s",
        "width": "1920", # Assuming HD, adjust if needed
        "height": "1080"
    })

    # Asset definition
    asset_duration_fcp = f"{audio_duration_samples}/{audio_sr}s"
    audio_asset = ET.SubElement(resources, "asset", {
        "id": "ASSET_BMXRefBetmarkedClip",
        "name": audio_file.stem, # Use name without extension for asset name
        "start": "0/1s",
        "duration": asset_duration_fcp,
        "hasAudio": "1",
        "audioSources": "1",
        "audioChannels": "2", # Assuming stereo, check if mono needed
        "audioRate": str(audio_sr)
    })

    # Media representation (link to the actual file)
    media_rep = ET.SubElement(audio_asset, "media-rep", {
        "kind": "original-media",
        "src": audio_file_uri
    })

    # --- Library and Event Structure ---
    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", {
        "name": "BeatMarked Clips" # Standard event name
    })

    # Asset Clip definition (how the asset is used in the event)
    asset_clip = ET.SubElement(event, "asset-clip", {
        "name": audio_name, # Clip name can include extension
        "ref": "ASSET_BMXRefBetmarkedClip",
        "offset": "0/1s",
        "duration": clip_duration_fcp,
        "format": "BMXRefTimelineFormat",
        "audioRole": "music", # Or "dialogue", "effects"
        "tcFormat": "NDF" # Non-Drop Frame timecode
    })

    # Add markers to the asset clip
    print(f"Adding {len(beats)} markers to XML...")
    for i, beat_time_sec in enumerate(beats):
        marker_start_fcp = seconds_to_fcp_time(beat_time_sec, fps)
        marker_duration_fcp = f"1/{fps}s" # Minimal duration (1 frame)
        marker = ET.SubElement(asset_clip, "marker", {
             "start": marker_start_fcp,
             "duration": marker_duration_fcp,
             "value": f"Beat {i+1}",
             "completed": "0", # Standard attribute
             "note": f"Beat detected at {beat_time_sec:.3f}s (HPSS)" # Add note
        })

    # Write the XML to a file
    tree = ET.ElementTree(fcpxml)
    try: # Pretty print for readability (requires Python 3.9+)
        ET.indent(tree, space="\t", level=0)
    except AttributeError:
        print("ET.indent not available (requires Python 3.9+). XML will not be pretty-printed.")
        pass

    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"FCPXML successfully written to: {output_file}")

# --- GUI and Processing Logic ---
def process_audio():
    """Handles file selection, processing, and XML generation"""
    audio_file = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("Audio Files", "*.wav *.mp3 *.aif *.aiff"), ("All Files", "*.*")]
    )
    if not audio_file:
        print("No audio file selected.")
        return

    print(f"User selected: {audio_file}")

    try:
        # Define Project FPS (Important for FCPXML timing)
        # Consider making this a user input field in the GUI for flexibility
        project_fps = 30.0
        print(f"Using project FPS: {project_fps}")

        # Detect beats using the enhanced function
        beats, tempo, audio_sr = detect_beats(audio_file)

        # Check if beat detection returned results
        if not beats:
             messagebox.showwarning("No Beats Found", "Beat detection did not return any beats for this file.")
             print("Beat detection returned no results.")
             return # Stop processing if no beats found


        messagebox.showinfo(
            "Beats Detected",
            f"🎵 Detected {len(beats)} beats at {tempo:.1f} BPM\n"
            f"(Using HPSS for enhanced accuracy)\n"
            f"Audio Sample Rate: {audio_sr} Hz"
        )

        # Ask where to save the FCPXML file
        output_file = filedialog.asksaveasfilename(
            title="Save FCP XML File",
            defaultextension=".fcpxml",
            initialfile=f"{pathlib.Path(audio_file).stem}_beatmap.fcpxml",
            filetypes=[("Final Cut Pro XML", "*.fcpxml"), ("All Files", "*.*")]
        )
        if not output_file:
            print("No output file selected.")
            return

        print(f"Will save FCPXML to: {output_file}")

        # Create the FCPXML file (referencing the original audio location)
        create_fcp_xml(beats, audio_file, output_file, fps=project_fps, audio_sr=audio_sr)

        messagebox.showinfo("Success", f"✅ Created {output_file}\nwith {len(beats)} markers for {project_fps}fps.")

    except FileNotFoundError as e:
        messagebox.showerror("Error", f"❌ File Not Found:\n{e}")
        print(f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to process audio:\n{e}")
        print(f"An unexpected error occurred during processing: {e}")
        # Full traceback was already printed in detect_beats if error happened there
        # If error happened elsewhere, print it now
        if "detect_beats" not in str(e): # Avoid double printing if error was in detect_beats
             import traceback
             traceback.print_exc()

# --- Create the GUI ---
root = tk.Tk()
root.title("Beat Marker for FCP (HPSS Enhanced)")
root.geometry("450x200") # Slightly wider for new title

label = tk.Label(root, text="Generate Beat Markers for FCP\n(HPSS Enhanced Accuracy)", font=("Arial", 14))
label.pack(pady=15)

# Future enhancement: Add Entry for FPS here
# fps_label = tk.Label(root, text="Project FPS:")
# fps_label.pack()
# fps_entry = tk.Entry(root)
# fps_entry.insert(0, "30.0")
# fps_entry.pack()
# # You would then read from fps_entry in process_audio

button = tk.Button(root, text="Select Audio & Generate Markers", command=process_audio, font=("Arial", 12), padx=10, pady=5)
button.pack(pady=15)

root.mainloop()