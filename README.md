# flstudio-mcp

# This is an MCP server that connect to FL Studio.
Made this in 3 days. We're open sourcing it to see what we can actually get out of it. The possibilities are endless.

## If you're running to any issues, join our discord and we can setup it for you.

## Step 1: Download the Files
You should see two main items. 
- A folder called Test Controller
- A python file called trigger.py

The Test Controller folder has a file called device_test.py that receives information from the MCP server.

trigger.py is the MCP server.
  
Place the Test Controller folder in Image-Line/FL Studio/Settings/Hardware (Don't change the name of this file or folder)

## Step 2: Set up MCP for Claude
Follow this tutorial to see how to setup MCP servers in Claude. 

https://modelcontextprotocol.io/quickstart/server

If the Hammer icon doesn't show up, open Task Manager and force close the Claude process.

It should then show up.

## Step 3: set Up Virutal MIDI Ports
For Windows, download LoopMIDI from here

https://www.tobias-erichsen.de/software/loopmidi.html

Install LoopMIDI and add a port using the + button.

This is what mine looks like:
![loopmidi2](https://github.com/user-attachments/assets/fdc2770f-e07a-4b19-824b-56de8a4aa2c3)

## Step 4: Setup MIDI Controller
Open FL Studio.

Go To Options > MIDI Settings.

In the Input Tab, click the MIDI Input you just created with LoopMIDI.

Change controller type from (generic controller) to Test Controller.

## Step 5: Download Packages
Go to the folder with the trigger.py file. (This is the MCP Server file)

Run this command to download the necessary packages: uv pip install httpx mido python-rtmidi typing fastmcp
(uv should be installed from the Claude MCP setup)

## Step 6: Verify MCP Connection
Tell claude to get available MIDI ports.

This should use the MCP to get the ports from FL Studio.

If Windows, copy the port you created with LoopMIDI and the number in front of it.

![loopmidi](https://github.com/user-attachments/assets/a14b0aaa-5127-47c9-b041-fcb5a70339d9)

In my case, I copy loopMIDI Port 2

Open trigger.py in a text editor and replace the default port with the name of the port you just copied.
output_port = mido.open_output('loopMIDI Port 2') 

## Step 7: Make Music

Use the MCP to send melodies, chords, drums, etc.

I tend to use this prompt when I start a new chat: Here is format for notes: note(0-127),velocity(0-100),length in beats(decimal),position in beats(decimal)





Figure out a way to create a cursor MCP to connect with this controller 
Cursor Docs: https://docs.cursor.com/context/model-context-protocol#model-context-protocol

NOTE: run this command to install necessary stuff pip install FL-Studio-API-Stubs
