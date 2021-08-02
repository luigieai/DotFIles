colors = {
    'main':         '#036D19',
    'secondary':    '#09A129',
    'background':   '#081C0F',
    'text':         '#14CC60',
    'separator':    '#434758',
    'urgent':       '#993932',
    'block-background': '#0A2E36',
    'rosinha': '#F400A1'
}

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