"""
Reusable UI Components for the Sign Language Translator GUI.
Includes StatusBadge, StatCard, Card, ActionButton, HeaderBar, and Sidebar.
Built with CustomTkinter following the modern dark design system.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any, List
import frontend.ui.styles as styles
import frontend.config as config


class Card(ctk.CTkFrame):
    """
    Standard dark container card with subtle border and rounded corners.
    """
    def __init__(self, master, corner_radius: int = styles.RADIUS_CARD, **kwargs):
        super().__init__(
            master,
            corner_radius=corner_radius,
            fg_color=styles.COLOR_BG_CARD,
            border_width=1,
            border_color=styles.COLOR_BORDER,
            **kwargs
        )


class StatusBadge(ctk.CTkFrame):
    """
    Pill-shaped status badge with a color-coded dot indicator and label.
    Supports states: connected, disconnected, ready, detecting, processing, error.
    """
    def __init__(self, master, status_type: str = "connected", text: Optional[str] = None, **kwargs):
        super().__init__(
            master,
            corner_radius=styles.RADIUS_BADGE,
            border_width=1,
            **kwargs
        )
        self.dot_label = ctk.CTkLabel(self, text="●", font=styles.FONT_BADGE)
        self.dot_label.pack(side="left", padx=(10, 4), pady=4)

        self.text_label = ctk.CTkLabel(self, text="", font=styles.FONT_BADGE)
        self.text_label.pack(side="left", padx=(0, 10), pady=4)

        self.set_status(status_type, text)

    def set_status(self, status_type: str, text: Optional[str] = None):
        """Update badge colors and text based on status type."""
        status_map = {
            "connected": {
                "dot_color": styles.COLOR_STATUS_CONNECTED,
                "text": text or "Connected",
                "fg_color": styles.COLOR_STATUS_CONNECTED_BG,
                "border_color": styles.COLOR_STATUS_CONNECTED_BORDER,
                "text_color": styles.COLOR_STATUS_CONNECTED,
            },
            "ready": {
                "dot_color": styles.COLOR_STATUS_READY,
                "text": text or "Ready",
                "fg_color": styles.COLOR_STATUS_READY_BG,
                "border_color": styles.COLOR_STATUS_READY_BORDER,
                "text_color": styles.COLOR_STATUS_READY,
            },
            "detecting": {
                "dot_color": styles.COLOR_STATUS_DETECTING,
                "text": text or "Detecting...",
                "fg_color": styles.COLOR_STATUS_DETECTING_BG,
                "border_color": styles.COLOR_STATUS_DETECTING_BORDER,
                "text_color": styles.COLOR_STATUS_DETECTING,
            },
            "processing": {
                "dot_color": styles.COLOR_STATUS_DETECTING,
                "text": text or "Processing...",
                "fg_color": styles.COLOR_STATUS_DETECTING_BG,
                "border_color": styles.COLOR_STATUS_DETECTING_BORDER,
                "text_color": styles.COLOR_STATUS_DETECTING,
            },
            "disconnected": {
                "dot_color": styles.COLOR_STATUS_DISCONNECTED,
                "text": text or "Disconnected",
                "fg_color": styles.COLOR_STATUS_DISCONNECTED_BG,
                "border_color": styles.COLOR_STATUS_DISCONNECTED_BORDER,
                "text_color": styles.COLOR_STATUS_DISCONNECTED,
            },
            "error": {
                "dot_color": styles.COLOR_STATUS_DISCONNECTED,
                "text": text or "Error",
                "fg_color": styles.COLOR_STATUS_DISCONNECTED_BG,
                "border_color": styles.COLOR_STATUS_DISCONNECTED_BORDER,
                "text_color": styles.COLOR_STATUS_DISCONNECTED,
            },
        }

        config_data = status_map.get(status_type.lower(), status_map["ready"])
        self.configure(fg_color=config_data["fg_color"], border_color=config_data["border_color"])
        self.dot_label.configure(text_color=config_data["dot_color"])
        self.text_label.configure(text=config_data["text"], text_color=config_data["text_color"])


class StatCard(Card):
    """
    Elevated statistic / KPI card displaying a metric, title, and descriptive detail.
    """
    def __init__(self, master, title: str, value: str, subtext: str = "",
                 accent_color: Optional[str] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        # Header with Title
        self.lbl_title = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_title.pack(anchor="w", padx=16, pady=(14, 2))

        # Main Value Display
        self.lbl_value = ctk.CTkLabel(
            self,
            text=value,
            font=styles.FONT_STAT_VALUE,
            text_color=accent_color or styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_value.pack(anchor="w", padx=16, pady=2)

        # Subtext / Meta description
        self.lbl_subtext = ctk.CTkLabel(
            self,
            text=subtext,
            font=styles.FONT_STAT_LABEL,
            text_color=styles.COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_subtext.pack(anchor="w", padx=16, pady=(2, 14))

    def update_value(self, value: str, subtext: Optional[str] = None):
        """Update stat card contents dynamically."""
        self.lbl_value.configure(text=value)
        if subtext is not None:
            self.lbl_subtext.configure(text=subtext)


class ActionButton(ctk.CTkButton):
    """
    Styled button with pre-configured variants: primary, secondary, danger, success.
    """
    def __init__(self, master, text: str, command: Optional[Callable] = None,
                 variant: str = "primary", **kwargs):
        variant_config = {
            "primary": {
                "fg_color": styles.COLOR_ACCENT_PRIMARY,
                "hover_color": styles.COLOR_ACCENT_HOVER,
                "text_color": styles.COLOR_TEXT_INVERTED,
                "border_width": 0,
            },
            "secondary": {
                "fg_color": styles.COLOR_BTN_SECONDARY,
                "hover_color": styles.COLOR_BTN_SECONDARY_HOVER,
                "text_color": styles.COLOR_TEXT_PRIMARY,
                "border_width": 1,
                "border_color": styles.COLOR_BTN_SECONDARY_BORDER,
            },
            "danger": {
                "fg_color": styles.COLOR_DANGER_BG,
                "hover_color": styles.COLOR_DANGER,
                "text_color": styles.COLOR_DANGER,
                "border_width": 1,
                "border_color": styles.COLOR_DANGER,
            },
            "success": {
                "fg_color": styles.COLOR_STATUS_CONNECTED_BG,
                "hover_color": styles.COLOR_STATUS_CONNECTED,
                "text_color": styles.COLOR_STATUS_CONNECTED,
                "border_width": 1,
                "border_color": styles.COLOR_STATUS_CONNECTED_BORDER,
            },
        }
        cfg = variant_config.get(variant, variant_config["primary"])
        super().__init__(
            master,
            text=text,
            command=command,
            font=styles.FONT_BODY_BOLD,
            corner_radius=styles.RADIUS_BUTTON,
            height=38,
            **cfg,
            **kwargs
        )


class HeaderBar(ctk.CTkFrame):
    """
    Top application header displaying active section title, breadcrumb,
    and live system/glove telemetry indicators.
    """
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            height=58,
            fg_color=styles.COLOR_BG_HEADER,
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        self.pack_propagate(False)

        # Left: Breadcrumb / Section title
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", padx=styles.PAD_LG, pady=10)

        self.lbl_system = ctk.CTkLabel(
            self.left_container,
            text="SYSTEM /",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_MUTED
        )
        self.lbl_system.pack(side="left", padx=(0, 6))

        self.lbl_page_title = ctk.CTkLabel(
            self.left_container,
            text="Dashboard",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY
        )
        self.lbl_page_title.pack(side="left")

        # Right: Real-time telemetry badges
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", padx=styles.PAD_LG, pady=10)

        # Device chip
        self.lbl_device = ctk.CTkLabel(
            self.right_container,
            text=f"Device: {config.DEFAULT_DEVICE_NAME} (Simulated)",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_SECONDARY
        )
        self.lbl_device.pack(side="left", padx=(0, 12))

        # Battery indicator
        self.lbl_battery = ctk.CTkLabel(
            self.right_container,
            text=f"🔋 {config.DEFAULT_BATTERY_LEVEL}%",
            font=styles.FONT_BODY_BOLD,
            text_color=styles.COLOR_STATUS_CONNECTED
        )
        self.lbl_battery.pack(side="left", padx=(0, 14))

        # Glove Connection Badge
        self.badge_glove = StatusBadge(self.right_container, status_type="connected", text="Glove: Connected")
        self.badge_glove.pack(side="left", padx=(0, 8))

        # Detection Status Badge (Frontend-neutral)
        self.badge_system = StatusBadge(self.right_container, status_type="ready", text="Status: Ready")
        self.badge_system.pack(side="left")

    def set_title(self, title: str):
        """Update active section title in breadcrumb."""
        self.lbl_page_title.configure(text=title)

    def update_telemetry(self, glove_connected: bool, system_state: str, battery: int, device_name: str):
        """Update top bar indicators."""
        self.lbl_device.configure(
            text=f"Device: {device_name} (Simulated)" if glove_connected else "Device: Disconnected"
        )
        self.lbl_battery.configure(
            text=f"🔋 {battery}%" if glove_connected else "🔋 —",
            text_color=styles.COLOR_STATUS_CONNECTED if battery > 20 else styles.COLOR_DANGER
        )
        self.badge_glove.set_status(
            "connected" if glove_connected else "disconnected",
            "Glove: Connected" if glove_connected else "Glove: Disconnected"
        )
        self.badge_system.set_status(system_state.lower(), f"Status: {system_state}")


class Sidebar(ctk.CTkFrame):
    """
    Persistent left navigation drawer containing branding,
    menu action buttons with active highlighting, and an exit button.
    """
    def __init__(self, master, nav_items: List[Dict[str, str]], on_navigate: Callable[[str], None],
                 on_exit: Callable[[], None], **kwargs):
        super().__init__(
            master,
            width=220,
            fg_color=styles.COLOR_BG_SIDEBAR,
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        self.pack_propagate(False)
        self.nav_items = nav_items
        self.on_navigate = on_navigate
        self.on_exit = on_exit
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        self.active_page = config.PAGE_HOME

        self._build_header()
        self._build_navigation()
        self._build_footer()

    def _build_header(self):
        """Render top branding section."""
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 16))

        # Logo / Icon badge
        logo_icon = ctk.CTkLabel(
            brand_frame,
            text="🖐️",
            font=("Segoe UI", 24)
        )
        logo_icon.pack(side="left", padx=(0, 10))

        text_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        lbl_app_name = ctk.CTkLabel(
            text_frame,
            text="SIGN TRANSLATE",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_app_name.pack(fill="x")

        lbl_app_sub = ctk.CTkLabel(
            text_frame,
            text="Sensor Glove System",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_app_sub.pack(fill="x")

        # Divider
        divider = ctk.CTkFrame(self, height=1, fg_color=styles.COLOR_BORDER_LIGHT)
        divider.pack(fill="x", padx=16, pady=(0, 16))

    def _build_navigation(self):
        """Render menu navigation buttons."""
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=12)

        for item in self.nav_items:
            page_id = item["id"]
            label = f"  {item['icon']}   {item['label']}"
            btn = ctk.CTkButton(
                menu_frame,
                text=label,
                anchor="w",
                font=styles.FONT_NAV,
                height=42,
                corner_radius=styles.RADIUS_BUTTON,
                fg_color="transparent",
                hover_color=styles.COLOR_BG_CARD_HOVER,
                text_color=styles.COLOR_TEXT_SECONDARY,
                command=lambda pid=page_id: self._handle_click(pid)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[page_id] = btn

    def _build_footer(self):
        """Render bottom exit and metadata area."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", padx=12, pady=16)

        divider = ctk.CTkFrame(footer_frame, height=1, fg_color=styles.COLOR_BORDER_LIGHT)
        divider.pack(fill="x", pady=(0, 12))

        # Version tag
        lbl_version = ctk.CTkLabel(
            footer_frame,
            text=f"Version {config.APP_VERSION}",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_version.pack(pady=(0, 8))

        # Exit Button
        btn_exit = ctk.CTkButton(
            footer_frame,
            text="  ⏻   Exit Application",
            anchor="w",
            font=styles.FONT_BODY,
            height=38,
            corner_radius=styles.RADIUS_BUTTON,
            fg_color=styles.COLOR_DANGER_BG,
            hover_color=styles.COLOR_DANGER,
            text_color=styles.COLOR_DANGER,
            border_width=1,
            border_color=styles.COLOR_DANGER,
            command=self.on_exit
        )
        btn_exit.pack(fill="x")

    def _handle_click(self, page_id: str):
        self.set_active(page_id)
        self.on_navigate(page_id)

    def set_active(self, page_id: str):
        """Highlight the currently active navigation item."""
        self.active_page = page_id
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=styles.COLOR_ACCENT_PRIMARY,
                    hover_color=styles.COLOR_ACCENT_HOVER,
                    text_color=styles.COLOR_TEXT_INVERTED,
                    font=styles.FONT_NAV_ACTIVE
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=styles.COLOR_BG_CARD_HOVER,
                    text_color=styles.COLOR_TEXT_SECONDARY,
                    font=styles.FONT_NAV
                )


