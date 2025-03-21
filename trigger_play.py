# import mido
# from mido import Message
# import time

# # Open the output port to communicate with FL Studio
# output_port = mido.open_output('IAC Driver Bus 1')  # Replace with your port name

# # Bass note constants
# E1 = 40  # Low E (thump)
# A1 = 45  # A above low E (thump)
# D2 = 50  # D (pop)
# E2 = 52  # E (pop)
# G2 = 55  # G (pop)

# # Duration constants
# SIXTEENTH = 0.2   # Adjust tempo by changing this value
# EIGHTH = SIXTEENTH * 2
# QUARTER = SIXTEENTH * 4

# def play_note(note, duration, velocity=80):
#     """Play a note for specified duration"""
#     send_play_message(note, velocity)
#     time.sleep(duration)
#     send_stop_message(note)

# def send_play_message(note, velocity=80):
#     note_on = Message('note_on', note=note, velocity=velocity)
#     output_port.send(note_on)
#     print(f"Note ON: {note}")

# def send_stop_message(note):
#     note_off = Message('note_off', note=note, velocity=0)
#     output_port.send(note_off)
#     print(f"Note OFF: {note}")

# def play_slap_groove(loops=4):
#     """Play a funky slap bass groove"""
#     print("Starting slap bass groove...")
    
#     for loop in range(loops):
#         print(f"Loop {loop+1}/{loops}")
        
#         # Bar 1: Basic slap pattern
#         play_note(E1, EIGHTH, 100)       # Thumb slap on E
#         time.sleep(EIGHTH)            # Rest
#         play_note(A1, EIGHTH, 90)        # Thumb slap on A
#         play_note(G2, SIXTEENTH, 80)     # Pop high G
#         play_note(E1, EIGHTH, 100)       # Thumb slap on E
#         play_note(D2, SIXTEENTH, 75)     # Pop on D
#         play_note(A1, EIGHTH, 90)        # Thumb slap on A
#         play_note(E2, SIXTEENTH, 85)     # Pop on E
        
#         # Bar 2: Variation
#         play_note(E1, SIXTEENTH, 100)    # Quick thumb on E
#         play_note(E1, SIXTEENTH, 90)     # Quick thumb on E again
#         play_note(A1, EIGHTH, 85)        # Thumb on A
#         play_note(G2, EIGHTH, 80)     # Pop on G
#         play_note(G2, SIXTEENTH, 75)     # Pop on G again
#         play_note(E2, EIGHTH, 90)        # Longer pop on E
#         play_note(A1, EIGHTH, 100)       # Strong thumb on A
#         play_note(D2, EIGHTH, 85)        # Pop on D
    
#     print("Groove complete!")

# # Play the groove
# play_slap_groove()




import mido
import time

# Open a connection to FL Studio's MIDI input
# Use mido.get_output_names() to find the correct port name for your system
output_port = mido.open_output('IAC Driver Bus 1')  # Or 'IAC Driver Bus 1' on Mac

def play():
    """Send MIDI message to start playback in FL Studio"""
    # Send Note On for C3 (note 60)
    output_port.send(mido.Message('note_on', note=60, velocity=100))
    time.sleep(0.1)  # Small delay
    output_port.send(mido.Message('note_off', note=60, velocity=0))
    print("Sent Play command")

def stop():
    """Send MIDI message to stop playback in FL Studio"""
    # Send Note On for C#3 (note 61)
    output_port.send(mido.Message('note_on', note=61, velocity=100))
    time.sleep(0.1)  # Small delay
    output_port.send(mido.Message('note_off', note=61, velocity=0))
    print("Sent Stop command")

def record():
    """Send MIDI message to start recording in FL Studio"""
    # Send Note On for D3 (note 62)
    output_port.send(mido.Message('note_on', note=62, velocity=100))
    time.sleep(0.1)  # Small delay
    output_port.send(mido.Message('note_off', note=62, velocity=0))
    print("Sent Record command")

# Simple interface
while True:
    command = input("Enter command (play/stop/record/quit): ").strip().lower()
    if command == 'play':
        play()
    elif command == 'stop':
        stop()
    elif command == 'record':
        record()
    elif command == 'quit':
        break
    else:
        print("Unknown command")