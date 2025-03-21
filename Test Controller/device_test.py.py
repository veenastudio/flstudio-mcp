# device_test.py
# name=Test Controller
import transport
import ui
import midi

def OnInit():
    """Called when the script is loaded by FL Studio"""
    print("Test Controller initialized")
    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    print("Test Controller deinitialized")
    return

def OnRefresh(flags):
    """Called when FL Studio's state changes or when a refresh is needed"""
    print("Test Controller refreshed")
    return

def OnMidiIn(event):
    """
    Called whenever the device sends a MIDI message to FL Studio
    
    Args:
        event: The MIDI event object
    """
    print(f"MIDI In - Status: {event.status}, Data1: {event.data1}, Data2: {event.data2}")
    return

def OnMidiMsg(event, timestamp):
    """
    Called when a processed MIDI message is received
    
    Args:
        event: The MIDI event object
        timestamp: Time of the MIDI event
    """
    return

def OnIdle():
    """Called during FL Studio's idle processing time"""
    return

def OnUpdateBeatIndicator(value):
    """
    Called on every beat during playback
    
    Args:
        value: Beat indicator value
    """
    return

def OnDisplayZone(zone):
    """
    Called when a display zone needs updating
    
    Args:
        zone: The zone to update
    """
    return

def OnTransport(isPlaying):
    """
    Called when the transport state changes (play/stop)
    
    Args:
        isPlaying: Boolean indicating if the transport is playing
    """
    print(f"Transport state changed: {'Playing' if isPlaying else 'Stopped'}")
    return

def OnProgramChange(progNum):
    """
    Called when a program change message is received
    
    Args:
        progNum: Program number
    """
    return

def OnTempoChange(tempo):
    """
    Called when the tempo changes
    
    Args:
        tempo: New tempo value
    """
    print(f"Tempo changed to: {tempo} BPM")
    return

def OnControlChange(event):
    """
    Called when a control change message is received
    
    Args:
        event: The control change event object
    """
    return

def OnNoteOn(event):
    """
    Called when a note on message is received
    
    Args:
        event: The note on event object
    """
    return

def OnNoteOff(event):
    """
    Called when a note off message is received
    
    Args:
        event: The note off event object
    """
    return

def OnPitchBend(event):
    """
    Called when a pitch bend message is received
    
    Args:
        event: The pitch bend event object
    """
    return

def OnSysEx(event):
    """
    Called when a system exclusive message is received
    
    Args:
        event: The SysEx event object
    """
    return

# Transport control functions
def play():
    """Starts playback in FL Studio"""
    transport.start()
    return

def stop():
    """Stops playback in FL Studio"""
    transport.stop()
    return

def record():
    """Starts recording in FL Studio"""
    transport.record()
    return

def pause():
    """Pauses playback in FL Studio"""
    transport.stop(1)  # 1 = pause mode
    return

def rewind():
    """Rewinds in FL Studio"""
    transport.rewind()
    return

def fast_forward(startStop, flags=midi.GT_All):
    """
    Fast forward in FL Studio
    
    Args:
        startStop: Whether to start or stop fast-forwarding
        flags: Global transport flags
    """
    transport.fastForward(startStop, flags)
    return