class PlaceholderPage(ctk.CTkFrame):
    """
    Modern placeholder view rendered for tabs in upcoming development phases.
    Ensures seamless switching with zero blank or broken screens.
    """
    def __init__(self, master, title: str, subtitle: str, phase_label: str, icon: str = "📦", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        center_card = Card(self, corner_radius=styles.RADIUS_CARD)
        center_card.place(relx=0.5, rely=0.45, anchor="center")

        icon_lbl = ctk.CTkLabel(center_card, text=icon, font=("Segoe UI", 48))
        icon_lbl.pack(padx=60, pady=(40, 10))

        title_lbl = ctk.CTkLabel(center_card, text=title, font=styles.FONT_TITLE, text_color=styles.COLOR_TEXT_PRIMARY)
        title_lbl.pack(padx=60, pady=4)

        sub_lbl = ctk.CTkLabel(center_card, text=subtitle, font=styles.FONT_SUBTITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        sub_lbl.pack(padx=60, pady=4)

        badge = ctk.CTkLabel(
            center_card,
            text=f"  {phase_label}  ",
            font=styles.FONT_BADGE,
            fg_color=styles.COLOR_ACCENT_BG,
            text_color=styles.COLOR_STATUS_READY,
            corner_radius=6
        )
        badge.pack(padx=60, pady=(16, 40))
