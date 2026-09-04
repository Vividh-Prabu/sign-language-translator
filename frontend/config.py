"""
Configuration module for the Sign Language Translator Frontend GUI.
Centralizes window parameters, navigation identifiers, mock data toggles,
and service configuration.
"""

# Application Metadata
APP_NAME = "Sign Language Translator"
APP_SUBTITLE = "Smart Glove Sensor System"
APP_VERSION = "1.0.0-preview"

# Window Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 760
MIN_WINDOW_WIDTH = 1020
MIN_WINDOW_HEIGHT = 660

# Appearance
DEFAULT_APPEARANCE_MODE = "dark"
DEFAULT_COLOR_THEME = "blue"

# Navigation Identifiers
PAGE_HOME = "home"
PAGE_GLOVE = "glove"
PAGE_SENSORS = "sensors"
PAGE_TRANSLATE = "translate"
PAGE_HISTORY = "history"
PAGE_SETTINGS = "settings"
PAGE_HELP = "help"

# Navigation Items Order & Display Labels
NAV_ITEMS = [
    {"id": PAGE_HOME, "label": "Dashboard", "icon": "⚡"},
    {"id": PAGE_GLOVE, "label": "Glove Status", "icon": "🧤"},
    {"id": PAGE_SENSORS, "label": "Sensors", "icon": "📊"},
    {"id": PAGE_TRANSLATE, "label": "Translation", "icon": "🔄"},
    {"id": PAGE_HISTORY, "label": "History", "icon": "🕒"},
    {"id": PAGE_SETTINGS, "label": "Settings", "icon": "⚙️"},
    {"id": PAGE_HELP, "label": "Help & Docs", "icon": "❓"},
]

# Backend & Hardware Integration Flags
USE_MOCK_DATA = True
API_BASE_URL = "http://localhost:8000/api"
POLL_INTERVAL_MS = 1000

# Glove Hardware Defaults
DEFAULT_DEVICE_NAME = "Glove-01"
DEFAULT_BATTERY_LEVEL = 87
AUTO_CONNECT = False

# Speech Settings
TTS_ENABLED = True
DEFAULT_SPEECH_RATE = 150
