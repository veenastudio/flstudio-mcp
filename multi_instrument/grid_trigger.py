import mido
from mido import Message
import time
import os

# Constants for channel assignments
DRUMS_CHANNEL = 0
KICK_CHANNEL = 1
SNARE_CHANNEL = 2
HATS_CHANNEL = 3
BASS_CHANNEL = 4
KEYS_CHANNEL = 6
LEAD_CHANNEL = 8

# Dictionary to map MIDI channels to FL Studio channels
midi_to_fl_channel_map = {
    0: DRUMS_CHANNEL,
    1: KICK_CHANNEL,
    2: SNARE_CHANNEL,
    3: HATS_CHANNEL,
    4: BASS_CHANNEL,
    5: KEYS_CHANNEL,
    6: LEAD_CHANNEL
}

# MIDI Notes for instrument sounds (General MIDI standard)
KICK = 36      # C1
SNARE = 38     # D1
CLAP = 39      # D#1
CLOSED_HAT = 42  # F#1
OPEN_HAT = 46  # A#1

# Dictionary of note names to MIDI values
note_to_midi = {
    "C3": 48, "C#3": 49, "D3": 50, "D#3": 51, "E3": 52, "F3": 53, "F#3": 54, 
    "G3": 55, "G#3": 56, "A3": 57, "A#3": 58, "B3": 59,
    "C4": 60, "C#4": 61, "D4": 62, "D#4": 63, "E4": 64, "F4": 65, "F#4": 66, 
    "G4": 67, "G#4": 68, "A4": 69, "A#4": 70, "B4": 71,
    "C5": 72, "C#5": 73, "D5": 74, "D#5": 75, "E5": 76, "F5": 77, "F#5": 78, 
    "G5": 79, "G#5": 80, "A5": 81, "A#5": 82, "B5": 83,
    "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65, "F#": 66, 
    "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
}

# Dictionary of chord types
chord_dictionary = {
    "maj": [0, 4, 7],       # Major: root, major third, perfect fifth
    "min": [0, 3, 7],       # Minor: root, minor third, perfect fifth
    "maj7": [0, 4, 7, 11],  # Major 7th: major + major seventh
    "min7": [0, 3, 7, 10],  # Minor 7th: minor + minor seventh
    "7": [0, 4, 7, 10],     # Dominant 7th: major + minor seventh
}

def connect_to_fl_studio():
    """Connect to FL Studio via MIDI port"""
    print("Connecting to FL Studio...")
    
    # Common port names
    port_names = [
        'FL STUDIO MIDI',  # Windows common name
        'To FL STUDIO MIDI',
        'MIDI In',
        'IAC Driver Bus 1',  # Mac default
        'loopMIDI Port'  # loopMIDI virtual port
    ]
    
    # Try to connect to any of the predefined ports
    for port_name in port_names:
        try:
            output_port = mido.open_output(port_name)
            print(f"Successfully connected to {port_name}")
            return output_port
        except:
            continue
    
    # If predefined ports fail, show available ports and ask for manual selection
    print("Could not connect to default ports. Available ports:")
    available_ports = mido.get_output_names()
    
    for i, port in enumerate(available_ports):
        print(f"  {i}: {port}")
    
    if not available_ports:
        print("No MIDI ports found. Please make sure FL Studio is running and MIDI is properly configured.")
        return None
    
    # Ask for manual port selection
    try:
        selection = int(input("Enter port number to use: "))
        if 0 <= selection < len(available_ports):
            output_port = mido.open_output(available_ports[selection])
            print(f"Successfully connected to {available_ports[selection]}")
            return output_port
    except:
        pass
    
    print("Failed to connect to any MIDI port.")
    return None

def send_midi_note(port, note, velocity=100, duration=0.1, channel=0):
    """Send a MIDI note on/off message with specified duration"""
    # Make sure note and velocity are within MIDI range
    if note < 0: note = 0
    if note > 127: note = 127
    if velocity < 0: velocity = 0
    if velocity > 127: velocity = 127
    
    print(f"Sending note: {note}, velocity: {velocity}, channel: {channel}")
    
    # Send note on
    note_on = Message('note_on', note=note, velocity=velocity, channel=channel)
    port.send(note_on)
    # time.sleep(duration)
    
    # Send note off
    note_off = Message('note_off', note=note, velocity=0, channel=channel)
    port.send(note_off)
    # time.sleep(0.05)  # Small pause between messages

