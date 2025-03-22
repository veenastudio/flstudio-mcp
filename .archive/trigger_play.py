#trigger_play.py
#This is an older file. 
import mido
from mido import Message
import time
import random

# Open the output port to communicate with FL Studio
# Replace with your port name - you may need to check available ports
port_name = 'IAC Driver Bus 1'  # Mac default
# port_name = 'FL STUDIO MIDI' # Common Windows name

try:
    output_port = mido.open_output(port_name)
    print(f"Successfully connected to {port_name}")
except:
    print(f"Failed to connect to {port_name}")
    print("Available ports:")
    print(mido.get_output_names())
    exit(1)

# MIDI Note mappings (based on device_test.py)
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

# Drum sound MIDI notes
KICK = 36      # C1
SNARE = 38     # D1
CLAP = 39      # D#1
CLOSED_HAT = 42  # F#1
OPEN_HAT = 46  # A#1
LOW_TOM = 43   # G1
MID_TOM = 45   # A1
HIGH_TOM = 48  # C2
CRASH = 49     # C#2
RIDE = 51      # D#2
PERCUSSION = 54  # F#2

# Send a MIDI note message
def send_midi_note(note, velocity=100, duration=0.1):
    note_on = Message('note_on', note=note, velocity=velocity)
    output_port.send(note_on)
    print(f"Sent MIDI note {note} (on), velocity {velocity}")
    time.sleep(duration)
    note_off = Message('note_off', note=note, velocity=0)
    output_port.send(note_off)
    print(f"Sent MIDI note {note} (off)")
    time.sleep(0.1)  # Small pause between messages

# Send a MIDI CC message (for parameters)
def send_midi_cc(control, value, channel=0):
    # Ensure value is within MIDI range (0-127)
    if value > 127:
        print(f"Warning: Value {value} exceeds MIDI range (0-127)")
        return False
    
    cc = Message('control_change', channel=channel, control=control, value=value)
    output_port.send(cc)
    print(f"Sent CC: control={control}, value={value}")
    time.sleep(0.1)  # Small pause between messages
    return True

# Split a larger value into two MIDI CC messages (MSB/LSB)
def send_split_value(msb_control, lsb_control, value, channel=0):
    msb = value >> 7        # Most significant 7 bits
    lsb = value & 0x7F      # Least significant 7 bits
    
    send_midi_cc(msb_control, msb, channel)
    send_midi_cc(lsb_control, lsb, channel)
    print(f"Split value {value} into MSB={msb} and LSB={lsb}")

# Add a note to the pattern with proper timing
def add_note(note_value, position, length, velocity):
    print(f"Adding note: {note_value} at position {position}, length {length}, velocity {velocity}")
    
    # Calculate the step position for the channel rack grid (16 steps per bar)
    # This is critical for visual representation in the channel rack
    step_position = int((position / 100.0) * 16) % 16
    print(f"Step position in channel rack: {step_position}")
    
    # Send the add note command
    send_midi_note(NOTE_ADD_NOTE)
    time.sleep(0.2)  # Additional delay to ensure command is processed
    
    # Send note value (the MIDI note number)
    send_midi_cc(3, note_value)
    time.sleep(0.1)
    
    # Send position - for positions <= 127, we can send directly
    if position <= 127:
        send_midi_cc(4, position)
    else:
        # For larger positions, use the split value approach
        send_split_value(4, 5, position)
    time.sleep(0.1)
    
    # Send length - for lengths <= 127, we can send directly
    if length <= 127:
        send_midi_cc(6, length)
    else:
        # For larger lengths, use the split value approach
        send_split_value(6, 7, length)
    time.sleep(0.1)
    
    # Send velocity (always 0-127)
    send_midi_cc(8, velocity)
    
    # Add a specific CC to indicate this should be shown in the step sequencer
    # CC 9 will be used to tell FL Studio to add this to the step sequencer grid
    send_midi_cc(9, step_position)
    
    # Wait for FL Studio to process the note addition
    time.sleep(0.3)
    print(f"Note {note_value} added successfully at step {step_position}")

# Create a new channel and name it
def create_channel(name):
    print(f"Creating channel: {name}")
    
    # Send the add channel command
    send_midi_note(NOTE_ADD_CHANNEL)
    time.sleep(0.5)  # Longer delay for channel creation
    
    # Now name the channel
    send_midi_note(NOTE_NAME_CHANNEL)
    time.sleep(0.2)
    
    # Send each character of the name as a MIDI CC value
    for char in name:
        send_midi_cc(2, ord(char))
        time.sleep(0.05)
    
    # Send terminator (0) to indicate end of name
    send_midi_cc(2, 0)
    
    # Additional delay after naming to ensure it's processed
    time.sleep(0.5)
    print(f"Channel '{name}' created successfully")

