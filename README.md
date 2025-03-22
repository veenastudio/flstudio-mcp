# flstudio-mcp
## Step 1: Create a listener for midi messages in FL studio
place the Test Controller folder in FL Studio/Settings/Hardware

Open FL Studio. Go To Options > MIDI Settings. In the Input Tab, click the MIDI Input you have (usually the first one). Change controller type from (generic controller) to Test Controller.

Ctrl+Alt+S to open script viewer. Click on the second tab (not Interpreter). it should have the same name as your MIDI Input. You can type in commands like play() to execute.


## Step 2: Create a python script to send messages to FL studio listener. 

run the `grid_trigger.py` file. (`python grid_trigger.py`). 

Make sure that the name of the midi port in the script matches the name of the midi port in the FL Studio MIDI settings. (e.g. 'IAC Driver Bus 1' for mac or 'loopMIDI Port' for windows)


Figure out a way to create a cursor MCP to connect with this controller 
Cursor Docs: https://docs.cursor.com/context/model-context-protocol#model-context-protocol

NOTE: run this command to install necessary stuff pip install FL-Studio-API-Stubs
