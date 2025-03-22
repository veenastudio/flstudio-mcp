# device_test.py
# name=Test Controller

#This file contains logic for separating instruments, channels, preset selection. But i havent been able to send a proper song using this script yet. 

#file that listens to midi input and has definitions related to handling midi triggers




import transport
import ui
import midi
import channels
import playlist
import patterns
import arrangement
import general
import device
import time
import threading
import sys
import plugins
import mixer

# Global variables
running = True
command_history = []
current_pattern = 0
current_channel = 0
terminal_active = False

channel_to_edit = 0
step_to_edit = 0

# Enhanced channel configuration with more detailed instrument types
# Channel assignments for different instrument types
DRUMS_CHANNEL = 0
KICK_CHANNEL = 1 
SNARE_CHANNEL = 2
HATS_CHANNEL = 3
BASS_CHANNEL = 4
SUB_BASS_CHANNEL = 5
KEYS_CHANNEL = 6
PAD_CHANNEL = 7
LEAD_CHANNEL = 8
ARP_CHANNEL = 9

# Dictionary to track which channels have been configured
configured_channels = {}
for i in range(16):  # Support up to 16 channels
    configured_channels[i] = False

# Store MIDI channels to FL Studio channel mappings
midi_to_fl_channel_map = {
    0: DRUMS_CHANNEL,    # MIDI Channel 1 -> Drums
    1: KICK_CHANNEL,     # MIDI Channel 2 -> Kick
    2: SNARE_CHANNEL,    # MIDI Channel 3 -> Snare
    3: HATS_CHANNEL,     # MIDI Channel 4 -> Hats
    4: BASS_CHANNEL,     # MIDI Channel 5 -> Bass
    5: SUB_BASS_CHANNEL, # MIDI Channel 6 -> Sub Bass
    6: KEYS_CHANNEL,     # MIDI Channel 7 -> Keys
    7: PAD_CHANNEL,      # MIDI Channel 8 -> Pad
    8: LEAD_CHANNEL,     # MIDI Channel 9 -> Lead
    9: ARP_CHANNEL       # MIDI Channel 10 -> Arp
}

# Define instrument types for channel configuration
INSTRUMENT_DRUM = 0
INSTRUMENT_BASS = 1
INSTRUMENT_KEYS = 2
INSTRUMENT_LEAD = 3
INSTRUMENT_PAD = 4
INSTRUMENT_ARP = 5
INSTRUMENT_SUB = 6

# Channel defaults
channel_instrument_types = {
    DRUMS_CHANNEL: INSTRUMENT_DRUM,
    KICK_CHANNEL: INSTRUMENT_DRUM,
    SNARE_CHANNEL: INSTRUMENT_DRUM,
    HATS_CHANNEL: INSTRUMENT_DRUM,
    BASS_CHANNEL: INSTRUMENT_BASS,
    SUB_BASS_CHANNEL: INSTRUMENT_SUB,
    KEYS_CHANNEL: INSTRUMENT_KEYS,
    PAD_CHANNEL: INSTRUMENT_PAD,
    LEAD_CHANNEL: INSTRUMENT_LEAD,
    ARP_CHANNEL: INSTRUMENT_ARP
}

# Advanced plugin mappings with specific VST plugins
default_plugins = {
    DRUMS_CHANNEL: "FPC",
    KICK_CHANNEL: "FPC",
    SNARE_CHANNEL: "FPC", 
    HATS_CHANNEL: "FPC",
    BASS_CHANNEL: "FLEX",
    SUB_BASS_CHANNEL: "FLEX",
    KEYS_CHANNEL: "FLEX",
    PAD_CHANNEL: "FLEX",
    LEAD_CHANNEL: "FLEX",
    ARP_CHANNEL: "FLEX"
}

# Enhanced presets with more specific sounds
default_presets = {
    DRUMS_CHANNEL: "Trap Kit",
    KICK_CHANNEL: "808 Bass Drum",
    SNARE_CHANNEL: "Clap & Snare",
    HATS_CHANNEL: "Hi-Hat Collection",
    BASS_CHANNEL: "Deep Bass",
    SUB_BASS_CHANNEL: "808 Sub",
    KEYS_CHANNEL: "Warm Rhodes",
    PAD_CHANNEL: "Atmosphere",
    LEAD_CHANNEL: "Bright Synth Lead",
    ARP_CHANNEL: "Plucky Synth"
}

# Dictionary of effects for each channel (will apply to mixer tracks)
channel_effects = {
    DRUMS_CHANNEL: ["Compression", "EQ"],
    KICK_CHANNEL: ["EQ", "Limiter"],
    SNARE_CHANNEL: ["Reverb", "EQ"],
    HATS_CHANNEL: ["EQ", "Stereo Enhancer"],
    BASS_CHANNEL: ["Compression", "EQ", "Saturation"],
    SUB_BASS_CHANNEL: ["Limiter", "EQ"],
    KEYS_CHANNEL: ["Reverb", "Delay", "EQ"],
    PAD_CHANNEL: ["Reverb", "Chorus", "EQ"],
    LEAD_CHANNEL: ["Delay", "EQ", "Compression"],
    ARP_CHANNEL: ["Delay", "Reverb", "Filter"]
}

# Dictionary of chord types
chord_dictionary = {
    "maj": [0, 4, 7],       # Major: root, major third, perfect fifth
    "min": [0, 3, 7],       # Minor: root, minor third, perfect fifth
    "dim": [0, 3, 6],       # Diminished: root, minor third, diminished fifth
    "aug": [0, 4, 8],       # Augmented: root, major third, augmented fifth
    "maj7": [0, 4, 7, 11],  # Major 7th: major + major seventh
    "7": [0, 4, 7, 10],     # Dominant 7th: major + minor seventh
    "min7": [0, 3, 7, 10],  # Minor 7th: minor + minor seventh
    "sus4": [0, 5, 7],      # Suspended 4th: root, perfect fourth, perfect fifth
    "sus2": [0, 2, 7],      # Suspended 2nd: root, major second, perfect fifth
    "9": [0, 4, 7, 10, 14], # Dominant 9th: dominant 7th + major 9th
    "maj9": [0, 4, 7, 11, 14], # Major 9th: major 7th + major 9th
    "min9": [0, 3, 7, 10, 14], # Minor 9th: minor 7th + major 9th
    "add9": [0, 4, 7, 14],  # Add9: major triad + major 9th
    "min6": [0, 3, 7, 9],   # Minor 6th: minor triad + major 6th
    "maj6": [0, 4, 7, 9],   # Major 6th: major triad + major 6th
}