def send_midi_cc(port, control, value, channel=0):
    """Send a MIDI Control Change message"""
    if value > 127:
        value = 127  # Clamp to MIDI range
    elif value < 0:
        value = 0
    
    print(f"Sending CC: control={control}, value={value}, channel={channel}")
    cc = Message('control_change', channel=channel, control=control, value=value)
    port.send(cc)
    # time.sleep(0.05)  # Small pause between messages

def create_drum_beat(port, pattern_type="trap"):
    """Create a drum beat based on pattern type"""
    print(f"Creating {pattern_type} drum beat...")
    
    # Define patterns for different styles
    patterns = {
        "basic": [
            {"channel": 0, "note": KICK, "steps": [0, 8], "velocity": 100},
            {"channel": 0, "note": SNARE, "steps": [4, 12], "velocity": 90},
            {"channel": 0, "note": CLOSED_HAT, "steps": [0, 2, 4, 6, 8, 10, 12, 14], "velocity": 80}
        ],
        "trap": [
            {"channel": 0, "note": KICK, "steps": [0, 6, 10], "velocity": 100},
            {"channel": 0, "note": SNARE, "steps": [4, 12], "velocity": 90},
            {"channel": 0, "note": CLAP, "steps": [4, 12], "velocity": 85},
            {"channel": 0, "note": CLOSED_HAT, "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "velocity": 70},
            {"channel": 0, "note": OPEN_HAT, "steps": [7, 15], "velocity": 85}
        ],
        "house": [
            {"channel": 0, "note": KICK, "steps": [0, 4, 8, 12], "velocity": 100},
            {"channel": 0, "note": CLAP, "steps": [4, 12], "velocity": 90},
            {"channel": 0, "note": CLOSED_HAT, "steps": [2, 6, 10, 14], "velocity": 80},
            {"channel": 0, "note": OPEN_HAT, "steps": [7], "velocity": 85}
        ]
    }
    
    # Use the selected pattern or default to "basic"
    selected_pattern = patterns.get(pattern_type, patterns["basic"])
    
    # Send all the drum notes based on the pattern
    for drum in selected_pattern:
        for step in drum["steps"]:
            # Channel, note, velocity, midi channel for this drum part
            midi_channel = drum.get("channel", 0)  # Use drum's channel or default to 0
            
            # Calculate timing based on 16th notes
            # Each step is 1/16th note, so convert step number to timing
            beat_duration = 60 / 120  # seconds per beat at 120 BPM
            sixteenth_duration = beat_duration / 4  # duration of a 16th note
            
            # Work out when this note should be played
            note_time = step * sixteenth_duration
            note_duration = sixteenth_duration * 0.8  # Slightly shorter than a full 16th
            
            # Send the note after waiting the correct amount of time
            # sleep_time = note_time - (time.time() % beat_duration)
            # time.sleep(max(0, sleep_time))  # Ensure non-negative sleep duration
            send_midi_note(port, drum["note"], drum["velocity"], note_duration, midi_channel)

def create_chord_progression(port, root_note="C", progression_type="pop"):
    """Create a chord progression"""
    print(f"Creating {progression_type} chord progression in {root_note}...")
    
    # Convert root note to MIDI
    if root_note in note_to_midi:
        root_midi = note_to_midi[root_note]
    else:
        # Default to C4 if not found
        root_midi = 60
        print(f"Root note {root_note} not found, defaulting to C (60)")
    
    # Define different chord progressions
    progressions = {
        "pop": [
            {"chord": "maj", "transpose": 0},   # I   (C major)
            {"chord": "maj", "transpose": 5},   # IV  (F major)
            {"chord": "min", "transpose": 9},   # vi  (A minor)
            {"chord": "maj", "transpose": 7}    # V   (G major)
        ],
        "trap": [
            {"chord": "min", "transpose": 0},   # i   (C minor)
            {"chord": "min", "transpose": 5},   # iv  (F minor)
            {"chord": "maj", "transpose": 7},   # V   (G major)
            {"chord": "min", "transpose": 0}    # i   (C minor)
        ],
        "lofi": [
            {"chord": "min7", "transpose": 0},  # i7  (C minor 7)
            {"chord": "maj7", "transpose": 3},  # III7 (Eb major 7)
            {"chord": "min7", "transpose": 5},  # iv7 (F minor 7)
            {"chord": "7", "transpose": 7}      # V7  (G dominant 7)
        ]
    }
    
    # Use the selected progression or default to "pop"
    selected_progression = progressions.get(progression_type, progressions["pop"])
    
    # MIDI channel for chords
    midi_channel = 5  # Using channel 5 for keys
    
    # Send each chord in the progression
    for i, chord_data in enumerate(selected_progression):
        chord_type = chord_data["chord"]
        transpose = chord_data["transpose"]
        
        # Get chord root
        chord_root = root_midi + transpose
        
        # Get chord intervals
        intervals = chord_dictionary.get(chord_type, [0, 4, 7])
        
        # Calculate chord notes
        chord_notes = [chord_root + interval for interval in intervals]
        
        # Calculate when to play this chord (each chord lasts 1 bar)
        beat_duration = 60 / 120  # seconds per beat at 120 BPM
        chord_start_time = i * 4 * beat_duration  # 4 beats per chord
        chord_duration = 4 * beat_duration * 0.9  # Slightly less than a full bar
        
        # Schedule chord playback
        # time.sleep(chord_start_time - time.time() % (4 * beat_duration))
        
        # Play all notes in the chord simultaneously
        for note in chord_notes:
            send_midi_note(port, note, 80, chord_duration, midi_channel)

def create_bassline(port, root_note="C", pattern_type="simple"):
    """Create a bassline pattern"""
    print(f"Creating {pattern_type} bassline in {root_note}...")
    
    # Convert root note to MIDI (2 octaves down for bass)
    if root_note in note_to_midi:
        root_midi = note_to_midi[root_note] - 24  # 2 octaves down
    else:
        # Default to C2 if not found
        root_midi = 36  # C2
        print(f"Root note {root_note} not found, defaulting to C2 (36)")
    
    # Define different bassline patterns
    patterns = {
        "simple": [
            {"note": 0, "step": 0, "duration": 4},  # Root on beat 1
            {"note": 0, "step": 8, "duration": 4}   # Root on beat 3
        ],
        "octave": [
            {"note": 0, "step": 0, "duration": 4},  # Root on beat 1
            {"note": 12, "step": 4, "duration": 4}, # Octave up on beat 2
            {"note": 0, "step": 8, "duration": 4},  # Root on beat 3
            {"note": 12, "step": 12, "duration": 4} # Octave up on beat 4
        ],
        "walking": [
            {"note": 0, "step": 0, "duration": 4},  # Root
            {"note": 5, "step": 4, "duration": 2},  # Fifth
            {"note": 7, "step": 6, "duration": 2},  # Seventh
            {"note": 12, "step": 8, "duration": 4}, # Octave
            {"note": 7, "step": 12, "duration": 4}  # Seventh
        ]
    }
    
    # Use the selected pattern or default to "simple"
    selected_pattern = patterns.get(pattern_type, patterns["simple"])
    
    # MIDI channel for bass
    midi_channel = 4  # Using channel 4 for bass
    
    # Send each bass note in the pattern
    for note_data in selected_pattern:
        note = root_midi + note_data["note"]
        step = note_data["step"]
        duration = note_data["duration"]
        
        # Calculate timing
        beat_duration = 60 / 120  # seconds per beat at 120 BPM
        sixteenth_duration = beat_duration / 4  # duration of a 16th note
        
        # Calculate note timing
        note_time = step * sixteenth_duration
        note_duration = duration * sixteenth_duration * 0.9  # Slightly shorter
        
        # Schedule note playback
        # time.sleep(note_time - time.time() % beat_duration)
        send_midi_note(port, note, 100, note_duration, midi_channel)

def create_full_beat(port, style="trap", root_note="C"):
    """Create a full beat with drums, bass, and chords"""
    print(f"Creating full {style} beat in {root_note}...")
    
    # Create drum beat
    create_drum_beat(port, style)
    
    # Create bassline
    if style == "trap":
        create_bassline(port, root_note, "octave")
    elif style == "house":
        create_bassline(port, root_note, "simple")
    else:
        create_bassline(port, root_note, "walking")
    
    # Create chord progression
    create_chord_progression(port, root_note, style)
    
    print(f"Full {style} beat in {root_note} created!")

def create_channels_and_instruments(port):
    """Set up channels with appropriate instruments in FL Studio"""
    # We'll use Note On messages with special MIDI notes to configure instruments
    # We need to send notes to the channel we want to configure
    
    # Define some special configuration notes (these are defined in your FL Studio script)
    NOTE_ADD_CHANNEL = 67    # G3
    NOTE_SELECT_CHANNEL = 70  # A#3
    NOTE_SET_INSTRUMENT = 65  # F3
    NOTE_SET_PRESET = 66      # F#3
    
    # Since FL Studio recognizes instruments, we just need to:
    # 1. Add a channel
    # 2. Select the channel
    # 3. Set the instrument type
    # 4. Set the preset
    
    print("Setting up channels and instruments...")
    
    # List of channels to create
    channels = [
        {"name": "DRUMS", "instrument": "FPC", "preset": "Trap Kit"},
        {"name": "KICK", "instrument": "FPC", "preset": "808 Bass Drum"},
        {"name": "SNARE", "instrument": "FPC", "preset": "Clap & Snare"},
        {"name": "HATS", "instrument": "FPC", "preset": "Hi-Hat Collection"},
        {"name": "BASS", "instrument": "FLEX", "preset": "Deep Bass"},
        {"name": "KEYS", "instrument": "FLEX", "preset": "Warm Rhodes"},
        {"name": "LEAD", "instrument": "FLEX", "preset": "Bright Synth Lead"}
    ]
    
    # Create each channel
    for i, channel in enumerate(channels):
        # Add new channel
        send_midi_note(port, NOTE_ADD_CHANNEL, 100, 0.2)
        time.sleep(0.5)
        
        # Select the channel
        send_midi_cc(port, 100, i, 0)  # CC 100 selects channel
        time.sleep(0.2)
        
        # Set instrument type
        instrument_code = {"FPC": 0, "FLEX": 1}.get(channel["instrument"], 0)
        send_midi_cc(port, 125, instrument_code, 0)  # CC 125 sets instrument
        time.sleep(0.5)
        
        # Set preset
        preset_code = 0  # Default preset
        send_midi_cc(port, 121, preset_code, 0)  # CC 121 sets preset
        time.sleep(0.5)
    
    print("Channels and instruments set up successfully!")

def main():
    """Main function to create a beat in FL Studio"""
    # Connect to FL Studio
    port = connect_to_fl_studio()
    if not port:
        print("Failed to connect to FL Studio. Exiting.")
        return
    
    # Set up channels with instruments first
    create_channels_and_instruments(port)
    # time.sleep(1)  # Give FL Studio time to process
    
    # Ask user for beat style
    print("\nAvailable styles:")
    print("1. Trap")
    print("2. House")
    print("3. Pop")
    
    try:
        style_choice = int(input("Choose a style (1-3): "))
        if style_choice == 1:
            style = "trap"
        elif style_choice == 2:
            style = "house"
        else:
            style = "pop"
    except:
        style = "trap"  # Default
    
    # Ask user for root note
    root_note = input("Enter root note (e.g., C, F#, Bb): ").strip()
    if not root_note:
        root_note = "C"  # Default
    
    # Create the full beat
    create_full_beat(port, style, root_note)
    
    print("\nBeat created successfully in FL Studio!")
    print("Note: Make sure your FL Script Controller is loaded in FL Studio")
    
    # Keep the script running until user decides to exit
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()