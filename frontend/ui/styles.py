"""
Design System and Styling Constants for the Sign Language Translator GUI.
Provides a cohesive, modern dark theme inspired by professional developer tools.
"""

# Color Palette - Modern Deep Dark Theme
COLOR_BG_DARK = "#0d1117"        # Main window background
COLOR_BG_SIDEBAR = "#080c10"     # Left navigation panel
COLOR_BG_HEADER = "#0d1117"      # Top header background
COLOR_BG_CARD = "#161b22"        # Surface / Card background
COLOR_BG_CARD_HOVER = "#1c2128"  # Card hover state
COLOR_BG_SUBTLE = "#21262d"      # Subtle container / input field

# Borders & Separators
COLOR_BORDER = "#30363d"         # Subtle card & container borders
COLOR_BORDER_LIGHT = "#21262d"   # Secondary divider
COLOR_BORDER_FOCUS = "#58a6ff"   # Focused/active border

# Text & Typography Colors
COLOR_TEXT_PRIMARY = "#f0f6fc"   # High-contrast white
COLOR_TEXT_SECONDARY = "#8b949e" # Balanced medium gray
COLOR_TEXT_MUTED = "#484f58"     # Low-contrast helper text
COLOR_TEXT_INVERTED = "#ffffff"  # On colored buttons

# Primary Accent Colors (Azure / Electric Blue)
COLOR_ACCENT_PRIMARY = "#2f81f7"
COLOR_ACCENT_HOVER = "#388bfd"
COLOR_ACCENT_PRESSED = "#1f6feb"
COLOR_ACCENT_BG = "#13233a"      # Subtle accent tint background

# Secondary / Neutral Actions
COLOR_BTN_SECONDARY = "#21262d"
COLOR_BTN_SECONDARY_HOVER = "#30363d"
COLOR_BTN_SECONDARY_BORDER = "#363b42"

# Destructive Actions
COLOR_DANGER = "#f85149"
COLOR_DANGER_HOVER = "#da3633"
COLOR_DANGER_BG = "#301314"

# Semantic Status Colors
COLOR_STATUS_CONNECTED = "#3fb950"    # Vibrant Emerald Green
COLOR_STATUS_CONNECTED_BG = "#13271c"
COLOR_STATUS_CONNECTED_BORDER = "#1b4b2c"

COLOR_STATUS_READY = "#58a6ff"        # Sky Blue
COLOR_STATUS_READY_BG = "#13233a"
COLOR_STATUS_READY_BORDER = "#1f4b7a"

COLOR_STATUS_DETECTING = "#d29922"    # Warm Amber / Warning
COLOR_STATUS_DETECTING_BG = "#2c2210"
COLOR_STATUS_DETECTING_BORDER = "#533f1c"

COLOR_STATUS_DISCONNECTED = "#f85149" # Coral Red / Error
COLOR_STATUS_DISCONNECTED_BG = "#301314"
COLOR_STATUS_DISCONNECTED_BORDER = "#5c2223"

# Typography System
FONT_FAMILY = "Segoe UI"

FONT_DISPLAY = (FONT_FAMILY, 32, "bold")
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "normal")

FONT_SECTION_HEADER = (FONT_FAMILY, 15, "bold")
FONT_CARD_TITLE = (FONT_FAMILY, 12, "bold")

FONT_STAT_VALUE = (FONT_FAMILY, 24, "bold")
FONT_STAT_LABEL = (FONT_FAMILY, 11, "normal")

FONT_NAV = (FONT_FAMILY, 13, "normal")
FONT_NAV_ACTIVE = (FONT_FAMILY, 13, "bold")

FONT_BODY = (FONT_FAMILY, 12, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 12, "bold")
FONT_SMALL = (FONT_FAMILY, 10, "normal")
FONT_BADGE = (FONT_FAMILY, 11, "bold")
FONT_MONO = ("Consolas", 12, "normal")

# Geometry & Spacing
RADIUS_CARD = 10
RADIUS_BUTTON = 7
RADIUS_BADGE = 12
RADIUS_PILL = 20

PAD_XS = 4
PAD_SM = 8
PAD_MD = 16
PAD_LG = 24
PAD_XL = 32
