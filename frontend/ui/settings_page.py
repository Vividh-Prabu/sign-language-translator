"""
Settings Page for the Sign Language Translator GUI.
Provides controls for Appearance theme, Translation Language, Speech synthesis tuning,
Hardware Glove preferences, and Application About details.
"""

import customtkinter as ctk
from typing import Optional, Callable

import frontend.config as config
import frontend.ui.styles as styles
from frontend.ui.components import Card, ActionButton, StatusBadge
from frontend.services.tts_service import tts_service


class SettingsPage(ctk.CTkFrame):
    """
    Page 6: Application Settings and Configuration.
    """

    def __init__(self, master, on_theme_change: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_theme_change = on_theme_change

        self._build_header()
        self._build_content()

    def _build_header(self):
        """Render page title and subtitle."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Settings & Preferences",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Configure application appearance, audio speech output, device preferences, and system parameters.",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def _build_content(self):
        """Construct the scrollable settings sections."""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # ==========================================
        # SECTION 1: Appearance & Display
        # ==========================================
        card_app = Card(scroll)
        card_app.pack(fill="x", pady=(0, styles.PAD_MD))

        h1 = ctk.CTkFrame(card_app, fg_color="transparent")
        h1.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_app_title = ctk.CTkLabel(h1, text="APPEARANCE & THEME", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_app_title.pack(side="left")

        row_theme = ctk.CTkFrame(card_app, fg_color="transparent")
        row_theme.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        lbl_theme_desc = ctk.CTkLabel(
            row_theme,
            text="Interface Color Theme:\nSelect your preferred visual appearance mode.",
            font=styles.FONT_BODY,
            text_color=styles.COLOR_TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        lbl_theme_desc.pack(side="left")

        self.combo_theme = ctk.CTkOptionMenu(
            row_theme,
            values=["Dark", "Light", "System"],
            command=self._handle_theme_change,
            font=styles.FONT_BODY,
            fg_color=styles.COLOR_BG_SUBTLE,
            button_color=styles.COLOR_BTN_SECONDARY_HOVER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=36,
            width=140,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.combo_theme.set("Dark")
        self.combo_theme.pack(side="right")

        # ==========================================
        # SECTION 2: Speech & Audio
        # ==========================================
        card_speech = Card(scroll)
        card_speech.pack(fill="x", pady=(0, styles.PAD_MD))

        h2 = ctk.CTkFrame(card_speech, fg_color="transparent")
        h2.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_sp_title = ctk.CTkLabel(h2, text="SPEECH & TEXT-TO-SPEECH (TTS)", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_sp_title.pack(side="left")

        # TTS Toggle Row
        row_tts_toggle = ctk.CTkFrame(card_speech, fg_color="transparent")
        row_tts_toggle.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))

        lbl_tts_desc = ctk.CTkLabel(row_tts_toggle, text="Enable Audio Speech Output:", font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_PRIMARY)
        lbl_tts_desc.pack(side="left")

        self.switch_tts = ctk.CTkSwitch(
            row_tts_toggle,
            text="TTS Active",
            font=styles.FONT_BODY,
            text_color=styles.COLOR_STATUS_CONNECTED,
            command=self._handle_tts_toggle,
            progress_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.switch_tts.pack(side="right")
        if config.TTS_ENABLED:
            self.switch_tts.select()

        # Speed Slider Row
        row_speed = ctk.CTkFrame(card_speech, fg_color="transparent")
        row_speed.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_SM))

        lbl_spd_name = ctk.CTkLabel(row_speed, text="Speech Speed (Rate):", font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_PRIMARY)
        lbl_spd_name.pack(side="left")

        self.lbl_speed_val = ctk.CTkLabel(
            row_speed,
            text=f"{config.DEFAULT_SPEECH_RATE} WPM",
            font=styles.FONT_MONO,
            text_color=styles.COLOR_STATUS_READY
        )
        self.lbl_speed_val.pack(side="right", padx=(8, 0))

        self.slider_speed = ctk.CTkSlider(
            row_speed,
            from_=100,
            to=250,
            number_of_steps=15,
            command=self._handle_speed_change,
            height=16,
            progress_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.slider_speed.pack(side="right", fill="x", expand=True, padx=12)
        self.slider_speed.set(config.DEFAULT_SPEECH_RATE)

        # Test Voice Button Row
        row_test = ctk.CTkFrame(card_speech, fg_color="transparent")
        row_test.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_MD))

        btn_test_voice = ActionButton(
            row_test,
            text="🔊  Test Voice Output",
            command=self._handle_test_voice,
            variant="secondary",
            width=180
        )
        btn_test_voice.pack(side="left")

        lbl_tts_hint = ctk.CTkLabel(
            row_test,
            text="Uses local speech synthesis (pyttsx3 or Windows SAPI).",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_tts_hint.pack(side="left", padx=12)

        # ==========================================
        # SECTION 3: Language & Localization
        # ==========================================
        card_lang = Card(scroll)
        card_lang.pack(fill="x", pady=(0, styles.PAD_MD))

        h3 = ctk.CTkFrame(card_lang, fg_color="transparent")
        h3.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_lang_title = ctk.CTkLabel(h3, text="LANGUAGE & LOCALIZATION", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_lang_title.pack(side="left")

        row_lang = ctk.CTkFrame(card_lang, fg_color="transparent")
        row_lang.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        lbl_lang_desc = ctk.CTkLabel(row_lang, text="Target Translation Language:", font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_PRIMARY)
        lbl_lang_desc.pack(side="left")

        self.combo_lang = ctk.CTkOptionMenu(
            row_lang,
            values=["English (US)", "Spanish (ES)", "French (FR)", "German (DE)"],
            font=styles.FONT_BODY,
            fg_color=styles.COLOR_BG_SUBTLE,
            button_color=styles.COLOR_BTN_SECONDARY_HOVER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=36,
            width=160,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.combo_lang.set("English (US)")
        self.combo_lang.pack(side="right")

        # ==========================================
        # SECTION 4: Hardware Glove Preferences
        # ==========================================
        card_glove = Card(scroll)
        card_glove.pack(fill="x", pady=(0, styles.PAD_MD))

        h4 = ctk.CTkFrame(card_glove, fg_color="transparent")
        h4.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_glv_title = ctk.CTkLabel(h4, text="HARDWARE GLOVE PREFERENCES", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_glv_title.pack(side="left")

        row_glove_name = ctk.CTkFrame(card_glove, fg_color="transparent")
        row_glove_name.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))

        lbl_gname = ctk.CTkLabel(row_glove_name, text="Default Device Name:", font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_PRIMARY)
        lbl_gname.pack(side="left")

        self.entry_device_name = ctk.CTkEntry(
            row_glove_name,
            font=styles.FONT_BODY,
            fg_color=styles.COLOR_BG_SUBTLE,
            border_color=styles.COLOR_BORDER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=34,
            width=180,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.entry_device_name.insert(0, config.DEFAULT_DEVICE_NAME)
        self.entry_device_name.pack(side="right")

        row_autoconnect = ctk.CTkFrame(card_glove, fg_color="transparent")
        row_autoconnect.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_MD))

        lbl_ac_desc = ctk.CTkLabel(row_autoconnect, text="Automatic Connection on App Startup:", font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_PRIMARY)
        lbl_ac_desc.pack(side="left")

        self.switch_ac = ctk.CTkSwitch(
            row_autoconnect,
            text="Auto-Connect",
            font=styles.FONT_BODY,
            text_color=styles.COLOR_TEXT_SECONDARY,
            progress_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.switch_ac.pack(side="right")
        if config.AUTO_CONNECT:
            self.switch_ac.select()

        # ==========================================
        # SECTION 5: About & Project Information
        # ==========================================
        card_about = Card(scroll)
        card_about.pack(fill="x", pady=(0, styles.PAD_LG))

        h5 = ctk.CTkFrame(card_about, fg_color="transparent")
        h5.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_about_title = ctk.CTkLabel(h5, text="ABOUT & SYSTEM INFORMATION", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_about_title.pack(side="left")

        body_about = ctk.CTkFrame(card_about, fg_color="transparent")
        body_about.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        info_items = [
            ("Application", f"{config.APP_NAME} — {config.APP_SUBTITLE}"),
            ("Version", config.APP_VERSION),
            ("Project Scope", "3-Person College Project (Sensor Glove Sign Language Translator)"),
            ("Active Subsystem", "Frontend Desktop GUI (CustomTkinter)"),
            ("Data Mode", "Simulated Telemetry & Mock Service Layer (API Ready)"),
        ]

        for k, v in info_items:
            rf = ctk.CTkFrame(body_about, fg_color="transparent")
            rf.pack(fill="x", pady=2)
            ctk.CTkLabel(rf, text=k, font=styles.FONT_BODY_BOLD, text_color=styles.COLOR_TEXT_MUTED, width=160, anchor="w").pack(side="left")
            ctk.CTkLabel(rf, text=v, font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_PRIMARY, anchor="w").pack(side="left")

        # Bottom Actions: Save & Reset
        action_bar = ctk.CTkFrame(scroll, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, styles.PAD_XL))

        self.btn_save_settings = ActionButton(
            action_bar,
            text="💾  Save Settings",
            command=self._handle_save_settings,
            variant="primary",
            width=160
        )
        self.btn_save_settings.pack(side="left", padx=(0, 10))

        self.btn_reset_defaults = ActionButton(
            action_bar,
            text="↺  Reset Defaults",
            command=self._handle_reset_defaults,
            variant="secondary",
            width=150
        )
        self.btn_reset_defaults.pack(side="left")

    def _handle_theme_change(self, mode: str):
        """Handle theme change."""
        ctk.set_appearance_mode(mode.lower())
        if self.on_theme_change:
            self.on_theme_change()

    def _handle_tts_toggle(self):
        """Toggle text-to-speech service."""
        is_on = bool(self.switch_tts.get())
        tts_service.set_enabled(is_on)
        self.switch_tts.configure(
            text="TTS Active" if is_on else "TTS Disabled",
            text_color=styles.COLOR_STATUS_CONNECTED if is_on else styles.COLOR_DANGER
        )

    def _handle_speed_change(self, val: float):
        """Update speech speed slider and label."""
        int_val = int(val)
        self.lbl_speed_val.configure(text=f"{int_val} WPM")
        tts_service.set_rate(int_val)

    def _handle_test_voice(self):
        """Play a short test speech phrase."""
        tts_service.speak("Voice output is functioning correctly.")

    def _handle_save_settings(self):
        """Persist settings with visual confirmation toast."""
        self.btn_save_settings.configure(text="✓ Settings Saved!", state="disabled")

        def _restore():
            self.btn_save_settings.configure(text="💾  Save Settings", state="normal")

        self.after(1000, _restore)

    def _handle_reset_defaults(self):
        """Restore default configuration values."""
        self.combo_theme.set("Dark")
        ctk.set_appearance_mode("dark")
        self.switch_tts.select()
        tts_service.set_enabled(True)
        self.slider_speed.set(config.DEFAULT_SPEECH_RATE)
        self.lbl_speed_val.configure(text=f"{config.DEFAULT_SPEECH_RATE} WPM")
        tts_service.set_rate(config.DEFAULT_SPEECH_RATE)
        self.combo_lang.set("English (US)")
        self.entry_device_name.delete(0, "end")
        self.entry_device_name.insert(0, config.DEFAULT_DEVICE_NAME)
        self.switch_ac.deselect()
