This file contains documentation for the FL Studio API Stubs (https://github.com/IL-Group/FL-Studio-API-Stubs).

--- 
# Getting started with MIDI Controller Scripting

!!! NOTE
    This tutorial is for writing your own MIDI Controller Scripts. If you're
    looking to install an existing script, check out [this tutorial](./installing_scripts.md)
    instead.

If you use a MIDI controller with FL Studio, it can be frustrating when it
doesn’t work correctly out of the box. Fortunately, FL Studio includes a
feature called MIDI Controller Scripting, which lets us add support for any
MIDI device that FL Studio is capable of communicating with.

This tutorial covers some basic features of MIDI Controller Scripting and walks
you through the process of writing a simple script that links transport
buttons on your MIDI Controller to control FL Studio. While this tutorial
doesn't expect much knowledge of programming or the Python programming
language, you'll need to learn these if you want to take your program further.

The specific controller I will be writing a script for is the Novation
Launchkey Mini Mk3, but the steps should apply for any MIDI controller.

## First steps

Before you get started, there are a couple of things you should do to get
yourself set up.

* Check the [working script list](https://forum.image-line.com/viewtopic.php?t=228179)
  on the [Image-Line forums](https://forum.image-line.com/) to see if your
  controller is already supported by an existing script.

* If you're planning on sharing your script with others, consider resetting
  your controller to its factory defaults or exporting its settings to a file
  using its configuration program. This is important since otherwise your
  script may not work for others.

* Install a code editor to work effectively with your code. A great option is
  [Visual Studio Code](https://code.visualstudio.com), which offers excellent
  support for any features you'll need when working on MIDI Controller Scripts.

* Install [Python](https://python.org) and then follow the
  [installation instructions](/installation.md) in order to get intelligent
  suggestions and documentation as you write your code.

## Creating a device folder

Open up your MIDI Controller Scripts folder. This can be found within your
[Image-Line data directory](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/envsettings_files.htm#userdata)
at `Image-Line/FL Studio/Settings/Hardware`. From there, create a new folder
based on the name of your script. For example, I called my one `Demo device`.

| Platform | Example |
|----------|---------|
| Windows  | ![A screenshot of the Windows file explorer, showing a new "Demo device" folder](./getting_started/script_folder.png) |
| MacOS    | ***TODO*** |

## Starter code

Open your new folder in your text editor of choice. In VS Code, you can use
`File > Open Folder` then select the folder you created.

From there, create a new Python file with the name of your device, based on
this template: `device_[name].py`. For example, I named my file
`device_launchkey.py`.

Open this file and copy the starter code across.

??? code "Click to view the starter code"

    ```py linenums="1"
    # name=Demo Device (Starter)
    # url=TODO
    """
    This is a simple starter script that provides some tooling to simplify the
    process of creating a MIDI script to add basic support to your MIDI
    controllers.

    Authors:
    * Maddy Guthridge
    * Your Name
    """


    def OnMidiIn(event):
        """
        Called whenever your device sends a MIDI message to FL Studio
        """
        # TODO: follow the tutorial to add logic for handling events here

        # Print out the information about this event
        print_event(event)


    def print_event(event):
        """
        Prints information about MIDI events

        You shouldn't need to modify this function. If this code doesn't make sense
        to you, that is ok, since it is beyond the scope of the tutorial.
        """
        # If there is sysex data in the event, tell the user that we don't cover
        # that in this tutorial
        if event.sysex is not None:
            sysex = event.sysex
            print(f"Event: sysex={[hex(b) for b in sysex]}")
            print("Note that sysex events are somewhat more complex than standard "
                "events, and are beyond the scope of the tutorial.")
        # Otherwise print out the info
        else:
            # Assign variables to get the info
            status = event.status
            data1 = event.data1
            data2 = event.data2
            handled = event.handled
            # Then use a formatted string to print out the info in a readable
            # format
            print(f"Event: {status=:3}, {data1=:3}, {data2=:3}, handled={bool(handled)}")

        # Add an extra blank line for readability
        print()
    ```

### A look at the starter code

Let's take a moment to familiarize ourselves with this code. Don't worry if you
don't understand all of it - as long as you grasp the basics, you'll be fine!

```py  linenums="1"
# name=Demo Device (Starter)
# url=TODO
```

These lines contain information about the name and help URL for your script.
You should set the `name` to be the name of your MIDI controller, and you can
set the `url` to any URL within the Image-Line forums - once you've finished
your script, you can make this link to your post where you share your awesome
work!

Below them, you can see documentation which you can edit to contain information
about your work, such as how to use it, as well as the author and copyright
information.

After this is the definition for the `OnMidiIn` function. You can see it is
documented as `Called whenever your device sends a MIDI message to FL Studio`,
and contains some comments as well as a single call to `print_event`.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    # TODO: follow the tutorial to add logic for handling events here

    # Print out the information about this event
    print_event(event)
```

This is the function we'll be modifying in order to make our script handle
incoming events.

Finally, we have a definition for `print_event`, which is a function that we'll
use to display information about incoming events. Note that there is no need
to understand this function, but if you're interested, it is thoroughly
commented to explain how it works.

```py linenums="24"
def print_event(event):
    ...
```

### Assigning your device to the script

We should now assign our script to work with FL Studio. Launch FL Studio, or if
it was already open, close it an re-open it. Then, open the MIDI Settings and
find your device in the lists of inputs and outputs.

Set the port number for your device's inputs and outputs to numbers of your
choice. The value shouldn't matter as long as it is unique, and the input port
matches the output port for each device.

Then, with the input selected, you should use the script drop-down to select
your script. This should have the same name as you entered in the comment
earlier.

If your device has two MIDI ports, try assigning the script to the first port,
as this is more likely to be the one that receives the messages you need.

This screenshot contains the setup I used to get my device working correctly.

![A screenshot of FL Studio's MIDI Settings, showing the script correctly loaded](./getting_started/midi_settings.png)

To validate your setup, you should now open `View > Script output` and select
your MIDI Controller from the tabs. If it is working correctly, you should see
output appear as you press buttons on your controller.

!!! info "Expected output"

    ```txt
    FL Studio Midi scripting version: 35
    "C:\Users\migue\Documents\Image-Line\FL Studio\Settings\Hardware\Demo Device\device_demo.py"
    Event: status=191, data1=115, data2=127, handled=False

    Event: status=191, data1=115, data2=  0, handled=False
    ```

## Writing our script

Now it's time to start programming. We can use the output from our script to
get the information we need to be able to link up all the buttons on our
controller. If the output ever gets too cluttered, you can always click the
`Clear output` button in the bottom left of the output window.

### Investigating our device

Try pressing and releasing the play button of your device. On many controllers,
including mine, this will send two events - one for when you press the button,
and another for when you release it.

```txt
Event: status=191, data1=115, data2=127, handled=False
Event: status=191, data1=115, data2=  0, handled=False
```

If your device didn't send any MIDI messages, you should try assigning your
script to a different MIDI port in FL Studio's MIDI settings.

Each event can often be identified using the `status` and `data1` values, with
`data2` containing additional information about the event, and my controller is
no different: the play button is identified as `status=191, data1=115`, with
`data2=127` for a press and `data2=0` for a release.

Write your results down so you can use them later.

### Linking the play button

Let's write some code that can identify the play button. We can add an `if`
statement to our `OnMidiIn` function so that it matches events with the right
`status` and `data1` values to be a play button.

Inside this `if` statement, you can see we call the `print` function, which is
used to write information to the script output. In this case, we are printing
`"You pressed the play button"`.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    if event.status == 191 and event.data1 == 115:
        print("You pressed the play button")

    # ... rest of the code
```

!!! warning "Careful"

    Be sure to add a colon `:` at the end of your `if` statement, and to use a
    `==` (double equals) operator to check if the values match.

After you've written similar code to match the play button, try pressing
`Reload script` in the script output. Now each time you press the play button,
it should display that you did in the output.

```txt
You pressed the play button
Event: status=191, data1=115, data2=127, handled=False
```

Great! Now all we need to do is link it to a feature in FL Studio. To access FL
Studio's playback and other transport features, we need to `import` the
[`transport`][transport] module. Right after your opening documentation, add
the following code to access this module.

```py linenums="12"
import transport
```

Now instead of `print`ing information, we can instead start playback when our
user hits the play button. Modify your `if` statement so that it calls
[`transport.start()`][transport.start] instead of `print`.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    if event.status == 191 and event.data1 == 115:
        transport.start()

    # ... rest of the code
```

After you reload your script, try slowly pressing and releasing the play
button. Notice that FL Studio only plays while the button is pressed down. This
is because a second call to [`transport.start()`][transport.start] pauses
playback when the button gets lifted. Let's fix this by adding an additional
check to ensure that we only start playback when the button gets pressed.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    if event.status == 191 and event.data1 == 115:
        # Note that we are checking if `data2` is greater than zero -- this is
        # because some controllers could send other values to indicate a press,
        # especially if the button is velocity-sensitive.
        if event.data2 > 0:
            transport.start()

    # ... rest of the code
```

Hit reload and try again -- it should work now! Finally, let's tell FL Studio
that it's safe to ignore the event, since we have handled it. To do this, you
can set [`event.handled = True`][fl_classes.FlMidiMsg.handled]. Let's also add
a comment to remind us that this code is for the play button, so that we can
remember what it is for if we come back to this code in the distant future.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    # PLAY BUTTON
    if event.status == 191 and event.data1 == 115:
        if event.data2 > 0:
            transport.start()
        # Notice that I mark the event as handled, even for releases of the
        # button -- we don't want FL Studio to do anything about those.
        event.handled = True

    # ... rest of the code
```

### Linking the record button

Now that we've got the play button handled, let's link the record button. Since
we know that if the user pressed the play button, their button press won't have
been the record button, we can use an `elif` statement to make our check
exclusive to the play button.

Perform the steps from [investigating our device](#investigating-our-device)
again on the record button, and take note of your results. For me, the event
was identified as `status=191, data1=117`.

Then, you can handle the record button by calling
[`transport.record()`][transport.record]. We'll use similar logic to ignore
button releases, and to mark the event as handled.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    # PLAY BUTTON
    if event.status == 191 and event.data1 == 115:
        if event.data2 > 0:
            transport.start()
        event.handled = True
    # RECORD BUTTON
    elif event.status == 191 and event.data1 == 117:
        if event.data2 > 0:
            transport.record()
        event.handled = True

    # ... rest of the code
```

Once again, test your work by hitting save, then reloading the script in FL
Studio.

### Linking fast-forward and rewind

Fast-forward and rewind buttons usually behave slightly differently to other
buttons. This is because they should only be active when they are pressed down,
and should stop once they are lifted. To accomplish this, we can add an `else`
statement after our check for the `data2` value.

For the fast-forward button, we should call [`transport.fastForward(2)`][transport.fastForward]
when the button is pressed to start fast-forwarding, and then
`transport.fastForward(0)` when it is released to stop.

```py  linenums="14"
def OnMidiIn(event):
    """
    Called whenever your device sends a MIDI message to FL Studio
    """
    # PLAY BUTTON
    if event.status == 191 and event.data1 == 115:
        if event.data2 > 0:
            transport.start()
        event.handled = True
    # RECORD BUTTON
    elif event.status == 191 and event.data1 == 117:
        if event.data2 > 0:
            transport.record()
        event.handled = True
    # FAST FORWARD BUTTON
    elif event.status == 191 and event.data == 113:
        if event.data2 > 0:
            transport.fastForward(2)
        else:
            transport.fastForward(0)
        event.handled = True

    # ... rest of the code
```

Finally, we can use similar logic for the rewind button by calling
[`transport.rewind`][transport.rewind] instead.

This is all that we'll be implementing in this tutorial.

??? code "Click to reveal the finished code"

    ```py linenums="1"
    # name=Demo Device (Complete)
    # url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """
    This is a simple starter script that provides some tooling to simplify the
    process of creating a MIDI script to add basic support to your MIDI
    controllers.

    Authors:
    * Maddy Guthridge
    """
    import transport

    def OnMidiIn(event):
        """
        Called whenever your device sends a MIDI message to FL Studio
        """

        # PLAY BUTTON
        if event.status == 191 and event.data1 == 115:
            # If event.data2 is greater than zero, that means they're pressing the
            # button, so we should start playback
            if event.data2 > 0:
                transport.start()
            # Let's mark the event as handled either way, so that FL Studio doesn't
            # also try to handle it for us
            event.handled = True

        # RECORD BUTTON
        elif event.status == 191 and event.data1 == 117:
            if event. data2 > 0:
                transport.record()
            event.handled = True

        # FAST FORWARD BUTTON
        elif event.status == 191 and event.data1 == 113:
            if event. data2 > 0:
                transport.fastForward(2)
            else:
                transport.fastForward(0)
            event.handled = True

        # REWIND BUTTON
        elif event.status == 191 and event.data1 == 112:
            if event. data2 > 0:
                transport.rewind(2)
            else:
                transport.rewind(0)
            event.handled = True

        # Print out the information about this event
        # IMPORTANT: This is commented out as printing information continuously
        # can be quite laggy

        # print_event(event)


    def print_event(event):
        """
        Prints information about MIDI events

        You shouldn't need to modify this function. If this code doesn't make sense
        to you, that is ok, since it is beyond the scope of the tutorial.
        """
        # If there is sysex data in the event, tell the user that we don't cover
        # that in this tutorial
        if event.sysex is not None:
            sysex = event.sysex
            print(f"Event: {sysex=}")
            print("Note that sysex events are somewhat more complex than standard "
                "events, and are beyond the scope of the tutorial.")
        # Otherwise print out the info
        else:
            # Assign variables to get the info
            status = event.status
            data1 = event.data1
            data2 = event.data2
            handled = event.handled
            # Then use a formatted string to print out the info in a readable
            # format
            print(f"Event: {status=:02}, {data1=:02}, {data2=:02}, {handled=}")

        # Add an extra blank line for readability
        print()
    ```

## Where to from here?

There are so many more things you can do with MIDI Controller Scripting. Here
are some ideas:

* Learn more Python so you can write more advanced and powerful scripts.
  ([This video](https://www.youtube.com/watch?v=rfscVS0vtbw) is an excellent
  resource).

* Link more of your controller's buttons to FL Studio. For inspiration, some
  functions you could look at are [`transport.setLoopMode()`][transport.setLoopMode],
  [`ui.next()`][ui.next], and [`ui.previous()`][ui.previous].

* Configure your script so that it gets [set up automatically](./automatic_script_setup.md)
  by FL Studio when a compatible device is connected.

* Look for a "programmer's manual" for your device, which will have essential
  information required for taking full control of your device. Not all devices
  have these, but they are invaluable when they are made available, so it is
  worth looking.

* Use the functions in the [`device`][device] module to send MIDI messages back
  to your device, potentially allowing you to control its LEDs and screen.

* Share your hard work with the world: check out the
  [sharing your script tutorial](./sharing_scripts.md) for instructions.

* Enjoy your device's new integration with FL Studio.



---

# Event mapping

FL Studio uses an advanced system mapping events from hardware controls to
software controls, which can be confusing to use without an explanation.

## Control IDs

These represent the unique identifier of a single hardware control within FL
Studio. They are formed from a port number, a MIDI channel and a CC number,
which are encoded as follows:

```py
cc + (channel << 16) + ((port + 1) << 22)
```

This encoding can be calculated using the
[`midi.EncodeRemoteControlID`][midi.EncodeRemoteControlID] function.

## Event IDs

FL Studio maps events using event IDs, which represent the unique identifier of
a single software control. When automating these controls, event IDs are mapped
to control IDs. You can determine this link using the
[`device.findEventID`][device.findEventID] function.

From this, several functions are available to interact with FL Studio using
event IDs.

* [`device.getLinkedValue`][device.getLinkedValue]: get the value associated
  with this event ID.
* [`device.getLinkedValueString`][device.getLinkedValueString]: get the value
  associated with this event ID as a string.
* [`device.getLinkedParamName`][device.getLinkedParamName]: get the name of
  the parameter linked with this event ID.
* [`device.getLinkedInfo`][device.getLinkedInfo]: get info about the parameter
  linked with this event ID.
* [`ui.openEventEditor`][ui.openEventEditor]: open an event editor window for
  the control associated with this event ID.
* [`channels.getRecEventId`][channels.getRecEventId]: return the base value
  for event IDs associated with this channel.
* [`channels.incEventValue`][channels.incEventValue]: get an event value
  increased by a step.
* [`general.processRECEvent`][general.processRECEvent]: let FL Studio handle a
  change to the value of this event ID.



---

# Time units used within FL Studio

FL Studio uses many different time formats, and it is important to understand
them all, so that your scripts can correctly interpret time-related data.

## Beats

A beat represents a musical beat, the central unit of time when playing live
music.

## Bars

A bar is a collection of beats, grouped based on the value of a time signature.

## Steps

A step is a subdivision of a beat. These are the same length as a unit in the
step sequencer. By default, there are 4 steps per beat.

## Ticks

A tick is the smallest subdivision of MIDI time. By default, there are 96 ticks
per quarter note, but this value can be adjusted by changing the
[timebase (PPQN)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/songsettings_settings.htm)
of a project. The project timebase can be determined by calling
[`general.getRecPPQ()`][general.getRecPPQ].

Ticks can be used as in an absolute format (number of ticks since the start of
the arrangement), or in conjunction with other beat-based time unit (see
[B:S:T](#bst)).

## B:S:T

"B:S:T" is time counted as bars, steps and ticks. It is comprised of

* The bar number within the current arrangement.
* The number of steps since the start of the current bar.
* The number of ticks since the start of the current step.

## Seconds

The same as seconds in real life. If you want to know more,
[here's a link to the Wikipedia article](https://en.wikipedia.org/wiki/Second).

## Minutes

One minute is equal to 60 seconds.

## Centiseconds

One centisecond is equal to one hundredth of a second.

## Milliseconds

One millisecond is equal to one thousandth of a second.

## M:S:CS

"M:S:CS" is time counted as minutes, seconds and centiseconds.

* The number of minutes since the start of the current arrangement.
* The number of seconds since the start of the current minute.
* The number of centiseconds since the start of the current second.

## Fractional

Fractional time is represented as a percentage of the way through the song. For
example, `0.5` means that the playhead is half-way through the song.

Fractional time is measured based on ticks, so tempo changes will cause the
rate of change of fractional time to vary.


---
# Performance Mode

Performance mode in FL Studio is a powerful tool for sequencing patterns
on-the-fly, used to create live performances.

Most of the functions associated with live performance are found in the
[`playlist`][playlist] module.

To determine whether performance mode is enabled, use
[`playlist.getPerformanceModeState`][playlist.getPerformanceModeState].

## Display zone

The display zone is the region that a controller is currently mapping for live
performance. When set using [`playlist.liveDisplayZone`][playlist.liveDisplayZone],
FL Studio indicates this region using a red rectangle.

## Blocks

When performance mode is active, clips within the performance region are called
"blocks".

## Loop modes

In performance mode, each playlist track has a loop mode, which determines how
the blocks on this track advance when the track is being played.

## Trigger modes

Each playlist track also has a trigger mode which determines the action taken
when pressing on a block.

## Trigger snap

When triggering a block, the trigger snap value of its track determines how FL
Studio will adjust the timing of the clip so that it starts in time with other
clips. For example, if this is set to a beat, and you trigger a block half a
beat early, FL Studio will wait the remaining half-beat so that the block will
start on the next beat.

## Position snap

Contrastingly, the position snap value determines how far FL Studio can skip
into the clip so that it remains in time with other clips. For example, if this
is set to a beat, and you trigger a block half a beat late, FL Studio will skip
the first half-beat of that block so it remains in-time.



---

# MIDI Controller Scripting

MIDI Controller Scripting allows native support for **any MIDI controller**.
Scripts are written in the
[Python programming language](https://www.python.org/about/gettingstarted/).
FL Studio executes these scripts, so that they can control FL Studio's
interaction with a MIDI device, meaning that the MIDI controller can access
features of FL Studio, and FL Studio can send back data to the controller to
trigger drum pad lights or show text on a display. The only limitations are
your controller's communication interface and your imagination.

There is no need to install anything to run scripts in FL Studio, as it has a
Python interpreter built-in. However, if you want to benefit from advanced code
editor features when writing your scripts, you may wish to follow the
[installation instructions](../library.md) to access this documentation
as you write code.

* **Script hierarchy** - As FL Studio natively handles many MIDI functions and
  messages, this allows you to write simple scripts to handle specific cases or
  inputs and leave the rest to FL Studio's generic MIDI support. For example,
  you do not need to tell FL Studio what to do with MIDI notes. If the script
  doesn't specifically make changes to default behavior, FL Studio will handle
  them as normal.

* **Scripts are complex** - With power and flexibility comes complexity. MIDI
  Controller Scripting is intended for hardware manufacturers and advanced
  users to create custom support for MIDI controllers. If you are new to
  programming, MIDI scripting will be confronting and confusing at first. This
  is normal, but patience and persistence will be rewarded! There are some
  simple examples to get started on our user forum listed below.

## MIDI Controller Scripting support forum

FL Studio customers can access the
[MIDI Controller Scripting forum](https://support.image-line.com/redirect/midi_scripting_forum)
to discuss scripting, share scripts, make feature requests and report issues.

## Getting started

Check out the [getting started tutorial](./tutorials/getting_started.md).

## Basic information

* [Script locations and file names](./script_files.md)

* [Script metadata](./script_metadata.md)

* [Callbacks](./callbacks/)

* [Objects used within MIDI Controller Scripting](./fl_classes/)

## API modules

These are Python modules that are built into FL Studio.

* [`arrangement`][arrangement]

* [`channels`][channels]

* [`device`][device]

* [`general`][general]

* [`launchMapPages`][launchMapPages]

* [`mixer`][mixer]

* [`patterns`][patterns]

* [`playlist`][playlist]

* [`plugins`][plugins]

* [`screen`][screen]

* [`transport`][transport]

* [`ui`][ui]

## Extra modules

These are Python files stored within FL Studio's Python library directory.

* [`midi`][midi]

* [`utils`][utils]


---

# Script locations and file names

Script files are located within the [user data folder](https://www.image-line.com/fl-studio-learning/fl-studio-beta-online-manual/html/envsettings_files.htm#userdata)
under `.../Image-Line/FL Studio/Settings/Hardware/[script_name]`, where
`[script_name]` is a folder with a unique name. This folder should contain all
resources required to run the script, including:

* `device_[script_name].py` - this Python file is the entry-point for your
  script. It can have any content, but must begin with `device_` and end with
  `.py`.

* [Launchmap files][launchMapPages], stored as `Page[number].src`, where number
  is a positive integer.

* Additional Python files. Since each script has it's base directory added to
  its `PYTHONPATH`, any additional modules can be `import`ed from within your
  script with ease.

* Any additional resources, such as a `README.md` or a `LICENSE.txt`.


---

# Script metadata

Scripts can specify metadata, which is used to provide information to FL Studio
about the script.

This metadata is specified in a comment at the top of the script's entrypoint
(`device_*.py`) file.

## Example metadata

```py  linenums="1"
# name=Novation Launch Control XL
# url=https://forum.image-line.com/viewtopic.php?p=1494175
# receiveFrom=Forward Device
# supportedDevices=Launch Control XL,Launch Control XL mkII
# supportedHardwareIds=00 20 29 61 00 00 00 00 00 02 07
```

## `name`

The name property controls the name displayed to users in the script selection
menu. This should be descriptive, and should preferably contain your device's
make and model.

This property is required for all scripts. Scripts that do not specify the
property will not be shown in the list of available scripts.

```py
# name=Novation LaunchControl XL
```

## `url`

A help/support URL for your script. This URL must be a post on the
[Image-Line forum](https://forum.image-line.com/). Any URLs that don't start
with `https://forum.image-line.com/` will be redirected to the MIDI Controller
Scripting forum's main page.

```py
# url=https://forum.image-line.com/viewtopic.php?p=1494175
```

This property is optional.

## `receiveFrom`

A comma-separated list of device names from which this script can receive
MIDI messages.

```py
# receiveFrom=Forward Device
```

In the above example, the script named `Forward Device` will see this script in
its available dispatch targets, and will be able to send MIDI messages to this
script using [`device.dispatch()`][device.dispatch].

This property is optional.

## `supportedDevices`

A comma-separated list of device names to link to. FL Studio will automatically
link devices to your script if they have a matching name.

In this example, FL Studio will link the script to devices named
`Launch Control XL` and `Launch Control XL mkII`.

```py
# supportedDevices=Launch Control XL,Launch Control XL mkII
```

Note that device names change depending on your operating system, so it is
important to test these on both Windows and MacOS to ensure that automatic
linking works for both.

This property is optional.

## `supportedHardwareIds`

A comma-separated list of device hardware IDs to link to. FL Studio will
automatically link devices to your script if they provide a matching hardware
ID.

A hardware ID is sent by MIDI Controllers in response to a
[device ID request](https://music.stackexchange.com/a/93913/99162).

You can determine your device's hardware ID by calling
[`device.getDeviceID()`][device.getDeviceID] from that device's script output
console.

The hardware ID should be written as a series of space-separated hexadecimal
bytes.

```py
# supportedHardwareIds=00 20 29 61 00 00 00 00 00 02 07
```

FL Studio matches devices by using `bytes.startswith`, so bytes can be omitted
from the end of the hardware ID, allowing your script to disregard unimportant
aspects such as the firmware version.

This property is optional.

---

# Piano roll scripting

Piano roll scripting allows you to interact with and modify notes and markers
on the FL Studio piano roll.

For support and to share your work, check out the
[Piano roll scripting forum](https://forum.image-line.com/viewforum.php?f=2008).

Scripts should be placed in the `Image-Line/FL Studio/Settings/Piano roll scripts`
directory.

Main script files should use the `.pyscript` file extension, with additional
modules using standard `.py` files.

Additional scripts are located in the following directories:

* `Image-Line/Downloads/Piano roll scripts`: browser script downloads.

* `FL Studio 21/Contents/Resources/FL/System/Config/Piano roll scripts`:
  built-in scripts.

## Module reference

* [`flpianoroll`](flpianoroll): main module for piano roll scripting.

---

# Edison scripting

Edison audio scripting can be used to analyze, manipulate and generate audio
within the [Edison audio editor](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Edison.htm)
and [Slicex](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Slicex.htm).

For support and to share your work, check out the
[Edison scripting forum](https://forum.image-line.com/viewforum.php?f=2009).

Edison scripts can be placed within the
`Image-Line/FL Studio/Settings/Audio scripts` directory.

Main script files should use the `.pyscript` file extension, with additional
modules using standard `.py` files.

## Module reference

* [`enveditor`](./enveditor): edit waveforms in Edison.


---


