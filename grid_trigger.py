import mido
from mido import Message
import time

# Open the output port to communicate with FL Studio
# Replace with your port name - you may need to check available ports
port_name = 'IAC Driver Bus 1'  # Mac default
# port_name = 'FL STUDIO MIDI' # Common Windows name

try:
    output_port = mido.open_output(port_name)
    print(f"Successfully connected to {port_name}")
except Exception as e:
    print(f"Failed to connect to {port_name}: {str(e)}")
    print("Available ports:")
    print(mido.get_output_names())
    exit(1)

# MIDI Note mappings for FL Studio commands
NOTE_PLAY = 60          # C3
NOTE_STOP = 61          # C#3
NOTE_RECORD = 62        # D3
NOTE_NEW_PROJECT = 63   # D#3
NOTE_SET_BPM = 64       # E3
NOTE_NEW_PATTERN = 65   # F3
NOTE_SELECT_PATTERN = 66  # F#3
NOTE_ADD_CHANNEL = 67   # G3
NOTE_NAME_CHANNEL = 68  # G#3
NOTE_ADD_NOTE = 69      # A3
NOTE_ADD_TO_PLAYLIST = 70  # A#3
NOTE_SET_PATTERN_LEN = 71  # B3

# Define custom MIDI CC messages for direct step sequencer grid control
CC_SELECT_CHANNEL = 100  # Select which channel to edit
CC_SELECT_STEP = 110     # Select which step to edit
CC_TOGGLE_STEP = 111     # Toggle the selected step on/off
CC_STEP_VELOCITY = 112   # Set velocity for the selected step

# Drum sound MIDI notes
KICK = 36      # C1
SNARE = 38     # D1
CLAP = 39      # D#1
CLOSED_HAT = 42  # F#1
OPEN_HAT = 46  # A#1

# Send a MIDI note message
def send_midi_note(note, velocity=100, duration=0.1):
    """Send a MIDI note on/off message with specified duration"""
    note_on = Message('note_on', note=note, velocity=velocity)
    output_port.send(note_on)
    print(f"Sent MIDI note {note} (on), velocity {velocity}")
    time.sleep(duration)
    note_off = Message('note_off', note=note, velocity=0)
    output_port.send(note_off)
    print(f"Sent MIDI note {note} (off)")
    time.sleep(0.1)  # Small pause between messages

# Send a MIDI CC message
def send_midi_cc(control, value, channel=0):
    """Send a MIDI Control Change message"""
    if value > 127:
        print(f"Warning: Value {value} exceeds MIDI range (0-127)")
        value = 127
    cc = Message('control_change', channel=channel, control=control, value=value)
    output_port.send(cc)
    print(f"Sent CC: control={control}, value={value}")
    time.sleep(0.1)  # Small pause between messages

# Create a new channel with a name
def create_channel(name):
    """Create a new channel in FL Studio with the specified name"""
    print(f"Creating channel: {name}")
    
    send_midi_note(NOTE_ADD_CHANNEL)
    time.sleep(0.5)  # Longer delay for channel creation
    
    send_midi_note(NOTE_NAME_CHANNEL)
    time.sleep(0.2)
    
    for char in name:
        send_midi_cc(2, ord(char))
        time.sleep(0.05)
    
    send_midi_cc(2, 0)  # Terminator
    time.sleep(0.5)
    print(f"Channel '{name}' created successfully")

# Set a specific step in the step sequencer grid
def set_step(channel, step, enabled=True, velocity=100):
    """
    Set a step in the FL Studio step sequencer grid
    
    Args:
        channel: Channel index (0-based)
        step: Step index (0-15)
        enabled: Whether the step is active
        velocity: Velocity/level for the step (0-127)
    """
    print(f"Setting channel {channel}, step {step}, enabled={enabled}, velocity={velocity}")
    
    # Select the channel
    send_midi_cc(CC_SELECT_CHANNEL, channel)
    time.sleep(0.1)
    
    # Select the step
    send_midi_cc(CC_SELECT_STEP, step)
    time.sleep(0.1)
    
    # Enable/disable the step
    send_midi_cc(CC_TOGGLE_STEP, 1 if enabled else 0)
    time.sleep(0.1)
    
    # Set the velocity/level if the step is enabled
    if enabled:
        send_midi_cc(CC_STEP_VELOCITY, velocity)
        time.sleep(0.1)