# Dictionary of note names to MIDI values
note_to_midi = {
    "C0": 12, "C#0": 13, "DB0": 13, "D0": 14, "D#0": 15, "EB0": 15, "E0": 16, "F0": 17, "F#0": 18, "GB0": 18, "G0": 19, "G#0": 20, "AB0": 20, "A0": 21, "A#0": 22, "BB0": 22, "B0": 23,
    "C1": 24, "C#1": 25, "DB1": 25, "D1": 26, "D#1": 27, "EB1": 27, "E1": 28, "F1": 29, "F#1": 30, "GB1": 30, "G1": 31, "G#1": 32, "AB1": 32, "A1": 33, "A#1": 34, "BB1": 34, "B1": 35,
    "C2": 36, "C#2": 37, "DB2": 37, "D2": 38, "D#2": 39, "EB2": 39, "E2": 40, "F2": 41, "F#2": 42, "GB2": 42, "G2": 43, "G#2": 44, "AB2": 44, "A2": 45, "A#2": 46, "BB2": 46, "B2": 47,
    "C3": 48, "C#3": 49, "DB3": 49, "D3": 50, "D#3": 51, "EB3": 51, "E3": 52, "F3": 53, "F#3": 54, "GB3": 54, "G3": 55, "G#3": 56, "AB3": 56, "A3": 57, "A#3": 58, "BB3": 58, "B3": 59,
    "C4": 60, "C#4": 61, "DB4": 61, "D4": 62, "D#4": 63, "EB4": 63, "E4": 64, "F4": 65, "F#4": 66, "GB4": 66, "G4": 67, "G#4": 68, "AB4": 68, "A4": 69, "A#4": 70, "BB4": 70, "B4": 71,
    "C5": 72, "C#5": 73, "DB5": 73, "D5": 74, "D#5": 75, "EB5": 75, "E5": 76, "F5": 77, "F#5": 78, "GB5": 78, "G5": 79, "G#5": 80, "AB5": 80, "A5": 81, "A#5": 82, "BB5": 82, "B5": 83,
    "C": 60, "C#": 61, "DB": 61, "D": 62, "D#": 63, "EB": 63, "E": 64, "F": 65, "F#": 66, "GB": 66, "G": 67, "G#": 68, "AB": 68, "A": 69, "A#": 70, "BB": 70, "B": 71
}

# Drum mappings (General MIDI standard)
drum_note_map = {
    "kick": 36,
    "snare": 38,
    "clap": 39,
    "closed_hat": 42, 
    "open_hat": 46,
    "low_tom": 43,
    "mid_tom": 47,
    "high_tom": 50,
    "crash": 49,
    "ride": 51,
    "rim": 37
}

