#!/usr/bin/python

"""
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
"""

import os
import getpass


USER = getpass.getuser()
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR = '%s/data' % PROJECT_DIR

# CSS
DEMOLITIONS_CSS = 'css/demolitions.css'
# JS
DEMOLITIONS_JS = 'js/demolitions.js'
EVENT_TRACKING_JS = 'js/event-tracking.js'

# CSS
RENDER_DEMOLITIONS_CSS = 'css/demolitions.min.css'
# JS
RENDER_DEMOLITIONS_JS = 'js/demolitions.min.js'
RENDER_EVENT_TRACKING_JS = 'js/event-tracking.min.js'

google_photos_id = '1wnGautZ-9PiNeCx_4Mc8VXb39OoNFf42XrVsHwHtXwQ'

google_doc_ids = [
    '1SISZtgH_IeT9jPD0L0Z40_nQY-fOrQTkerpw1fyZ3S8',  # Gallo
    '1WVmqfGLYRCXQiPggDdmzf9VEu0L7LxuONVW7-IzrNUk',  # Road Home
    '1ICmuUIhYIZHd6QA_dvqps5Sdj1D02HvaKhcPWDGje9I',  # NOAH
    '12shJ-3mgE7fRNBEfhN8EXFIzrnYNVsrmnh34G9l2pjc',  # Debose
    '1HfVStH9Kr-gWJPiCJT6M21oiE8fgFwZ-0Y83gw7RmxI',  # Swap
    '1v8c6ZPMXKwU4WaD1u0UmUa7hPtRy3WCUi5chGSDlmnY',  # Lockett
    '1yOEkgZmI-_A4eF7SBzsjkUFxuHuDnV_ui-JHl_R9xN0',  # Voigts
    '1Z-1p_8zoyQGLNYjkCA4l7TzhYk5_1N_RCNCwiCfsPFg'  # Cabrini
]
