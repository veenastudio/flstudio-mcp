# device_test.py
# name=Test Controller

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

# Global variables
running = True
command_history = []
current_pattern = 0
current_channel = 0
terminal_active = False

channel_to_edit = 0
step_to_edit = 0

def OnInit():
    """Called when the script is loaded by FL Studio"""
    print("FL Studio Terminal Beat Builder initialized")
    print("Type 'help' for a list of commands")
    
    # Start the terminal input thread
    start_terminal_thread()
    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    global running
    running = False  # Signal the terminal thread to exit
    print("FL Studio Terminal Beat Builder deinitialized")
    return

def OnRefresh(flags):
    """Called when FL Studio's state changes or when a refresh is needed"""
    # Update terminal with current state if needed
    return

def OnMidiIn(event):
    """Called whenever the device sends a MIDI message to FL Studio"""
    print(f"MIDI In - Status: {event.status}, Data1: {event.data1}, Data2: {event.data2}")
    return


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
            channels.setStepLevel(channel_to_edit, step_to_edit, velocity)
            print(f"Set step level for channel {channel_to_edit}, step {step_to_edit} to {velocity}")
            commit_pattern_changes()  # Force UI update
            event.handled = True
        
        # Process other CC messages with existing code
        else:
            # Handle other CC messages with your existing code...
            pass
    
    # Handle Note On messages with your existing code...
    # [rest of your existing OnMidiMsg function]

# Make sure your commit_pattern_changes function is defined:
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
    
    print("\n===== FL STUDIO TERMINAL BEAT BUILDER =====")
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
            current_tempo = mixer.getTempo()
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
            new_pattern = patterns.findFirstEmpty()
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
                    new_pattern = patterns.findFirstEmpty()
                    patterns.copyPattern(source_pattern, new_pattern)
                    patterns.jumpTo(new_pattern)
                    print(f"Cloned pattern {source_pattern} to {new_pattern}")
                except ValueError:
                    print("Invalid pattern number")
            else:
                source_pattern = patterns.patternNumber()
                new_pattern = patterns.findFirstEmpty()
                patterns.copyPattern(source_pattern, new_pattern)
                patterns.jumpTo(new_pattern)
                print(f"Cloned current pattern to {new_pattern}")
        elif subcmd == "length":
            if len(args) > 1:
                try:
                    beats = int(args[1])
                    patterns.setPatternLength(beats)
                    print(f"Set pattern length to {beats} beats")
                except ValueError:
                    print("Invalid beat count")
            else:
                print(f"Current pattern length: {patterns.getPatternLength()} beats")
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
                    new_channel = channels.addChannel(channels.CH_Sampler)
                elif preset_type == "plugin":
                    new_channel = channels.addChannel(channels.CH_Plugin)
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
    
    # Note commands
    elif cmd == "note":
        if len(args) >= 3:
            try:
                note_name = args[0].upper()
                position = float(args[1])
                length = float(args[2])
                
                # Convert note name to MIDI note number
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
    
    # Playlist commands
    elif cmd == "playlist":
        if not args:
            print("Please specify a playlist subcommand")
            return
            
        subcmd = args[0].lower()
        if subcmd == "add":
            if len(args) > 1:
                try:
                    pattern_num = int(args[1])
                    position = float(args[2]) if len(args) > 2 else 1
                    track = int(args[3]) if len(args) > 3 else 0
                    
                    # Calculate position in PPQ
                    ppq = general.getRecPPQ()
                    pos_ticks = int(position * ppq * 4)  # Convert bars to ticks
                    
                    playlist.addPattern(pattern_num, pos_ticks, track)
                    playlist.refresh()  # Force playlist to update
                    print(f"Added pattern {pattern_num} at position {position} on track {track}")
                except ValueError:
                    print("Invalid parameters. Format: playlist add [pattern] [position] [track]")
            else:
                print("Please specify a pattern number")
        elif subcmd == "clear":
            playlist.clearPlaylist()
            print("Cleared playlist")
            playlist.refresh()  # Force playlist to update
        elif subcmd == "refresh":
            playlist.refresh()
            print("Playlist refreshed")
    
    # Mixer commands
    elif cmd == "mixer":
        if not args:
            print(f"Current mixer track: {mixer.trackNumber()}")
            return
            
        subcmd = args[0].lower()
        if subcmd == "select":
            if len(args) > 1:
                try:
                    track_num = int(args[1])
                    mixer.setTrackNumber(track_num)
                    print(f"Selected mixer track {track_num}")
                except ValueError:
                    print("Invalid track number")
            else:
                print("Please specify a track number")
        elif subcmd == "volume":
            if len(args) > 1:
                try:
                    volume = float(args[1])  # 0.0 to 1.0
                    track = mixer.trackNumber()
                    mixer.setTrackVolume(track, volume)
                    print(f"Set mixer track {track} volume to {volume}")
                except ValueError:
                    print("Invalid volume value (0.0 to 1.0)")
            else:
                track = mixer.trackNumber()
                volume = mixer.getTrackVolume(track)
                print(f"Mixer track {track} volume: {volume}")
                
    # Command to force UI refresh
    elif cmd == "refresh":
        ui.crDisplayRect()
        playlist.refresh()
        print("UI refreshed")
    
    # Command to save the project
    elif cmd == "save":
        ui.saveNew()
        print("Project saved")
    
    # Quit command
    elif cmd in ["quit", "exit"]:
        print("Exiting terminal interface...")
        global running
        running = False
    
    # Unknown command
    else:
        print(f"Unknown command: {cmd}")
        print("Type 'help' for a list of commands")

def show_help():
    """Display help information"""
    help_text = """
FL STUDIO TERMINAL BEAT BUILDER COMMANDS

PROJECT COMMANDS:
  new                  - Create a new project
  save                 - Save the current project
  bpm [tempo]          - Get or set the project tempo
  refresh              - Force UI refresh

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

NOTE COMMANDS:
  note [name] [pos] [len] [vel] - Add a note (e.g., note C4 0 1 100)

PLAYLIST COMMANDS:
  playlist add [pat] [pos] [track] - Add pattern to playlist
  playlist clear                   - Clear playlist
  playlist refresh                 - Force playlist refresh

MIXER COMMANDS:
  mixer                - Show current mixer track
  mixer select [num]   - Select a mixer track
  mixer volume [val]   - Set/get mixer track volume

GENERAL COMMANDS:
  help                 - Show this help
  quit/exit            - Exit terminal interface
"""
    print(help_text)

# Start the terminal interface when loaded in FL Studio
# No need to call this explicitly as OnInit will be called by FL Studio