# Build a basic trap beat (highly visible in FL Studio)
def create_trap_beat():
    print("Creating a trap beat in FL Studio...")
    
    # 1. Create a new project with sufficient delay
    send_midi_note(NOTE_NEW_PROJECT)
    time.sleep(2.0)  # Longer delay for project creation
    
    # 2. Set BPM to 140 (common for trap)
    send_midi_note(NOTE_SET_BPM)
    send_midi_cc(1, 140)
    time.sleep(0.5)
    
    # 3. Create a new pattern
    send_midi_note(NOTE_NEW_PATTERN)
    time.sleep(0.5)
    
    # 4. Set pattern length to 4 beats (1 bar)
    send_midi_note(NOTE_SET_PATTERN_LEN)
    send_midi_cc(1, 4)
    time.sleep(0.5)
    
    # 5. Create and add KICK DRUM pattern
    create_channel("808 Kick")
    
    # Trap style kick pattern
    add_note(KICK, 0, 30, 120)      # Beat 1 (strong)
    time.sleep(0.2)
    add_note(KICK, 75, 30, 90)      # Beat 1.75 (ghost note)
    time.sleep(0.2)
    add_note(KICK, 200, 30, 120)    # Beat 3
    time.sleep(0.2)
    add_note(KICK, 275, 30, 100)    # Beat 3.75 (ghost note)
    time.sleep(0.2)
    add_note(KICK, 350, 30, 80)     # Beat 4.5 (ghost note)
    time.sleep(0.5)  # Extra pause between instruments
    
    # 6. Create and add SNARE pattern
    create_channel("Snare")
    
    # Trap style snare
    add_note(SNARE, 100, 25, 110)   # Beat 2
    time.sleep(0.2)
    add_note(SNARE, 300, 25, 110)   # Beat 4
    time.sleep(0.5)  # Extra pause between instruments
    
    # 7. Create and add CLOSED HI-HAT pattern
    create_channel("Hi-Hat")
    
    # Trap style hi-hat pattern (16th notes with velocity variation)
    hihat_positions = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375]
    for i, pos in enumerate(hihat_positions):
        # Accented hi-hats on certain beats
        if i % 4 == 0:  # Every quarter note
            velocity = 100
        elif i % 2 == 0:  # Every 8th note
            velocity = 85
        else:  # Other 16th notes
            velocity = 70
        
        add_note(CLOSED_HAT, pos, 15, velocity)
        time.sleep(0.2)
    
    time.sleep(0.5)  # Extra pause between instruments
    
    # 8. Create and add OPEN HI-HAT for accents
    create_channel("Open Hat")
    
    # Add open hi-hats for groove
    add_note(OPEN_HAT, 50, 30, 90)   # Off-beat accent
    time.sleep(0.2)
    add_note(OPEN_HAT, 150, 30, 85)  # Off-beat accent
    time.sleep(0.2)
    add_note(OPEN_HAT, 250, 30, 90)  # Off-beat accent
    time.sleep(0.2)
    add_note(OPEN_HAT, 350, 30, 85)  # Off-beat accent
    time.sleep(0.5)  # Extra pause between instruments
    
    # 9. Add 808 bass (using a low tom as a substitute)
    create_channel("808 Bass")
    
    # 808 bass line (typical trap pattern)
    add_note(LOW_TOM - 12, 0, 100, 110)     # Longer 808 on beat 1
    time.sleep(0.2)
    add_note(LOW_TOM - 10, 200, 100, 100)   # Different note on beat 3
    time.sleep(0.5)  # Extra pause after all notes
    
    # 10. Add pattern to playlist
    print("Adding pattern to playlist...")
    time.sleep(1.0)  # Extra delay before adding to playlist
    send_midi_note(NOTE_ADD_TO_PLAYLIST)
    time.sleep(0.2)
    send_midi_cc(10, 1)   # Pattern number
    time.sleep(0.1)
    send_midi_cc(11, 0)   # Position (0 bars)
    time.sleep(0.1)
    send_midi_cc(12, 0)   # Track 0
    time.sleep(1.0)  # Extra delay after adding to playlist
    
    # 11. Play the pattern
    print("Playing the pattern...")
    time.sleep(0.5)
    send_midi_note(NOTE_PLAY)
    
    print("Trap beat created successfully and should be visible in FL Studio!")