# Create a simple 4/4 beat pattern
def create_basic_beat():
    """Create a simple 4/4 beat pattern with kick, snare, and hi-hat"""
    print("Creating a new drum pattern in FL Studio's Step Sequencer...")
    
    # 1. Create a new project
    send_midi_note(NOTE_NEW_PROJECT)
    time.sleep(2.0)  # Longer delay for project creation
    
    # 2. Set BPM to 90
    send_midi_note(NOTE_SET_BPM)
    send_midi_cc(1, 90)
    time.sleep(0.5)
    
    # 3. Create a new pattern
    send_midi_note(NOTE_NEW_PATTERN)
    time.sleep(0.5)
    
    # 4. Create channels
    create_channel("Kick")      # Channel 0
    create_channel("Clap")      # Channel 1
    create_channel("Hi-Hat")    # Channel 2
    create_channel("Snare")     # Channel 3
    
    # 5. Create kick pattern (every quarter note)
    print("Setting kick pattern...")
    for step in [0, 4, 8, 12]:  # Steps on beats 1, 2, 3, 4
        set_step(0, step, True, 100)
        time.sleep(0.2)
    
    # 6. Create clap pattern (beats 2 and 4)
    print("Setting clap pattern...")
    for step in [4, 12]:  # Steps on beats 2 and 4
        set_step(1, step, True, 90)
        time.sleep(0.2)
    
    # 7. Create hi-hat pattern (eighth notes)
    print("Setting hi-hat pattern...")
    for step in range(0, 16, 2):  # Steps on all eighth notes
        velocity = 90 if step % 4 == 0 else 70  # Accent on the beat
        set_step(2, step, True, velocity)
        time.sleep(0.2)
    
    # 8. Create snare pattern (beats 2 and 4)
    print("Setting snare pattern...")
    for step in [4, 12]:  # Steps on beats 2 and 4
        set_step(3, step, True, 95)
        time.sleep(0.2)
    
    # 9. Add pattern to playlist
    print("Adding pattern to playlist...")
    time.sleep(0.5)
    send_midi_note(NOTE_ADD_TO_PLAYLIST)
    time.sleep(0.2)
    send_midi_cc(10, 1)   # Pattern number
    time.sleep(0.1)
    send_midi_cc(11, 0)   # Position (0 bars)
    time.sleep(0.1)
    send_midi_cc(12, 0)   # Track 0
    time.sleep(0.5)
    
    # 10. Play the pattern
    print("Playing the pattern...")
    send_midi_note(NOTE_PLAY)
    
    print("Beat created successfully! You should see steps in the Channel Rack step sequencer.")

# Create a trap-style beat
def create_trap_beat():
    """Create a trap-style beat with hi-hat rolls and 808 kicks"""
    print("Creating a trap beat in FL Studio's Step Sequencer...")
    
    # 1. Create a new project
    send_midi_note(NOTE_NEW_PROJECT)
    time.sleep(2.0)
    
    # 2. Set BPM to 140 (typical trap tempo)
    send_midi_note(NOTE_SET_BPM)
    send_midi_cc(1, 140)
    time.sleep(0.5)
    
    # 3. Create a new pattern
    send_midi_note(NOTE_NEW_PATTERN)
    time.sleep(0.5)
    
    # 4. Create channels
    create_channel("808 Kick")   # Channel 0
    create_channel("Clap")       # Channel 1
    create_channel("Hi-Hat")     # Channel 2
    create_channel("Open Hat")   # Channel 3
    create_channel("808 Bass")   # Channel 4
    
    # 5. Create 808 kick pattern (trap style with ghost notes)
    print("Setting 808 kick pattern...")
    for step, velocity in [(0, 100), (6, 80), (8, 100), (14, 90)]:
        set_step(0, step, True, velocity)
        time.sleep(0.2)
    
    # 6. Create clap pattern (beats 2 and 4)
    print("Setting clap pattern...")
    for step in [4, 12]:
        set_step(1, step, True, 95)
        time.sleep(0.2)
    
    # 7. Create hi-hat pattern (trap style with rolls)
    print("Setting hi-hat pattern...")
    # Simple 16th note pattern with velocity variations
    velocities = [90, 60, 75, 60, 90, 60, 75, 60, 90, 60, 75, 60, 90, 60, 75, 60]
    for step, velocity in enumerate(velocities):
        set_step(2, step, True, velocity)
        time.sleep(0.2)
    
    # 8. Create open hi-hat accents
    print("Setting open hi-hat pattern...")
    for step in [2, 10]:
        set_step(3, step, True, 85)
        time.sleep(0.2)
    
    # 9. Create 808 bass pattern
    print("Setting 808 bass pattern...")
    for step, velocity in [(0, 100), (8, 95)]:
        set_step(4, step, True, velocity)
        time.sleep(0.2)
    
    # 10. Add pattern to playlist
    print("Adding pattern to playlist...")
    time.sleep(0.5)
    send_midi_note(NOTE_ADD_TO_PLAYLIST)
    time.sleep(0.2)
    send_midi_cc(10, 1)   # Pattern number
    time.sleep(0.1)
    send_midi_cc(11, 0)   # Position (0 bars)
    time.sleep(0.1)
    send_midi_cc(12, 0)   # Track 0
    time.sleep(0.5)
    
    # 11. Play the pattern
    print("Playing the pattern...")
    send_midi_note(NOTE_PLAY)
    
    print("Trap beat created successfully! You should see steps in the Channel Rack step sequencer.")

