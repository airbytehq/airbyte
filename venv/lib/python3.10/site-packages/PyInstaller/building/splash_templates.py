# -----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------
"""
Templates for the splash screen tcl script.
"""
from PyInstaller.compat import is_cygwin, is_darwin, is_win

ipc_script = r"""
proc _ipc_server {channel clientaddr clientport} {
    # This function is called if a new client connects to
    # the server. This creates a channel, which calls
    # _ipc_caller if data was send through the connection
    set client_name [format <%s:%d> $clientaddr $clientport]

    chan configure $channel \
        -buffering none \
        -encoding utf-8 \
        -eofchar \x04 \
        -translation cr
    chan event $channel readable [list _ipc_caller $channel $client_name]
}

proc _ipc_caller {channel client_name} {
    # This function is called if a command was sent through
    # the tcp connection. The current implementation supports
    # two commands: update_text and exit, although exit
    # is implemented to be called if the connection gets
    # closed (from python) or the character 0x04 was received
    chan gets $channel cmd

    if {[chan eof $channel]} {
        # This is entered if either the connection was closed
        # or the char 0x04 was send
        chan close $channel
        exit

    } elseif {![chan blocked $channel]} {
        # RPC methods

        # update_text command
        if {[string match "update_text*" $cmd]} {
            global status_text
            set first [expr {[string first "(" $cmd] + 1}]
            set last [expr {[string last ")" $cmd] - 1}]

            set status_text [string range $cmd $first $last]
        }
        # Implement other procedures here
    }
}

# By setting the port to 0 the os will assign a free port
set server_socket [socket -server _ipc_server -myaddr localhost 0]
set server_port [fconfigure $server_socket -sockname]

# This environment variable is shared between the python and the tcl
# interpreter and publishes the port the tcp server socket is available
set env(_PYIBoot_SPLASH) [lindex $server_port 2]
"""

image_script = r"""
# The variable $_image_data, which holds the data for the splash
# image is created by the bootloader.
image create photo splash_image
splash_image put $_image_data
# delete the variable, because the image now holds the data
unset _image_data

proc canvas_text_update {canvas tag _var - -}  {
    # This function is rigged to be called if the a variable
    # status_text gets changed. This updates the text on
    # the canvas
    upvar $_var var
    $canvas itemconfigure $tag -text $var
}
"""

splash_canvas_setup = r"""
package require Tk

set image_width [image width splash_image]
set image_height [image height splash_image]
set display_width [winfo screenwidth .]
set display_height [winfo screenheight .]

set x_position [expr {int(0.5*($display_width - $image_width))}]
set y_position [expr {int(0.5*($display_height - $image_height))}]

# Toplevel frame in which all widgets should be positioned
frame .root

# Configure the canvas on which the splash
# screen will be drawn
canvas .root.canvas \
    -width $image_width \
    -height $image_height \
    -borderwidth 0 \
    -highlightthickness 0

# Draw the image into the canvas, filling it.
.root.canvas create image \
    [expr {$image_width / 2}] \
    [expr {$image_height / 2}] \
    -image splash_image
"""

splash_canvas_text = r"""
# Create a text on the canvas, which tracks the local
# variable status_text. status_text is changed via C to
# update the progress on the splash screen.
# We cannot use the default label, because it has a
# default background, which cannot be turned transparent
.root.canvas create text \
        %(pad_x)d \
        %(pad_y)d \
        -fill %(color)s \
        -justify center \
        -font myFont \
        -tag vartext \
        -anchor sw
trace variable status_text w \
    [list canvas_text_update .root.canvas vartext]
set status_text "%(default_text)s"
"""

splash_canvas_default_font = r"""
font create myFont {*}[font actual TkDefaultFont]
font configure myFont -size %(font_size)d
"""

splash_canvas_custom_font = r"""
font create myFont -family %(font)s -size %(font_size)d
"""

if is_win or is_cygwin:
    transparent_setup = r"""
# If the image is transparent, the background will be filled
# with magenta. The magenta background is later replaced with transparency.
# Here is the limitation of this implementation, that only
# sharp transparent image corners are possible
wm attributes . -transparentcolor magenta
.root.canvas configure -background magenta
"""

elif is_darwin:
    # This is untested, but should work following: https://stackoverflow.com/a/44296157/5869139
    transparent_setup = r"""
wm attributes . -transparent 1
. configure -background systemTransparent
.root.canvas configure -background systemTransparent
"""

else:
    # For Linux there is no common way to create a transparent window
    transparent_setup = r""

pack_widgets = r"""
# Position all widgets in the window
pack .root
grid .root.canvas   -column 0 -row 0 -columnspan 1 -rowspan 2
"""

# Enable always-on-top behavior, by setting overrideredirect and the topmost attribute.
position_window_on_top = r"""
# Set position and mode of the window - always-on-top behavior
wm overrideredirect . 1
wm geometry         . +${x_position}+${y_position}
wm attributes       . -topmost 1
"""

# Disable always-on-top behavior
if is_win or is_cygwin or is_darwin:
    # On Windows, we disable the always-on-top behavior while still setting overrideredirect
    # (to disable window decorations), but set topmost attribute to 0.
    position_window = r"""
# Set position and mode of the window
wm overrideredirect . 1
wm geometry         . +${x_position}+${y_position}
wm attributes       . -topmost 0
"""
else:
    # On Linux, we must not use overrideredirect; instead, we set X11-specific type attribute to splash,
    # which lets the window manager to properly handle the splash screen (without window decorations
    # but allowing other windows to be brought to front).
    position_window = r"""
# Set position and mode of the window
wm geometry         . +${x_position}+${y_position}
wm attributes       . -type splash
"""

raise_window = r"""
raise .
"""


def build_script(text_options=None, always_on_top=False):
    """
    This function builds the tcl script for the splash screen.
    """
    # Order is important!
    script = [
        ipc_script,
        image_script,
        splash_canvas_setup,
    ]

    if text_options:
        # If the default font is used we need a different syntax
        if text_options['font'] == "TkDefaultFont":
            script.append(splash_canvas_default_font % text_options)
        else:
            script.append(splash_canvas_custom_font % text_options)
        script.append(splash_canvas_text % text_options)

    script.append(transparent_setup)

    script.append(pack_widgets)
    script.append(position_window_on_top if always_on_top else position_window)
    script.append(raise_window)

    return '\n'.join(script)