# Build a half-time hip-hop beat
def create_hip_hop_beat():
    print("Creating a half-time hip-hop beat in FL Studio...")
    
    # 1. Create a new project
    send_midi_note(NOTE_NEW_PROJECT)
    time.sleep(2.0)  # Longer delay for project creation
    
    # 2. Set BPM to 85 (common for half-time hip-hop)
    send_midi_note(NOTE_SET_BPM)
    send_midi_cc(1, 85)
    time.sleep(0.5)
    
    # 3. Create a new pattern
    send_midi_note(NOTE_NEW_PATTERN)
    time.sleep(0.5)
    
    # 4. Set pattern length to 4 beats (1 bar)
    send_midi_note(NOTE_SET_PATTERN_LEN)
    send_midi_cc(1, 4)
    time.sleep(0.5)
    
    # 5. Create and add KICK DRUM pattern
    create_channel("Kick")
    
    # Hip-hop kick pattern
    add_note(KICK, 0, 30, 115)      # Beat 1
    time.sleep(0.2)
    add_note(KICK, 250, 30, 90)     # Beat 3.5
    time.sleep(0.2)
    add_note(KICK, 300, 30, 110)    # Beat 4
    time.sleep(0.5)  # Extra pause between instruments
    
    # 6. Create and add SNARE pattern
    create_channel("Snare")
    
    # Half-time snare
    add_note(SNARE, 200, 30, 110)   # Beat 3
    time.sleep(0.5)  # Extra pause between instruments
    
    # Add clap to strengthen snare
    create_channel("Clap")
    add_note(CLAP, 200, 25, 95)     # Beat 3
    time.sleep(0.5)  # Extra pause between instruments
    
    # 7. Create and add CLOSED HI-HAT pattern
    create_channel("Hi-Hat")
    
    # Hip-hop style hi-hat pattern (8th notes)
    hihat_positions = [0, 50, 100, 150, 200, 250, 300, 350]
    for pos in hihat_positions:
        # Accented hi-hats on certain beats
        if pos % 100 == 0:  # Downbeats
            velocity = 95
        else:
            velocity = 75
        
        add_note(CLOSED_HAT, pos, 15, velocity)
        time.sleep(0.2)
    
    time.sleep(0.5)  # Extra pause between instruments
    
    # 8. Create and add percussion for flavor
    create_channel("Perc")
    
    add_note(PERCUSSION, 150, 20, 85)  # Beat 2.5
    time.sleep(0.2)
    add_note(PERCUSSION, 350, 20, 90)  # Beat 4.5
    time.sleep(0.5)  # Extra pause between instruments
    
    # 9. Add a bass line
    create_channel("Bass")
    
    # Simple bass line
    add_note(38, 0, 90, 100)      # C note on beat 1
    time.sleep(0.2)
    add_note(43, 200, 90, 95)     # F note on beat 3
    time.sleep(0.5)  # Extra pause after all notes
    
    # 10. Add crash at the beginning
    create_channel("Crash")
    
    add_note(CRASH, 0, 120, 90)    # Crash on beat 1
    time.sleep(0.5)  # Extra pause after all notes
    
    # 11. Add pattern to playlist
    print("Adding pattern to playlist...")
    time.sleep(1.0)  # Extra delay before adding to playlist
    send_midi_note(NOTE_ADD_TO_PLAYLIST)
    time.sleep(0.2)
    send_midi_cc(10, 1)   # Pattern number
    time.sleep(0.1)
    send_midi_cc(11, 0)   # Position (0 bars)
    time.sleep(0.1)
    send_midi_cc(12, 0)   # Track 0
    time.sleep(1.0)  # Extra delay after adding to playlist
    
    # 12. Play the pattern
    print("Playing the pattern...")
    time.sleep(0.5)
    send_midi_note(NOTE_PLAY)
    
    print("Hip-hop beat created successfully and should be visible in FL Studio!")