# Create a house beat
def create_house_beat():
    """Create a classic house beat with four-on-the-floor kick"""
    print("Creating a house beat in FL Studio's Step Sequencer...")
    
    # 1. Create a new project
    send_midi_note(NOTE_NEW_PROJECT)
    time.sleep(2.0)
    
    # 2. Set BPM to 128 (typical house tempo)
    send_midi_note(NOTE_SET_BPM)
    send_midi_cc(1, 128)
    time.sleep(0.5)
    
    # 3. Create a new pattern
    send_midi_note(NOTE_NEW_PATTERN)
    time.sleep(0.5)
    
    # 4. Create channels
    create_channel("Kick")       # Channel 0
    create_channel("Clap")       # Channel 1
    create_channel("Closed Hat") # Channel 2
    create_channel("Open Hat")   # Channel 3
    create_channel("Bass")       # Channel 4
    
    # 5. Create four-on-the-floor kick pattern
    print("Setting kick pattern...")
    for step in [0, 4, 8, 12]:
        set_step(0, step, True, 100)
        time.sleep(0.2)
    
    # 6. Create clap/snare on beats 2 and 4
    print("Setting clap pattern...")
    for step in [4, 12]:
        set_step(1, step, True, 90)
        time.sleep(0.2)
    
    # 7. Create closed hi-hat pattern (offbeats)
    print("Setting closed hi-hat pattern...")
    for step in [2, 6, 10, 14]:  # Offbeats
        set_step(2, step, True, 85)
        time.sleep(0.2)
    
    # 8. Create open hi-hat accents
    print("Setting open hi-hat pattern...")
    set_step(3, 7, True, 85)  # Single open hat accent
    time.sleep(0.2)
    
    # 9. Create simple bass pattern
    print("Setting bass pattern...")
    for step, velocity in [(0, 100), (4, 90), (8, 100), (12, 90)]:
        set_step(4, step, True, velocity)
        time.sleep(0.2)
    
    # 10. Add pattern to playlist
    print("Adding pattern to playlist...")
    time.sleep(0.5)
    send_midi_note(NOTE_ADD_TO_PLAYLIST)
    time.sleep(0.2)
    send_midi_cc(10, 1)   # Pattern number
    time.sleep(0.1)
    send_midi_cc(11, 0)   # Position (0 bars)
    time.sleep(0.1)
    send_midi_cc(12, 0)   # Track 0
    time.sleep(0.5)
    
    # 11. Play the pattern
    print("Playing the pattern...")
    send_midi_note(NOTE_PLAY)
    
    print("House beat created successfully! You should see steps in the Channel Rack step sequencer.")

if __name__ == "__main__":
    print("FL Studio Step Sequencer Grid Builder")
    print("1. Basic Beat")
    print("2. Trap Beat")
    print("3. House Beat")
    
    choice = input("Select a beat style (1-3): ")
    
    if choice == "1":
        create_basic_beat()
    elif choice == "2":
        create_trap_beat()
    elif choice == "3":
        create_house_beat()
    else:
        print("Invalid choice. Creating basic beat by default.")
        create_basic_beat()