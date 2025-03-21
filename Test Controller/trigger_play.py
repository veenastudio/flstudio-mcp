import mido
from mido import Message
import time

# Open the output port to communicate with FL Studio
output_port = mido.open_output('IAC Driver')  # Replace with your port name

# Send a "Play" message (e.g., when you press a key on your MIDI controller)
def send_play_message():
    # This will send a simple Note On message to FL Studio (can be mapped to 'Play')
    note_on = Message('note_on', note=60, velocity=64)  # Middle C with medium velocity
    output_port.send(note_on)
    print("Sent Play message")

# Send a "Stop" message (e.g., when you press another key)
def send_stop_message():
    # This will send a "Note Off" message (can be mapped to 'Stop')
    note_off = Message('note_off', note=60, velocity=64)
    output_port.send(note_off)
    print("Sent Stop message")

# Test Play and Stop messages (this is just an example)
send_play_message()
time.sleep(2)  # Wait for 2 seconds
send_stop_message()