# Build a four-on-the-floor house beat
def create_house_beat():
    print("Creating a house beat in FL Studio...")
    
    # 1. Create a new project
    send_midi_note(NOTE_NEW_PROJECT)
    time.sleep(2.0)  # Longer delay for project creation
    
    # 2. Set BPM to 126 (common for house)
    send_midi_note(NOTE_SET_BPM)
    send_midi_cc(1, 126)
    time.sleep(0.5)
    
    # 3. Create a new pattern
    send_midi_note(NOTE_NEW_PATTERN)
    time.sleep(0.5)
    
    # 4. Set pattern length to 4 beats (1 bar)
    send_midi_note(NOTE_SET_PATTERN_LEN)
    send_midi_cc(1, 4)
    time.sleep(0.5)
    
    # 5. Create and add KICK DRUM pattern
    create_channel("Kick")
    
    # Four-on-the-floor kick pattern
    for pos in [0, 100, 200, 300]:  # Beats 1, 2, 3, 4
        add_note(KICK, pos, 25, 110)
        time.sleep(0.2)
    
    time.sleep(0.5)  # Extra pause between instruments
    
    # 6. Create and add SNARE/CLAP pattern
    create_channel("Clap")
    
    # House clap on beats 2 and 4
    add_note(CLAP, 100, 25, 100)   # Beat 2
    time.sleep(0.2)
    add_note(CLAP, 300, 25, 100)   # Beat 4
    time.sleep(0.5)  # Extra pause between instruments
    
    # 7. Create and add closed hi-hat pattern
    create_channel("Closed Hat")
    
    # Off-beat 8th notes for hi-hats (classic house)
    for pos in [50, 150, 250, 350]:  # Off-beats
        add_note(CLOSED_HAT, pos, 15, 90)
        time.sleep(0.2)
    
    time.sleep(0.5)  # Extra pause between instruments
    
    # 8. Create and add open hi-hat for accent
    create_channel("Open Hat")
    
    # Single open hi-hat for accent
    add_note(OPEN_HAT, 250, 30, 85)  # Beat 3.5
    time.sleep(0.5)  # Extra pause between instruments
    
    # 9. Create and add ride cymbal for texture
    create_channel("Ride")
    
    # 16th note ride pattern for texture with varying velocities
    for i, pos in enumerate([0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375]):
        velocity = 75
        if i % 4 == 0:  # Accent on quarter notes
            velocity = 90
        elif i % 2 == 0:  # Lighter accent on 8th notes
            velocity = 80
            
        add_note(RIDE, pos, 15, velocity)
        time.sleep(0.2)
    
    time.sleep(0.5)  # Extra pause between instruments
    
    # 10. Add a simple bass line
    create_channel("Bass")
    
    # House bassline (simple version)
    add_note(36, 0, 25, 110)     # C note on beat 1
    time.sleep(0.2)
    add_note(36, 50, 25, 90)     # C note on beat 1.5
    time.sleep(0.2)
    add_note(43, 100, 25, 110)   # G note on beat 2
    time.sleep(0.2)
    add_note(43, 150, 25, 90)    # G note on beat 2.5
    time.sleep(0.2)
    add_note(36, 200, 25, 110)   # C note on beat 3
    time.sleep(0.2)
    add_note(36, 250, 25, 90)    # C note on beat 3.5
    time.sleep(0.2)
    add_note(43, 300, 25, 110)   # G note on beat 4
    time.sleep(0.2)
    add_note(48, 350, 25, 90)    # C note octave up on beat 4.5
    time.sleep(0.5)  # Extra pause after all notes
    
    # 11. Add pattern to playlist
    print("Adding pattern to playlist...")
    time.sleep(1.0)  # Extra delay before adding to playlist
    send_midi_note(NOTE_ADD_TO_PLAYLIST)
    time.sleep(0.2)
    send_midi_cc(10, 1)   # Pattern number
    time.sleep(0.1)
    send_midi_cc(11, 0)   # Position (0 bars)
    time.sleep(0.1)
    send_midi_cc(12, 0)   # Track 0
    time.sleep(1.0)  # Extra delay after adding to playlist
    
    # 12. Play the pattern
    print("Playing the pattern...")
    time.sleep(0.5)
    send_midi_note(NOTE_PLAY)
    
    print("House beat created successfully and should be visible in FL Studio!")

if __name__ == "__main__":
    print("FL Studio Beat Builder Script")
    print("1. Trap Beat")
    print("2. Hip-Hop Beat")
    print("3. House Beat")
    
    choice = input("Select a beat style (1-3): ")
    
    if choice == "1":
        create_trap_beat()
    elif choice == "2":
        create_hip_hop_beat()
    elif choice == "3":
        create_house_beat()
    else:
        print("Invalid choice. Creating trap beat by default.")
        create_trap_beat()