# Common drum patterns
drum_patterns = {
    "basic": [
        {"note": "kick", "steps": [0, 8]},
        {"note": "snare", "steps": [4, 12]},
        {"note": "closed_hat", "steps": [0, 2, 4, 6, 8, 10, 12, 14]}
    ],
    "breakbeat": [
        {"note": "kick", "steps": [0, 6, 10]},
        {"note": "snare", "steps": [4, 12]},
        {"note": "closed_hat", "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
        {"note": "open_hat", "steps": [7, 15]}
    ],
    "trap": [
        {"note": "kick", "steps": [0, 7, 10]},
        {"note": "snare", "steps": [4, 12]},
        {"note": "closed_hat", "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]},
        {"note": "open_hat", "steps": [3, 11]}
    ],
    "house": [
        {"note": "kick", "steps": [0, 4, 8, 12]},
        {"note": "clap", "steps": [4, 12]},
        {"note": "closed_hat", "steps": [2, 6, 10, 14]},
        {"note": "open_hat", "steps": [7]}
    ],
    "hiphop": [
        {"note": "kick", "steps": [0, 10]},
        {"note": "snare", "steps": [4, 12]},
        {"note": "closed_hat", "steps": [1, 3, 5, 7, 9, 11, 13, 15]}
    ],
    "lofi": [
        {"note": "kick", "steps": [0, 8]},
        {"note": "snare", "steps": [4, 12, 14]},
        {"note": "closed_hat", "steps": [2, 6, 10, 14]},
        {"note": "rim", "steps": [1, 9]}
    ]
}

# Common bass patterns with relative note values (scale degrees)
bass_patterns = {
    "simple": {
        "steps": [0, 8],
        "notes": [0, 0],
        "durations": [4, 4]  # Duration in 16th notes
    },
    "octave": {
        "steps": [0, 4, 8, 12],
        "notes": [0, 7, 0, 7],
        "durations": [4, 4, 4, 4]
    },
    "walking": {
        "steps": [0, 4, 8, 12, 14],
        "notes": [0, 3, 5, 7, 10],
        "durations": [4, 4, 4, 2, 2]
    },
    "groove": {
        "steps": [0, 3, 8, 11],
        "notes": [0, 0, 7, 7],
        "durations": [3, 3, 3, 7]
    },
    "edm": {
        "steps": [0, 4, 8, 12],
        "notes": [0, 0, 5, 7],
        "durations": [4, 4, 4, 4]
    },
    "dancehall": {
        "steps": [0, 4, 6, 10, 12, 14],
        "notes": [0, 0, 3, 3, 7, 7],
        "durations": [4, 2, 4, 2, 2, 2]
    }
}

# Common chord progressions (as scale degrees from key)
chord_progressions = {
    "pop": [
        {"root": 0, "type": "maj", "position": 0},  # I
        {"root": 5, "type": "maj", "position": 4},  # IV
        {"root": 3, "type": "min", "position": 8},  # vi
        {"root": 7, "type": "maj", "position": 12}  # V
    ],
    "blues": [
        {"root": 0, "type": "7", "position": 0},   # I7
        {"root": 5, "type": "7", "position": 4},   # IV7
        {"root": 0, "type": "7", "position": 8},   # I7
        {"root": 7, "type": "7", "position": 12}   # V7
    ],
    "edm": [
        {"root": 0, "type": "maj", "position": 0},  # I
        {"root": 5, "type": "maj", "position": 4},  # IV
        {"root": 3, "type": "min", "position": 8},  # vi
        {"root": 7, "type": "maj", "position": 12}  # V
    ],
    "sad": [
        {"root": 0, "type": "min", "position": 0},  # i
        {"root": 5, "type": "min", "position": 4},  # v
        {"root": 8, "type": "maj", "position": 8},  # VI
        {"root": 7, "type": "maj", "position": 12}  # V
    ],
    "cinematic": [
        {"root": 0, "type": "min", "position": 0},     # i
        {"root": 8, "type": "maj", "position": 4},     # VI
        {"root": 5, "type": "min", "position": 8},     # v
        {"root": 7, "type": "maj7", "position": 12}    # V7
    ],
    "jazz": [
        {"root": 0, "type": "maj7", "position": 0},    # Imaj7
        {"root": 3, "type": "7", "position": 4},       # VI7
        {"root": 10, "type": "min7", "position": 8},   # ii7
        {"root": 5, "type": "7", "position": 12}       # V7
    ]
}

# Major scale intervals
major_scale = [0, 2, 4, 5, 7, 9, 11]

# Minor scale intervals
minor_scale = [0, 2, 3, 5, 7, 8, 10]

# Pentatonic major scale
pentatonic_major = [0, 2, 4, 7, 9]

# Pentatonic minor scale
pentatonic_minor = [0, 3, 5, 7, 10]

# Blues scale
blues_scale = [0, 3, 5, 6, 7, 10]

# Dictionary of scales
scales = {
    "major": major_scale,
    "minor": minor_scale,
    "pentatonic_major": pentatonic_major,
    "pentatonic_minor": pentatonic_minor,
    "blues": blues_scale
}

def OnInit():
    """Called when the script is loaded by FL Studio"""
    print("Advanced FL Studio Controller initialized")
    print("Type 'help' for a list of commands")
    
    # Ensure we have enough channels
    ensure_channels_exist()
    
    # Start the terminal input thread
    start_terminal_thread()
    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    global running
    running = False  # Signal the terminal thread to exit
    print("FL Studio Controller deinitialized")
    return

def OnRefresh(flags):
    """Called when FL Studio's state changes or when a refresh is needed"""
    # Update terminal with current state if needed
    return

def OnMidiIn(event):
    """Called whenever the device sends a MIDI message to FL Studio"""
    print(f"MIDI In - Status: {event.status}, Data1: {event.data1}, Data2: {event.data2}")
    
    # Route MIDI messages to the appropriate channel based on MIDI channel
    midi_channel = event.status & 0x0F  # Extract MIDI channel (0-15)
    if midi_channel in midi_to_fl_channel_map:
        fl_channel = midi_to_fl_channel_map[midi_channel]
        
        # Ensure the channel is configured with appropriate instrument
        if not configured_channels[fl_channel]:
            configure_channel_instrument(fl_channel)
        
        # Handle Note On/Off messages
        if (event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16):
            # Mark as handled to prevent default processing
            event.handled = True
            
            # Determine if it's a note-on event with velocity > 0
            is_note_on = (event.data2 > 0)
            
            # Send the note to the appropriate FL Studio channel
            send_note_to_channel(
                channel=fl_channel, 
                note=event.data1, 
                velocity=event.data2,
                is_note_on=is_note_on
            )
            
        # Handle Control Change messages
        elif (event.status >= midi.MIDI_CONTROLCHANGE and event.status < midi.MIDI_CONTROLCHANGE + 16):
            # Mark as handled to prevent default processing
            event.handled = True
            
            # Process Control Change messages
            print(f"Received CC: {event.data1}, Value: {event.data2} for channel {fl_channel}")
            
            # Here you could add specific CC handling code
            # For example:
            # if event.data1 == 7:  # Volume
            #     channels.setChannelVolume(fl_channel, event.data2 / 127)
            
    return


def send_note_to_channel(channel, note, velocity, is_note_on):
    """Send a note event to a specific FL Studio channel"""
    channels.selectOneChannel(channel)
    
    if is_note_on and velocity > 0:
        # This is a note-on event
        channels.midiNoteOn(channel, note, velocity)
        print(f"Note ON to channel {channel}: note={note}, velocity={velocity}")
    else:
        # This is a note-off event
        channels.midiNoteOn(channel, note, 0)
        print(f"Note OFF to channel {channel}: note={note}")

def ensure_channels_exist():
    """Make sure we have enough channels for our instrument types"""
    # Count existing channels
    channel_count = channels.channelCount()
    
    # Add channels until we have enough for our needs
    max_channel_needed = max(DRUMS_CHANNEL, KICK_CHANNEL, SNARE_CHANNEL, HATS_CHANNEL, 
                            BASS_CHANNEL, SUB_BASS_CHANNEL, KEYS_CHANNEL, PAD_CHANNEL, 
                            LEAD_CHANNEL, ARP_CHANNEL)
    
    while channel_count <= max_channel_needed:
        channels.addChannel()
        channel_count += 1
        
    print(f"Ensured {channel_count} channels exist")

def configure_channel_instrument(channel_num):
    """Configure a channel with the appropriate instrument type"""
    if channel_num in default_plugins:
        plugin_name = default_plugins[channel_num]
        preset_name = default_presets[channel_num]
        
        # Select the channel
        channels.selectOneChannel(channel_num)
        
        # Set appropriate name based on instrument type
        channel_types = {
            DRUMS_CHANNEL: "DRUMS", 
            KICK_CHANNEL: "KICK",
            SNARE_CHANNEL: "SNARE",
            HATS_CHANNEL: "HATS",
            BASS_CHANNEL: "BASS",
            SUB_BASS_CHANNEL: "SUB BASS",
            KEYS_CHANNEL: "KEYS",
            PAD_CHANNEL: "PAD",
            LEAD_CHANNEL: "LEAD",
            ARP_CHANNEL: "ARP"
        }
        
        if channel_num in channel_types:
            channels.setChannelName(channel_num, channel_types[channel_num])
        
        # Set channel type based on instrument - FIX: don't use setChannelType
        instrument_type = channel_instrument_types.get(channel_num, INSTRUMENT_DRUM)
        
        # Configure channel based on instrument type
        if instrument_type == INSTRUMENT_DRUM:
            # For drums, use FPC or sampler
            # Instead of using setChannelType, we'll just rename the channel
            print(f"Configured channel {channel_num} as {channel_types.get(channel_num, 'DRUM')}")
            
        else:
            # For melodic instruments, use FLEX or other plugins
            print(f"Configured channel {channel_num} as {channel_types.get(channel_num, 'INSTRUMENT')}")
            
        # Mark as configured
        configured_channels[channel_num] = True
        
        # Route channel to separate mixer track
        channels.routeToMixerTrack(channel_num, channel_num + 1)  # +1 because mixer track 0 is master
        
        print(f"Channel {channel_num} configured with {plugin_name} and preset {preset_name}")
    else:
        print(f"No configuration defined for channel {channel_num}")

def OnMidiMsg(event, timestamp=0):
    """Called when a processed MIDI message is received"""
    print(f"MIDI Msg - Status: {event.status}, Data1: {event.data1}, Data2: {event.data2}")
    
    global channel_to_edit, step_to_edit
    
    # Handle Control Change messages for step sequencer grid control
    if event.status >= midi.MIDI_CONTROLCHANGE and event.status < midi.MIDI_CONTROLCHANGE + 16:
        # CC 100: Select channel to edit
        if event.data1 == 100:
            channel_to_edit = event.data2
            channels.selectOneChannel(channel_to_edit)
            print(f"Selected channel {channel_to_edit} for grid editing")
            event.handled = True
            
        # CC 110: Select step to edit
        elif event.data1 == 110:
            step_to_edit = event.data2
            print(f"Selected step {step_to_edit} for grid editing")
            event.handled = True
            
        # CC 111: Toggle step on/off
        elif event.data1 == 111:
            enabled = event.data2 > 0
            channels.setGridBit(channel_to_edit, step_to_edit, enabled)
            print(f"Set grid bit for channel {channel_to_edit}, step {step_to_edit} to {enabled}")
            commit_pattern_changes()  # Force UI update
            event.handled = True
            
        # CC 112: Set step velocity/level
        elif event.data1 == 112:
            velocity = event.data2
            channels.setStepParameterByIndex(channel_to_edit, patterns.patternNumber(), step_to_edit, midi.pVelocity, velocity)
            print(f"Set step level for channel {channel_to_edit}, step {step_to_edit} to {velocity}")
            commit_pattern_changes()  # Force UI update
            event.handled = True
            
        # CC 120: Select instrument type
        elif event.data1 == 120:
            instrument_type = event.data2
            
            # Map instrument types to channels
            channel_map = {
                0: DRUMS_CHANNEL,     # Drums
                1: KICK_CHANNEL,      # Kick
                2: SNARE_CHANNEL,     # Snare
                3: HATS_CHANNEL,      # Hats
                4: BASS_CHANNEL,      # Bass
                5: SUB_BASS_CHANNEL,  # Sub Bass
                6: KEYS_CHANNEL,      # Keys
                7: PAD_CHANNEL,       # Pad
                8: LEAD_CHANNEL,      # Lead
                9: ARP_CHANNEL        # Arp
            }
            
            channel_num = channel_map.get(instrument_type, -1)
                
            if channel_num >= 0:
                # Configure the channel if not already
                if not configured_channels[channel_num]:
                    configure_channel_instrument(channel_num)
                    
                # Select the channel
                channels.selectOneChannel(channel_num)
                print(f"Selected instrument type: {instrument_type}")
                
            event.handled = True
            
        # CC 121: Select a preset
        elif event.data1 == 121:
            preset_idx = event.data2
            channel = channels.selectedChannel()
            
            # Map preset index to preset names based on channel type
            if channel == DRUMS_CHANNEL or channel == KICK_CHANNEL or channel == SNARE_CHANNEL or channel == HATS_CHANNEL:
                presets = ["808 Kit", "Trap Kit", "House Kit", "Acoustic Kit", "Lo-Fi Kit"]
            elif channel == BASS_CHANNEL:
                presets = ["Deep Bass", "808 Sub", "Wobble Bass", "Synth Bass", "Fingered Bass"]
            elif channel == KEYS_CHANNEL:
                presets = ["Warm Rhodes", "Pad", "Pluck", "Organ", "Strings"]
            elif channel == LEAD_CHANNEL:
                presets = ["Saw Lead", "Square Lead", "Supersaw", "Acid Lead", "Vocal Lead"]
            else:
                presets = ["Default Preset"]
            
            if preset_idx < len(presets):
                preset_name = presets[preset_idx]
                # In a real implementation, you'd set the preset here
                print(f"Selected preset {preset_name} for channel {channel}")
            
            event.handled = True
            
        # CC 122: Set note properties
        elif event.data1 == 122:
            # Note properties: slide, porta, etc.
            property_value = event.data2
            
            # In a real implementation, you'd set note properties here
            print(f"Setting note properties to {property_value}")
            event.handled = True
            
        # CC 123: Set note value for step
        elif event.data1 == 123:
            note_value = event.data2
            
            # In a real implementation, you'd set the note value for a step here
            print(f"Setting note value {note_value} for step {step_to_edit}")
            event.handled = True
            
        # CC 124: Position for note
        elif event.data1 == 124:
            position = event.data2
            
            # In a real implementation, you'd set the position for a note here
            print(f"Setting position {position} for note")
            event.handled = True
            
        # CC 125: Set instrument type for channel
        elif event.data1 == 125:
            instrument_type = event.data2
            channel = channels.selectedChannel()
            
            # Set channel instrument type
            channel_instrument_types[channel] = instrument_type
            configure_channel_instrument(channel)
            print(f"Set channel {channel} instrument type to {instrument_type}")
            event.handled = True
            
        # Process other CC messages with existing code
        else:
            # Handle other CC messages with your existing code...
            pass
    
    # Handle Note On messages
    elif event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16:
        # Extract MIDI channel from status byte
        midi_channel = event.status & 0x0F
        
        # Map MIDI channel to instrument type if in our mapping
        if midi_channel in midi_to_fl_channel_map:
            target_channel = midi_to_fl_channel_map[midi_channel]
            # Forward note to the appropriate FL Studio channel
            send_note_to_channel(
                channel=target_channel,
                note=event.data1,
                velocity=event.data2,
                is_note_on=True
            )
            event.handled = True
        
        # Handle Note On messages for other cases
        pass

def commit_pattern_changes(pattern_num=None):
    """Force FL Studio to update the pattern data visually"""
    if pattern_num is None:
        pattern_num = patterns.patternNumber()
    
    # Force FL Studio to redraw and commit changes
    ui.crDisplayRect()
    
    # Force channel rack to update
    ui.setFocused(midi.widChannelRack)
    
    # Update playlist if needed
    playlist.refresh()
    
    # Request a full refresh
    # general.processRECEvent(midi.REC_UpdateControl, 1, midi.REC_UpdateValue)

def OnTransport(isPlaying):
    """Called when the transport state changes (play/stop)"""
    print(f"Transport state changed: {'Playing' if isPlaying else 'Stopped'}")
    return

def OnTempoChange(tempo):
    """Called when the tempo changes"""
    print(f"Tempo changed to: {tempo} BPM")
    return

# Terminal interface functions
def start_terminal_thread():
    """Start a thread to handle terminal input"""
    global terminal_active
    if not terminal_active:
        terminal_active = True
        thread = threading.Thread(target=terminal_loop)
        thread.daemon = True
        thread.start()

def terminal_loop():
    """Main terminal input loop"""
    global running, terminal_active
    
    print("\n===== FL STUDIO ADVANCED CONTROLLER =====")
    print("Enter commands to build your beat (type 'help' for commands)")
    
    while running:
        try:
            command = input("\nFLBEAT> ")
            command_history.append(command)
            process_command(command)
        except Exception as e:
            print(f"Error processing command: {e}")
    
    terminal_active = False

def process_command(command):
    """Process a command entered in the terminal"""
    cmd_parts = command.strip().split()
    
    if not cmd_parts:
        return
    
    cmd = cmd_parts[0].lower()
    args = cmd_parts[1:]
    
    # Help command
    if cmd == "help":
        show_help()
    
    # Project commands
    elif cmd == "new":
        ui.new()
        print("Created new project")
    elif cmd == "save":
        ui.saveNew()
        print("Project saved")
    elif cmd == "bpm":
        if args:
            try:
                new_tempo = float(args[0])
                transport.setTempo(new_tempo)
                print(f"Tempo set to {new_tempo} BPM")
            except ValueError:
                print("Invalid tempo value")
        else:
            current_tempo = mixer.getCurrentTempo()
            print(f"Current tempo: {current_tempo} BPM")
    
    # Transport commands
    elif cmd == "play":
        transport.start()
        print("Playback started")
    elif cmd == "stop":
        transport.stop()
        print("Playback stopped")
    elif cmd == "record":
        transport.record()
        print("Recording started")
    elif cmd == "loop":
        toggle = args[0].lower() if args else "toggle"
        if toggle == "on":
            transport.setLoopMode(1)
            print("Loop mode enabled")
        elif toggle == "off":
            transport.setLoopMode(0)
            print("Loop mode disabled")
        else:
            current = transport.getLoopMode()
            transport.setLoopMode(0 if current else 1)
            print(f"Loop mode {'enabled' if not current else 'disabled'}")
    
    # Pattern commands
    elif cmd == "pattern":
        if not args:
            print(f"Current pattern: {patterns.patternNumber()}")
            return
            
        subcmd = args[0].lower()
        if subcmd == "new":
            new_pattern = patterns.findFirstNextEmptyPat(midi.FFNEP_FindFirst)
            patterns.jumpTo(new_pattern)
            print(f"Created and selected pattern {new_pattern}")
        elif subcmd == "select":
            if len(args) > 1:
                try:
                    pattern_num = int(args[1])
                    patterns.jumpTo(pattern_num)
                    print(f"Selected pattern {pattern_num}")
                except ValueError:
                    print("Invalid pattern number")
            else:
                print("Please specify a pattern number")
        elif subcmd == "clone":
            if len(args) > 1:
                try:
                    source_pattern = int(args[1])
                    new_pattern = patterns.findFirstNextEmptyPat(midi.FFNEP_FindFirst)
                    patterns.clonePattern(source_pattern)
                    print(f"Cloned pattern {source_pattern}")
                except ValueError:
                    print("Invalid pattern number")
            else:
                source_pattern = patterns.patternNumber()
                patterns.clonePattern()
                print(f"Cloned current pattern")
        elif subcmd == "length":
            if len(args) > 1:
                try:
                    beats = int(args[1])
                    # Set pattern length (no direct API function, would need to use terminal commands)
                    print(f"Setting pattern length to {beats} beats")
                except ValueError:
                    print("Invalid beat count")
            else:
                length = patterns.getPatternLength(patterns.patternNumber())
                print(f"Current pattern length: {length} beats")
        elif subcmd == "refresh":
            # Force refresh the current pattern
            commit_pattern_changes()
            print("Pattern refreshed")
    
    # Channel commands
    elif cmd == "channel":
        if not args:
            print(f"Current channel: {channels.selectedChannel()}")
            return
            
        subcmd = args[0].lower()
        if subcmd == "select":
            if len(args) > 1:
                try:
                    channel_num = int(args[1])
                    channels.selectOneChannel(channel_num)
                    print(f"Selected channel {channel_num}")
                except ValueError:
                    print("Invalid channel number")
            else:
                print("Please specify a channel number")
        elif subcmd == "add":
            if len(args) > 1:
                preset_type = args[1].lower()
                if preset_type == "sampler":
                    # Correctly use addChannel with parameter
                    new_channel = channels.addChannel()
                elif preset_type == "plugin":
                    new_channel = channels.addChannel()
                else:
                    new_channel = channels.addChannel()
                print(f"Added new channel {new_channel}")
                channels.selectOneChannel(new_channel)
            else:
                new_channel = channels.addChannel()
                print(f"Added new channel {new_channel}")
                channels.selectOneChannel(new_channel)
        elif subcmd == "name":
            if len(args) > 1:
                name = " ".join(args[1:])
                channel = channels.selectedChannel()
                channels.setChannelName(channel, name)
                print(f"Renamed channel {channel} to '{name}'")
            else:
                channel = channels.selectedChannel()
                name = channels.getChannelName(channel)
                print(f"Channel {channel} name: '{name}'")
        elif subcmd == "mute":
            if len(args) > 1:
                try:
                    channel_num = int(args[1])
                    channels.muteChannel(channel_num)
                    print(f"Toggled mute on channel {channel_num}")
                except ValueError:
                    print("Invalid channel number")
            else:
                channel = channels.selectedChannel()
                channels.muteChannel(channel)
                print(f"Toggled mute on channel {channel}")
        elif subcmd == "instrument":
            if len(args) > 1:
                instrument_type = args[1].lower()
                channel = channels.selectedChannel()
                
                # Just update the instrument type in our dictionary and rename
                if instrument_type == "drums":
                    channel_instrument_types[channel] = INSTRUMENT_DRUM
                    channels.setChannelName(channel, "DRUMS")
                    print(f"Set channel {channel} as DRUMS")
                    
                elif instrument_type == "bass":
                    channel_instrument_types[channel] = INSTRUMENT_BASS
                    channels.setChannelName(channel, "BASS")
                    print(f"Set channel {channel} as BASS")
                    
                elif instrument_type == "keys":
                    channel_instrument_types[channel] = INSTRUMENT_KEYS
                    channels.setChannelName(channel, "KEYS")
                    print(f"Set channel {channel} as KEYS")
                    
                elif instrument_type == "lead":
                    channel_instrument_types[channel] = INSTRUMENT_LEAD
                    channels.setChannelName(channel, "LEAD")
                    print(f"Set channel {channel} as LEAD")
                    
                elif instrument_type == "pad":
                    channel_instrument_types[channel] = INSTRUMENT_PAD
                    channels.setChannelName(channel, "PAD")
                    print(f"Set channel {channel} as PAD")
                    
                elif instrument_type == "arp":
                    channel_instrument_types[channel] = INSTRUMENT_ARP
                    channels.setChannelName(channel, "ARP")
                    print(f"Set channel {channel} as ARP")
                    
                elif instrument_type == "sub":
                    channel_instrument_types[channel] = INSTRUMENT_SUB
                    channels.setChannelName(channel, "SUB BASS")
                    print(f"Set channel {channel} as SUB BASS")
                    
                else:
                    print(f"Unknown instrument type: {instrument_type}")
            else:
                print("Please specify an instrument type (drums, bass, keys, lead, pad, arp, sub)")
    
    # Plugin commands
    elif cmd == "plugin":
        if not args:
            print("Please specify a plugin subcommand")
            return
            
        subcmd = args[0].lower()
        if subcmd == "load":
            if len(args) > 1:
                plugin_name = " ".join(args[1:])
                channel = channels.selectedChannel()
                
                # We can't directly load plugins with API, but we can name the channel
                channels.setChannelName(channel, plugin_name)
                print(f"Loading plugin '{plugin_name}' on channel {channel}")
            else:
                print("Please specify a plugin name")
                
        elif subcmd == "preset":
            if len(args) > 1:
                preset_name = " ".join(args[1:])
                channel = channels.selectedChannel()
                # This would need plugin-specific implementation
                print(f"Loading preset '{preset_name}' on channel {channel}")
            else:
                print("Please specify a preset name")
                
        elif subcmd == "param":
            if len(args) >= 3:
                try:
                    param_index = int(args[1])
                    param_value = float(args[2])
                    channel = channels.selectedChannel()
                    # Set plugin parameter if this is a plugin channel
                    try:
                        if plugins.isValid(channel):
                            plugins.setParamValue(param_value, param_index, channel)
                            print(f"Set parameter {param_index} to {param_value} on channel {channel}")
                        else:
                            print(f"No valid plugin on channel {channel}")
                    except AttributeError:
                        print("Plugin parameter setting not available in this API version")
                except ValueError:
                    print("Invalid parameter index or value")
            else:
                print("Format: plugin param [index] [value]")
    
    # Note commands
    elif cmd == "note":
        if len(args) >= 3:
            try:
                note_name = args[0].upper()
                position = float(args[1])
                length = float(args[2])
                
                # Convert note name to MIDI note number
                if note_name in note_to_midi:
                    base_note = note_to_midi[note_name]
                else:
                    note_map = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}
                    base_note = note_map.get(note_name[0], 60)
                    
                    # Apply sharp/flat
                    if len(note_name) > 1:
                        if note_name[1] == "#":
                            base_note += 1
                        elif note_name[1] == "B":
                            base_note -= 1
                    
                    # Apply octave
                    if len(note_name) > 1 and note_name[-1].isdigit():
                        octave = int(note_name[-1])
                        base_note = (octave * 12) + (base_note % 12)
                
                # Add note
                pattern = patterns.patternNumber()
                channel = channels.selectedChannel()
                velocity = 100  # Default velocity
                
                if len(args) > 3:
                    try:
                        velocity = int(args[3])
                    except ValueError:
                        pass
                
                # Calculate position in PPQ
                ppq = general.getRecPPQ()
                pos_ticks = int(position * ppq)
                length_ticks = int(length * ppq)
                
                # Add the note
                note_index = channels.addNote(channel, pos_ticks, length_ticks, base_note, velocity, 0)
                print(f"Added note {note_name} at position {position}, length {length}, velocity {velocity} with index {note_index}")
                
                # Force pattern refresh
                commit_pattern_changes()
            except ValueError:
                print("Invalid note parameters. Format: note [name] [position] [length] [velocity]")
        else:
            print("Insufficient parameters. Format: note [name] [position] [length] [velocity]")
    
    # Musical command: Chord
    elif cmd == "chord":
        if len(args) >= 2:
            try:
                root_note = args[0].upper()
                chord_type = args[1].lower()
                position = float(args[2]) if len(args) > 2 else 0
                length = float(args[3]) if len(args) > 3 else 1
                
                # Convert root note to MIDI value
                root_midi = 60  # Default to middle C
                for note_name, midi_val in note_to_midi.items():
                    if root_note == note_name:
                        root_midi = midi_val
                        break
                
                # Get chord intervals
                intervals = chord_dictionary.get(chord_type, [0, 4, 7])
                
                # Calculate actual MIDI notes for the chord
                chord_notes = [root_midi + interval for interval in intervals]
                
                # Add each note
                channel = channels.selectedChannel()
                ppq = general.getRecPPQ()
                pos_ticks = int(position * ppq)
                length_ticks = int(length * ppq)
                
                for note in chord_notes:
                    channels.addNote(channel, pos_ticks, length_ticks, note, 100, 0)
                
                print(f"Added {root_note} {chord_type} chord at position {position}")
                commit_pattern_changes()
                
            except Exception as e:
                print(f"Error adding chord: {str(e)}")
        else:
            print("Format: chord [root] [type] [position] [length]")
    
    # Musical command: Bassline
    elif cmd == "bassline":
        if args:
            try:
                pattern_type = args[0].lower()
                root_note = args[1].upper() if len(args) > 1 else "C"
                
                # Select the BASS channel
                channels.selectOneChannel(BASS_CHANNEL)
                
                # Ensure bass channel is configured
                if not configured_channels[BASS_CHANNEL]:
                    configure_channel_instrument(BASS_CHANNEL)
                
                # Convert root note to MIDI value
                root_midi = 36  # Default to low C
                for note_name, midi_val in note_to_midi.items():
                    if root_note == note_name:
                        # Transpose to bass range (2 octaves down)
                        root_midi = midi_val - 24
                        break
                
                channel = BASS_CHANNEL
                ppq = general.getRecPPQ()
                
                # Different pattern types
                if pattern_type == "walking":
                    # Walking bass pattern (root, 5th, 6th, 7th)
                    notes = [root_midi, root_midi + 7, root_midi + 9, root_midi + 10]
                    positions = [0, 4, 8, 12]  # Quarter notes
                    
                elif pattern_type == "octave":
                    # Octave jumping pattern
                    notes = [root_midi, root_midi + 12, root_midi, root_midi + 12]
                    positions = [0, 4, 8, 12]
                    
                elif pattern_type == "simple":
                    # Simple root note on beats
                    notes = [root_midi, root_midi]
                    positions = [0, 8]
                    
                elif pattern_type == "edm":
                    # EDM style bass pattern
                    notes = [root_midi, root_midi, root_midi + 7, root_midi + 7]
                    positions = [0, 4, 8, 12]
                    
                elif pattern_type == "groove":
                    # Groove bass pattern
                    notes = [root_midi, root_midi, root_midi + 7, root_midi + 5]
                    positions = [0, 3, 8, 11]
                    
                elif pattern_type == "dancehall":
                    # Dancehall pattern
                    notes = [root_midi, root_midi, root_midi + 3, root_midi + 3, root_midi + 7, root_midi + 7]
                    positions = [0, 4, 6, 10, 12, 14]
                    
                else:
                    print(f"Unknown bassline pattern type: {pattern_type}")
                    return
                    
                # Add notes
                for i, pos in enumerate(positions):
                    note = notes[i % len(notes)]
                    pos_ticks = pos * (ppq // 4)  # Convert step to ticks
                    length_ticks = ppq // 2  # 8th note length
                    channels.addNote(channel, pos_ticks, length_ticks, note, 100, 0)
                    
                print(f"Added {pattern_type} bassline in {root_note}")
                commit_pattern_changes()
                
            except Exception as e:
                print(f"Error adding bassline: {str(e)}")
        else:
            print("Format: bassline [type] [root_note]")
            
    # Musical command: Arpeggio
    elif cmd == "arpeggio":
        if len(args) >= 2:
            try:
                root_note = args[0].upper()
                chord_type = args[1].lower()
                speed = args[2] if len(args) > 2 else "16th"
                length = int(args[3]) if len(args) > 3 else 1
                pattern_type = args[4] if len(args) > 4 else "up"
                
                # Default to use ARP channel
                channels.selectOneChannel(ARP_CHANNEL)
                
                # Ensure arp channel is configured
                if not configured_channels[ARP_CHANNEL]:
                    configure_channel_instrument(ARP_CHANNEL)
                
                # Convert root note to MIDI value
                root_midi = 60  # Default to middle C
                for note_name, midi_val in note_to_midi.items():
                    if root_note == note_name:
                        root_midi = midi_val
                        break
                
                # Get chord intervals
                intervals = chord_dictionary.get(chord_type, [0, 4, 7])
                
                # Calculate actual MIDI notes for the chord
                chord_notes = [root_midi + interval for interval in intervals]
                
                # Determine step spacing based on speed
                if speed == "8th":
                    step_size = 2
                elif speed == "triplet":
                    step_size = 1  # This is simplified; true triplets need more complex timing
                else:  # 16th
                    step_size = 1
                
                # Get direction pattern
                if pattern_type == "down":
                    note_indices = list(range(len(chord_notes) - 1, -1, -1))  # Descending
                elif pattern_type == "updown":
                    note_indices = list(range(len(chord_notes))) + list(range(len(chord_notes) - 2, 0, -1))  # Up and down
                elif pattern_type == "downup":
                    note_indices = list(range(len(chord_notes) - 1, -1, -1)) + list(range(1, len(chord_notes) - 1))  # Down and up
                elif pattern_type == "random":
                    import random
                    note_indices = [random.randint(0, len(chord_notes) - 1) for _ in range(8)]  # Random
                else:  # "up" - default
                    note_indices = list(range(len(chord_notes)))  # Ascending
                
                # Create the arpeggio pattern
                channel = ARP_CHANNEL
                ppq = general.getRecPPQ()
                
                for bar in range(length):
                    for i in range(16 // step_size):
                        note_index = note_indices[i % len(note_indices)]
                        note = chord_notes[note_index]
                        pos_ticks = (bar * 16 + i * step_size) * (ppq // 4)
                        length_ticks = (ppq // 4) * step_size - 1  # Slightly shorter than full step
                        channels.addNote(channel, pos_ticks, length_ticks, note, 100, 0)
                
                print(f"Added {speed} {pattern_type} arpeggio of {root_note} {chord_type}")
                commit_pattern_changes()
                
            except Exception as e:
                print(f"Error adding arpeggio: {str(e)}")
        else:
            print("Format: arpeggio [root] [chord_type] [speed] [length] [pattern]")
            
    # Musical command: Pad
    elif cmd == "pad":
        if len(args) >= 2:
            try:
                root_note = args[0].upper()
                chord_type = args[1].lower()
                
                # Select the PAD channel
                channels.selectOneChannel(PAD_CHANNEL)
                
                # Ensure pad channel is configured
                if not configured_channels[PAD_CHANNEL]:
                    configure_channel_instrument(PAD_CHANNEL)
                
                # Convert root note to MIDI value
                root_midi = 60  # Default to middle C
                for note_name, midi_val in note_to_midi.items():
                    if root_note == note_name:
                        root_midi = midi_val
                        break
                
                # Get chord intervals
                intervals = chord_dictionary.get(chord_type, [0, 4, 7])
                
                # Calculate actual MIDI notes for the chord
                chord_notes = [root_midi + interval for interval in intervals]
                
                # Add each note as a long sustained note
                channel = PAD_CHANNEL
                ppq = general.getRecPPQ()
                pos_ticks = 0  # Start at beginning
                length_ticks = ppq * 4  # Full bar length
                
                for note in chord_notes:
                    channels.addNote(channel, pos_ticks, length_ticks, note, 80, 0)  # Lower velocity for pad
                
                print(f"Added {root_note} {chord_type} pad")
                commit_pattern_changes()
                
            except Exception as e:
                print(f"Error adding pad: {str(e)}")
        else:
            print("Format: pad [root] [chord_type]")
            
    # Musical command: Lead
    elif cmd == "lead":
        if len(args) >= 2:
            try:
                root_note = args[0].upper()
                scale_type = args[1].lower()
                pattern_type = args[2] if len(args) > 2 else "simple"
                
                # Select the LEAD channel
                channels.selectOneChannel(LEAD_CHANNEL)
                
                # Ensure lead channel is configured
                if not configured_channels[LEAD_CHANNEL]:
                    configure_channel_instrument(LEAD_CHANNEL)
                
                # Convert root note to MIDI value
                root_midi = 72  # Default to C5
                for note_name, midi_val in note_to_midi.items():
                    if root_note == note_name:
                        root_midi = midi_val
                        break
                
                # Move to a higher octave for lead
                while root_midi < 60:  # Ensure at least C4 or higher
                    root_midi += 12
                
                # Get scale type
                if scale_type == "major":
                    scale = major_scale
                elif scale_type == "minor":
                    scale = minor_scale
                elif scale_type == "pent_major":
                    scale = pentatonic_major
                elif scale_type == "pent_minor":
                    scale = pentatonic_minor
                elif scale_type == "blues":
                    scale = blues_scale
                else:
                    print(f"Unknown scale type: {scale_type}, using major")
                    scale = major_scale
                
                # Add various lead patterns
                channel = LEAD_CHANNEL
                ppq = general.getRecPPQ()
                
                # Define patterns
                patterns = {
                    "simple": {
                        "notes": [0, 2, 4, 2],  # Scale degrees
                        "positions": [0, 4, 8, 12],  # In 16th notes
                        "velocities": [110, 90, 100, 90]
                    },
                    "melody1": {
                        "notes": [0, 2, 4, 7, 9, 7, 4, 2],
                        "positions": [0, 2, 4, 6, 8, 10, 12, 14],
                        "velocities": [100, 80, 90, 100, 100, 90, 85, 80]
                    },
                    "melody2": {
                        "notes": [0, 4, 7, 4, 5, 4, 2, 0],
                        "positions": [0, 2, 4, 6, 8, 10, 12, 14],
                        "velocities": [100, 90, 100, 80, 95, 80, 90, 100]
                    },
                    "arpeggio": {
                        "notes": [0, 4, 7, 12, 7, 4, 0, -5],
                        "positions": [0, 2, 4, 6, 8, 10, 12, 14],
                        "velocities": [100, 85, 90, 100, 90, 85, 80, 90]
                    }
                }
                
                # Get selected pattern or default to simple
                if pattern_type not in patterns:
                    print(f"Unknown pattern type: {pattern_type}, using simple")
                    pattern_type = "simple"
                
                pattern = patterns[pattern_type]
                
                # Create lead melody
                for i, scale_degree in enumerate(pattern["notes"]):
                    # Calculate the actual note value
                    octave_shift = scale_degree // len(scale)
                    note_index = scale_degree % len(scale)
                    if note_index < 0:
                        note_index = len(scale) + note_index
                        octave_shift -= 1
                    
                    note_interval = scale[note_index]
                    note = root_midi + note_interval + (octave_shift * 12)
                    
                    # Get position and velocity
                    position = pattern["positions"][i]
                    velocity = pattern["velocities"][i]
                    
                    # Add the note
                    pos_ticks = position * (ppq // 4)  # Convert to ticks
                    length_ticks = (ppq // 4) - 1  # Slightly less than a 16th note
                    
                    channels.addNote(channel, pos_ticks, length_ticks, note, velocity, 0)
                
                print(f"Added {pattern_type} lead melody in {root_note} {scale_type}")
                commit_pattern_changes()
                
            except Exception as e:
                print(f"Error adding lead: {str(e)}")
        else:
            print("Format: lead [root] [scale_type] [pattern_type]")
            
    # Drum pattern command
    elif cmd == "drums":
        if args:
            pattern_type = args[0].lower()
            
            if pattern_type in drum_patterns:
                # Select the DRUMS channel
                channels.selectOneChannel(DRUMS_CHANNEL)
                
                # Ensure drums channel is configured
                if not configured_channels[DRUMS_CHANNEL]:
                    configure_channel_instrument(DRUMS_CHANNEL)
                
                # For standard drum patterns
                if isinstance(drum_patterns[pattern_type], list):
                    # Add each drum element
                    for drum_part in drum_patterns[pattern_type]:
                        drum_name = drum_part["note"]
                        steps = drum_part["steps"]
                        
                        # Get the MIDI note number for this drum
                        if drum_name in drum_note_map:
                            note = drum_note_map[drum_name]
                            
                            # Add notes at each step
                            ppq = general.getRecPPQ()
                            
                            for step in steps:
                                pos_ticks = step * (ppq // 4)  # Convert to ticks (16th notes)
                                length_ticks = (ppq // 8)  # Very short for drums
                                
                                # Determine velocity based on drum and position
                                velocity = 100
                                if drum_name == "closed_hat":
                                    # Accent on beats
                                    velocity = 100 if step % 4 == 0 else 80
                                elif drum_name == "open_hat":
                                    velocity = 90
                                    
                                # Add the note
                                channels.addNote(DRUMS_CHANNEL, pos_ticks, length_ticks, note, velocity, 0)
                # For dict-style patterns
                else:
                    pattern = drum_patterns[pattern_type]
                    
                    # Add each drum element
                    for drum_name, steps in pattern.items():
                        # Get the MIDI note number for this drum
                        if drum_name in drum_note_map:
                            note = drum_note_map[drum_name]
                            
                            # Add notes at each step
                            ppq = general.getRecPPQ()
                            
                            for step in steps:
                                pos_ticks = step * (ppq // 4)  # Convert to ticks (16th notes)
                                length_ticks = (ppq // 8)  # Very short for drums
                                
                                # Determine velocity based on drum and position
                                velocity = 100
                                if drum_name == "closed_hat":
                                    # Accent on beats
                                    velocity = 100 if step % 4 == 0 else 80
                                elif drum_name == "open_hat":
                                    velocity = 90
                                    
                                # Add the note
                                channels.addNote(DRUMS_CHANNEL, pos_ticks, length_ticks, note, velocity, 0)
                
                print(f"Added {pattern_type} drum pattern")
                commit_pattern_changes()
            else:
                print(f"Unknown drum pattern: {pattern_type}")
                pattern_options = []
                for k in drum_patterns.keys():
                    pattern_options.append(k)
                print(f"Available patterns: {', '.join(pattern_options)}")
        else:
            print("Please specify a drum pattern type")
            pattern_options = []
            for k in drum_patterns.keys():
                pattern_options.append(k)
            print(f"Available patterns: {', '.join(pattern_options)}")
    
    # Full beat creation command
    elif cmd == "fullbeat":
        if args:
            try:
                style = args[0].lower()
                key = args[1].upper() if len(args) > 1 else "C"
                
                # Validate style
                valid_styles = ["pop", "trap", "house", "hiphop", "edm", "lofi"]
                if style not in valid_styles:
                    print(f"Unknown style: {style}. Using 'pop'")
                    style = "pop"
                
                # Create drum pattern based on style
                if style == "trap":
                    process_command("drums trap")
                elif style == "house":
                    process_command("drums house")
                elif style == "hiphop":
                    process_command("drums hiphop")
                elif style == "lofi":
                    process_command("drums lofi")
                else:  # pop or edm
                    process_command("drums basic")
                
                # Create bass pattern based on style
                root_bass = key
                if style == "trap":
                    process_command(f"bassline simple {root_bass}")
                elif style == "house":
                    process_command(f"bassline edm {root_bass}")
                elif style == "hiphop":
                    process_command(f"bassline groove {root_bass}")
                elif style == "lofi":
                    process_command(f"bassline walking {root_bass}")
                else:  # pop or edm
                    process_command(f"bassline octave {root_bass}")
                
                # Create chord progression based on style
                if style == "lofi":
                    # Select keys channel
                    channels.selectOneChannel(KEYS_CHANNEL)
                    if not configured_channels[KEYS_CHANNEL]:
                        configure_channel_instrument(KEYS_CHANNEL)
                    # Add lofi jazz chords
                    process_command(f"chord {key} min7 0 4")
                    process_command(f"chord {key} maj7 4 4")
                    process_command(f"chord {key} min7 8 4")
                    process_command(f"chord {key} 7 12 4")
                else:
                    # Select keys channel
                    channels.selectOneChannel(KEYS_CHANNEL)
                    if not configured_channels[KEYS_CHANNEL]:
                        configure_channel_instrument(KEYS_CHANNEL)
                    # Add standard chord progression
                    process_command(f"chord {key} maj 0 4")
                    process_command(f"chord {key} min 4 4")
                    process_command(f"chord {key} min 8 4")
                    process_command(f"chord {key} maj 12 4")
                
                # Add a pad for some styles
                if style in ["trap", "edm", "lofi"]:
                    process_command(f"pad {key} maj7")
                
                # Add arpeggio or lead for some styles
                if style in ["house", "edm"]:
                    process_command(f"arpeggio {key} maj 16th 1 up")
                elif style in ["trap", "hiphop"]:
                    process_command(f"lead {key} pent_minor melody1")
                
                print(f"Created full {style} beat in {key}")
                
            except Exception as e:
                print(f"Error creating full beat: {str(e)}")
        else:
            print("Format: fullbeat [style] [key]")
            print("Available styles: pop, trap, house, hiphop, edm, lofi")
            
    # Export command
    elif cmd == "export":
        print("Exporting project...")
        # In a real implementation, you'd use ui.exportWave() or similar
        print("Project exported")
        
    # Command to force UI refresh
    elif cmd == "refresh":
        ui.crDisplayRect()
        playlist.refresh()
        print("UI refreshed")
    
    # Quit command
    elif cmd in ["quit", "exit"]:
        print("Exiting terminal interface...")
        global running
        running = False
    
    # Unknown command
    else:
        print(f"Unknown command: {cmd}")
        print("Type 'help' for a list of commands")

def create_drum_pattern(pattern_type, channel):
    """Create a drum pattern based on pattern type"""
    # Process through the regular command interface
    channels.selectOneChannel(channel)
    process_command(f"drums {pattern_type}")
    return True

def show_help():
    """Display help information"""
    help_text = """
FL STUDIO ADVANCED CONTROLLER COMMANDS

PROJECT COMMANDS:
  new                  - Create a new project
  save                 - Save the current project
  bpm [tempo]          - Get or set the project tempo
  refresh              - Force UI refresh
  export               - Export project to audio

TRANSPORT COMMANDS:
  play                 - Start playback
  stop                 - Stop playback
  record               - Start recording
  loop [on|off|toggle] - Control loop mode

PATTERN COMMANDS:
  pattern              - Show current pattern
  pattern new          - Create a new pattern
  pattern select [num] - Select a pattern
  pattern clone [num]  - Clone a pattern
  pattern length [beats] - Set/get pattern length
  pattern refresh      - Force pattern refresh

CHANNEL COMMANDS:
  channel              - Show current channel
  channel select [num] - Select a channel
  channel add [type]   - Add new channel (sampler, plugin)
  channel name [name]  - Set/get channel name
  channel mute [num]   - Toggle mute on channel
  channel instrument [type] - Set channel as instrument type
                       (drums, bass, keys, lead, pad, arp, sub)

PLUGIN COMMANDS:
  plugin load [name]   - Load a plugin instrument
  plugin preset [name] - Load a plugin preset
  plugin param [index] [value] - Set plugin parameter

MUSICAL COMMANDS:
  note [name] [pos] [len] [vel] - Add a note (e.g., note C4 0 1 100)
  chord [root] [type] [pos] [len] - Add a chord (e.g., chord C maj 0 1)
  bassline [type] [root]  - Create bassline (e.g., bassline walking C)
                           Types: simple, octave, walking, edm, groove, dancehall
  arpeggio [root] [type] [speed] [len] [pattern] - Create arpeggio
                           (e.g., arpeggio C min 16th 1 up)
                           Patterns: up, down, updown, downup, random
  pad [root] [type]      - Create pad sound (e.g., pad C maj7)
  lead [root] [scale] [pattern] - Create lead melody
                           (e.g., lead C minor melody1)
                           Patterns: simple, melody1, melody2, arpeggio
  drums [pattern]        - Create drum pattern (e.g., drums trap)
                           Patterns: basic, breakbeat, trap, house, hiphop, lofi
  fullbeat [style] [key] - Create complete beat (e.g., fullbeat trap C)
                           Styles: pop, trap, house, hiphop, edm, lofi

GENERAL COMMANDS:
  help                 - Show this help
  quit/exit            - Exit terminal interface
"""
    print(help_text)

# Start the terminal interface when loaded in FL Studio
# No need to call this explicitly as OnInit will be called by FL Studio