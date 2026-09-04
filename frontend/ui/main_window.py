"""
Main Application Window and Navigation Controller for Sign Language Translator.
Manages the application shell, persistent sidebar, top telemetry header,
and dynamic page view switching.
"""

import customtkinter as ctk
from typing import Dict, Any

import frontend.config as config
import frontend.ui.styles as styles
from frontend.ui.components import (
    Card,
    StatusBadge,
    StatCard,
    ActionButton,
    HeaderBar,
    Sidebar,
    PlaceholderPage,
)
from frontend.services.api_client import api_client
from frontend.services.tts_service import tts_service


class MainWindow(ctk.CTk):
    """
    Main application window hosting the dark desktop interface.
    """

    def __init__(self):
        super().__init__()

        # Appearance & Base Window Configuration
        ctk.set_appearance_mode(config.DEFAULT_APPEARANCE_MODE)
        ctk.set_default_color_theme(config.DEFAULT_COLOR_THEME)

        self.title(f"{config.APP_NAME} — {config.APP_SUBTITLE}")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        self.configure(fg_color=styles.COLOR_BG_DARK)

        # Page registry & active state
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.current_page_id: str = config.PAGE_HOME

        # Construct App Shell Layout
        self._setup_layout()
        self._create_pages()

        # Display initial page
        self.show_page(config.PAGE_HOME)

        # Start periodic telemetry synchronization
        self._sync_telemetry()

    def _setup_layout(self):
        """Build the grid architecture (Sidebar on left, Header on top, Content in center)."""
        # Column 0: Fixed-width Sidebar | Column 1: Main Content Area
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Row 0: Header Bar | Row 1: Active Page Container
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # 1. Persistent Sidebar
        self.sidebar = Sidebar(
            self,
            nav_items=config.NAV_ITEMS,
            on_navigate=self.show_page,
            on_exit=self._on_exit,
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # 2. Top Header Bar
        self.header = HeaderBar(self)
        self.header.grid(row=0, column=1, sticky="ew")

        # 3. Main Content Container
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=1, sticky="nsew", padx=styles.PAD_LG, pady=styles.PAD_LG)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def _create_pages(self):
        """Instantiate all application pages into the page container."""
        # 1. Home / Dashboard Page (Primary view for Phase 3)
        self.pages[config.PAGE_HOME] = self._build_dashboard_page(self.content_container)

        # 2. Placeholders for subsequent planned phases
        self.pages[config.PAGE_GLOVE] = PlaceholderPage(
            self.content_container,
            title="Glove Status & Pairing",
            subtitle="Device connection, diagnostics, and battery health",
            phase_label="Scheduled for Phase 6",
            icon="🧤"
        )
        self.pages[config.PAGE_SENSORS] = PlaceholderPage(
            self.content_container,
            title="Live Sensor Telemetry",
            subtitle="Real-time sensor telemetry channels and orientation data",
            phase_label="Scheduled for Phase 7",
            icon="📊"
        )
        self.pages[config.PAGE_TRANSLATE] = PlaceholderPage(
            self.content_container,
            title="Sign Language Translation",
            subtitle="Sign recognition feed display, word builder, and speech output",
            phase_label="Scheduled for Phase 8",
            icon="🔄"
        )
        self.pages[config.PAGE_HISTORY] = PlaceholderPage(
            self.content_container,
            title="Translation History",
            subtitle="Searchable archive of recognized signs and exported transcripts",
            phase_label="Scheduled for Phase 9",
            icon="🕒"
        )
        self.pages[config.PAGE_SETTINGS] = PlaceholderPage(
            self.content_container,
            title="Application Settings",
            subtitle="Preferences, speech rate, theme configuration, and hardware parameters",
            phase_label="Scheduled for Phase 10",
            icon="⚙️"
        )
        self.pages[config.PAGE_HELP] = PlaceholderPage(
            self.content_container,
            title="Help & User Instructions",
            subtitle="Step-by-step glove operation guide and system troubleshooting",
            phase_label="Scheduled for Phase 10",
            icon="❓"
        )

    def _build_dashboard_page(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """
        Build the Home / Dashboard overview interface with high-level KPI cards,
        system readiness, and a prominent Quick Translation panel.
        """
        page = ctk.CTkFrame(parent, fg_color="transparent")
        page.grid_rowconfigure(2, weight=1)
        page.grid_columnconfigure(0, weight=1)

        # --- Section 1: Dashboard Header & Welcome ---
        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_welcome = ctk.CTkLabel(
            header_frame,
            text="System Overview",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_welcome.pack(side="left")

        # --- Section 2: Four KPI Metric Cards ---
        kpi_grid = ctk.CTkFrame(page, fg_color="transparent")
        kpi_grid.pack(fill="x", pady=(0, styles.PAD_LG))
        for col_idx in range(4):
            kpi_grid.grid_columnconfigure(col_idx, weight=1, uniform="kpi")

        # Card 1: Glove Connection
        glove_info = api_client.get_glove_status()
        self.card_glove_stat = StatCard(
            kpi_grid,
            title="Glove Connection",
            value="Connected",
            subtext=f"{glove_info['device_name']} (Simulated) • {glove_info['battery']}% Battery",
            accent_color=styles.COLOR_STATUS_CONNECTED
        )
        self.card_glove_stat.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        # Card 2: Detection Status
        self.card_system_stat = StatCard(
            kpi_grid,
            title="Detection Status",
            value="Ready",
            subtext="Frontend ready for detection",
            accent_color=styles.COLOR_STATUS_READY
        )
        self.card_system_stat.grid(row=0, column=1, padx=5, sticky="nsew")

        # Card 3: Current Sign
        curr_trans = api_client.get_current_translation()
        self.card_sign_stat = StatCard(
            kpi_grid,
            title="Last Sign",
            value=curr_trans["sign"],
            subtext=f"Confidence: {int(curr_trans['confidence'] * 100)}% (Simulated)",
            accent_color=styles.COLOR_TEXT_PRIMARY
        )
        self.card_sign_stat.grid(row=0, column=2, padx=5, sticky="nsew")

        # Card 4: Saved Translations
        history_count = len(api_client.get_history())
        self.card_history_stat = StatCard(
            kpi_grid,
            title="History Log",
            value=f"{history_count} Saved",
            subtext="Simulated session records",
            accent_color=styles.COLOR_TEXT_SECONDARY
        )
        self.card_history_stat.grid(row=0, column=3, padx=(10, 0), sticky="nsew")

        # --- Section 3: Prominent Quick Translation Card ---
        quick_trans_card = Card(page)
        quick_trans_card.pack(fill="x", pady=(0, styles.PAD_LG))

        # Header of Quick Translation Card
        card_header = ctk.CTkFrame(quick_trans_card, fg_color="transparent")
        card_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_section = ctk.CTkLabel(
            card_header,
            text="QUICK TRANSLATION FEED (SIMULATED)",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_section.pack(side="left")

        self.feed_badge = StatusBadge(card_header, status_type="ready", text="Simulated Data")
        self.feed_badge.pack(side="right")

        # Main Translation Display Body
        display_frame = ctk.CTkFrame(quick_trans_card, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_CARD)
        display_frame.pack(fill="x", padx=styles.PAD_LG, pady=styles.PAD_SM)

        inner_grid = ctk.CTkFrame(display_frame, fg_color="transparent")
        inner_grid.pack(fill="x", padx=styles.PAD_MD, pady=styles.PAD_MD)
        inner_grid.grid_columnconfigure(0, weight=1)
        inner_grid.grid_columnconfigure(1, weight=1)

        # Left Column: Detected Sign
        left_box = ctk.CTkFrame(inner_grid, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="w", padx=styles.PAD_SM)

        lbl_sign_hint = ctk.CTkLabel(
            left_box,
            text="DETECTED SIGN",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_sign_hint.pack(anchor="w")

        self.lbl_sign_val = ctk.CTkLabel(
            left_box,
            text=curr_trans["sign"],
            font=styles.FONT_DISPLAY,
            text_color=styles.COLOR_TEXT_PRIMARY
        )
        self.lbl_sign_val.pack(anchor="w", pady=(2, 0))

        # Right Column: Translated Text
        right_box = ctk.CTkFrame(inner_grid, fg_color="transparent")
        right_box.grid(row=0, column=1, sticky="w", padx=styles.PAD_SM)

        lbl_trans_hint = ctk.CTkLabel(
            right_box,
            text="TRANSLATED TEXT",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_trans_hint.pack(anchor="w")

        self.lbl_trans_val = ctk.CTkLabel(
            right_box,
            text=f'"{curr_trans["translation"]}"',
            font=("Segoe UI", 26, "italic"),
            text_color=styles.COLOR_STATUS_READY
        )
        self.lbl_trans_val.pack(anchor="w", pady=(4, 0))

        # Action Buttons Row
        actions_row = ctk.CTkFrame(quick_trans_card, fg_color="transparent")
        actions_row.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_MD))

        # Speak Button
        self.btn_speak = ActionButton(
            actions_row,
            text="🔊  Speak Translation",
            command=self._handle_speak,
            variant="primary",
            width=170
        )
        self.btn_speak.pack(side="left", padx=(0, 10))

        # Clear Button
        self.btn_clear = ActionButton(
            actions_row,
            text="🗑  Clear",
            command=self._handle_clear,
            variant="secondary",
            width=110
        )
        self.btn_clear.pack(side="left", padx=(0, 10))

        # Save Button
        self.btn_save = ActionButton(
            actions_row,
            text="💾  Save to History",
            command=self._handle_save,
            variant="secondary",
            width=150
        )
        self.btn_save.pack(side="left")

        # Go to Full Translation shortcut
        btn_full_page = ctk.CTkButton(
            actions_row,
            text="Open Full Detection Studio →",
            font=styles.FONT_BODY,
            fg_color="transparent",
            hover_color=styles.COLOR_BG_CARD_HOVER,
            text_color=styles.COLOR_ACCENT_PRIMARY,
            command=lambda: self.show_page(config.PAGE_TRANSLATE)
        )
        btn_full_page.pack(side="right")

        # --- Section 4: Quick Telemetry Snapshot ---
        telemetry_card = Card(page)
        telemetry_card.pack(fill="x")

        telemetry_inner = ctk.CTkFrame(telemetry_card, fg_color="transparent")
        telemetry_inner.pack(fill="x", padx=styles.PAD_LG, pady=styles.PAD_MD)

        lbl_telemetry_title = ctk.CTkLabel(
            telemetry_inner,
            text="HARDWARE LINK & TELEMETRY (SIMULATED)",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_telemetry_title.pack(anchor="w", pady=(0, 6))

        lbl_telemetry_desc = ctk.CTkLabel(
            telemetry_inner,
            text=(
                "Sensor glove is currently connected via simulated mock telemetry.\n"
                "Sensor channels, calibration, and live values can be monitored under the Sensors tab "
                "once hardware configuration is confirmed."
            ),
            font=styles.FONT_BODY,
            text_color=styles.COLOR_TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        lbl_telemetry_desc.pack(anchor="w")

        return page

    def show_page(self, page_id: str):
        """Switch the main content frame to the specified page identifier."""
        if page_id not in self.pages:
            return

        # Hide currently active page
        if self.current_page_id in self.pages:
            self.pages[self.current_page_id].pack_forget()

        # Display newly selected page
        self.pages[page_id].pack(fill="both", expand=True)
        self.current_page_id = page_id

        # Update sidebar active button
        self.sidebar.set_active(page_id)

        # Update header breadcrumb title
        page_labels = {
            config.PAGE_HOME: "Dashboard",
            config.PAGE_GLOVE: "Glove Status",
            config.PAGE_SENSORS: "Sensor Monitoring",
            config.PAGE_TRANSLATE: "Translation Studio",
            config.PAGE_HISTORY: "Translation History",
            config.PAGE_SETTINGS: "Settings",
            config.PAGE_HELP: "Help & Documentation",
        }
        self.header.set_title(page_labels.get(page_id, "Page"))

    def _sync_telemetry(self):
        """Periodic background callback to refresh telemetry indicators."""
        glove_info = api_client.get_glove_status()
        sys_state = api_client.get_system_state()

        self.header.update_telemetry(
            glove_connected=glove_info["connected"],
            system_state=sys_state,
            battery=glove_info["battery"],
            device_name=glove_info["device_name"],
        )

        # Reschedule update
        self.after(config.POLL_INTERVAL_MS, self._sync_telemetry)

    # --- Dashboard Action Handlers ---
    def _handle_speak(self):
        """Trigger text-to-speech for the active translation."""
        curr = api_client.get_current_translation()
        text = curr.get("translation", "")
        if text and text != "—":
            tts_service.speak(text)

    def _handle_clear(self):
        """Clear active translation values."""
        api_client.clear_current_translation()
        curr = api_client.get_current_translation()
        self.lbl_sign_val.configure(text=curr["sign"])
        self.lbl_trans_val.configure(text=f'"{curr["translation"]}"')
        self.card_sign_stat.update_value("—", "Cleared")

    def _handle_save(self):
        """Save active translation to history and update metric count."""
        saved = api_client.save_current_translation()
        if saved:
            count = len(api_client.get_history())
            self.card_history_stat.update_value(f"{count} Saved", "Updated just now")

    def _on_exit(self):
        """Safely shut down the application."""
        self.destroy()
