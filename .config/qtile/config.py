# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List  # noqa: F401

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
import os
import subprocess
import socket
# pacman -S python-xlib
from Xlib import X, display
from Xlib.ext import randr
from pprint import pprint


d = display.Display()
s = d.screen()
r = s.root
res = r.xrandr_get_screen_resources()._data

#dynamics screen!
num_screens = 0
for output in res['outputs']:
    print("Output %d:" % (output))
    mon = d.xrandr_get_output_info(output, res['config_timestamp'])._data
    print("%s: %d" % (mon['name'], mon['num_preferred']))
    if mon['num_preferred']:
        num_screens += 1
print("%d screens found!" % (num_screens))


#color pallete
def init_colors():
    colo = [
        ["#282c34", "#282c34"], # panel background
        ["#3d3f4b", "#434758"], # background for current screen tab
        ["#ffffff", "#ffffff"], # font color for group names
        ["#ff5555", "#ff5555"], # border line color for current tab
        ["#74438f", "#74438f"], # border line color for 'other tabs' and color for 'odd widgets'
        ["#4f76c7", "#4f76c7"], # color for the 'even widgets'
        ["#e1acff", "#e1acff"], # window name
        ["#ecbbfb", "#ecbbfb"]  # background for inactive screens
    ]
    return colo
#useful methods
def window_to_next_screen(qtile):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group)
def window_to_previous_screen(qtile):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group)

#vars
mod = "mod4"
terminal = guess_terminal()
colors = init_colors()

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),
    Key([mod, "shift"], "space", lazy.layout.flip(), desc="Switch which side the main pane will occupy"),
    # Switch between monitors
    Key([mod], "comma", lazy.next_screen(), desc='Move focus to next monitor'),
    Key([mod], "period", lazy.prev_screen(), desc='Move focus to previous monitor'),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.swap_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.swap_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod], "o", lazy.layout.grow(), desc="Grow window"),
    Key([mod], "i", lazy.layout.shrink(), desc="Shrink window"),
    Key([mod], "p", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawn("rofi -show drun"),
        desc="Spawn a command using rofi"),
    
    #Screenshots
    Key([], 'Print', lazy.spawn("flameshot gui")),
    
    #Audio
    Key([], "XF86AudioRaiseVolume",
        lazy.spawn("pulsemixer --change-volume +5 --max-volume 100")),
    Key([], "XF86AudioLowerVolume",
        lazy.spawn("pulsemixer --change-volume -5")),
    Key([], "XF86AudioMute",
        lazy.spawn("pulsemixer --toggle-mute ")),

]

groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([mod], i.name, lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),

        # mod1 + shift + letter of group = switch to & move focused window to group
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name, switch_group=False),
            desc="Switch to & move focused window to group {}".format(i.name)),
        # Or, use below if you prefer not to switch to that group.
        # # mod1 + shift + letter of group = move focused window to group
        # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
        #     desc="move focused window to group {}".format(i.name)),
    ])

layouts = [
    layout.MonadTall(
        border_width = 2,
        border_focus = colors[3][0],
        border_normal = colors[4][0],
        ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font='sans',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

def init_widgets_list():
    widgets_list = [
                widget.Sep(
                    linewidth = 0,
                    padding = 6,
                    foreground = colors[2],
                    background = colors[0]
                    ),
                widget.GroupBox(
                    margin_y = 5,
                    margin_x = 0,
                    padding_y = 5,
                    padding_x = 5,
                    borderwidth = 1,
                    active = colors[2],
                    inactive = colors[2],
                    rounded = False,
                    highlight_method = "block",
                    this_current_screen_border = colors[5],
                    this_screen_border = colors[1],
                    other_current_screen_border = colors[0],
                    other_screen_border = colors[0],
                    foreground = colors[2],
                    background = colors[0]
                    ),
                widget.CurrentLayout(
                    padding = 10,
                    background = colors[0],
                    foreground = colors[2]
                    ),
                widget.Prompt(
                    prompt=promptt,
                    padding = 10,
                    foreground = colors[3],
                    background = colors[0]
                    ),
                widget.Sep(
                    linewidth = 0,
                    padding = 40,
                    foregruond = colors[2],
                    background = colors[0],
                    ),
                widget.WindowName(
                    foreground = colors[6],
                    background = colors[0],
                    padding = 0,
                    ),
                widget.Systray(
                    background = colors[0],
                    padding = 5
                    ),
                widget.Notify(
                    default_timeout = 5,
                    max_chars = 10,
                    background = colors[0],
                    foreground = colors[3],
                    ),
                widget.CPU(
                    padding = 5,
                    background = colors[0],
                    foreground = colors[2],
                    ),
                widget.Memory(
                        padding = 5,
                        background = colors[0],
                        foreground = colors[2],
                        ),
                widget.Clock(
                        fontsize = 12,
                        foreground = colors[3],
                        background = colors[0],
                        format='%I:%M %P | %d/%m/%Y'
                        ),
            ]
    return widgets_list

promptt = "{0}@{1}: ".format(os.environ["USER"], socket.gethostname())
wl = init_widgets_list()

screens = [
        Screen(top=bar.Bar(widgets=wl, size=30)),
        Screen(top=bar.Bar(widgets=init_widgets_list(), size=30))
        ]
#for screen in range(0, num_screens):
#    screens.append(
#            Screen(top=bar.Bar(widgets=wl, size=30))
#            )


# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
    Match(title='V Barrier'), #Barrier
])
auto_fullscreen = True
focus_on_window_activation = "smart"

#Autostart programs
@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.call([home])

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
