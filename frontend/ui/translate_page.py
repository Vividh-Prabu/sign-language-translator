"""
Translation Studio Page for the Sign Language Translator GUI.
Provides the primary sign detection studio, real-time sign and translation display,
confidence rating meter, stream controls (Start/Stop), word/sentence builder,
and audio speech actions.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any

import frontend.config as config
import frontend.ui.styles as styles
from frontend.ui.components import Card, StatusBadge, ActionButton
from frontend.services.api_client import api_client
from frontend.services.tts_service import tts_service
from frontend.services.word_builder import word_builder


class TranslatePage(ctk.CTkFrame):
    """
    Page 4: Main Sign Language Translation Studio.
    """

    def __init__(self, master, on_status_change: Optional[callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_status_change = on_status_change

        self.detecting = False
        self._detection_job = None
        self._processing_job = None

        self._build_header()
        self._build_status_strip()
        self._build_translation_display()
        self._build_sentence_builder()
        self.refresh_ui()

    def _build_header(self):
        """Render page header title and subtitle."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Translation Studio",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Live gesture detection display, confidence metrics, and sentence assembly (Simulated).",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def _build_status_strip(self):
        """Render top status banner with glove status and detection state."""
        strip = Card(self)
        strip.pack(fill="x", pady=(0, styles.PAD_MD))

        inner = ctk.CTkFrame(strip, fg_color="transparent")
        inner.pack(fill="x", padx=styles.PAD_LG, pady=10)

        # Left: Glove Status Badge & Detection Status Badge
        self.badge_glove = StatusBadge(inner, status_type="connected", text="Glove: Connected (Simulated)")
        self.badge_glove.pack(side="left", padx=(0, 10))

        self.badge_detection = StatusBadge(inner, status_type="ready", text="Detection: Ready")
        self.badge_detection.pack(side="left")

        # Right: Last recognition event timestamp & Auto-Speak switch
        right_box = ctk.CTkFrame(inner, fg_color="transparent")
        right_box.pack(side="right")

        self.switch_autospeak = ctk.CTkSwitch(
            right_box,
            text="Auto-Speak Signs",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_SECONDARY,
            progress_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.switch_autospeak.pack(side="right", padx=(14, 0))

        self.lbl_timestamp = ctk.CTkLabel(
            right_box,
            text="Last Event: 10:42:15",
            font=styles.FONT_MONO,
            text_color=styles.COLOR_TEXT_MUTED
        )
        self.lbl_timestamp.pack(side="right")

    def _build_translation_display(self):
        """Construct the central live sign detection panel and toolbar."""
        studio_card = Card(self)
        studio_card.pack(fill="x", pady=(0, styles.PAD_MD))

        # Header Row
        card_header = ctk.CTkFrame(studio_card, fg_color="transparent")
        card_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_section = ctk.CTkLabel(
            card_header,
            text="LIVE SIGN DETECTION FEED (SIMULATED)",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_section.pack(side="left")

        self.badge_live = StatusBadge(card_header, status_type="ready", text="Telemetry Active")
        self.badge_live.pack(side="right")

        # Main Display Container
        display_frame = ctk.CTkFrame(studio_card, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_CARD)
        display_frame.pack(fill="x", padx=styles.PAD_LG, pady=styles.PAD_SM)

        inner_grid = ctk.CTkFrame(display_frame, fg_color="transparent")
        inner_grid.pack(fill="x", padx=styles.PAD_MD, pady=styles.PAD_LG)
        inner_grid.grid_columnconfigure(0, weight=1)
        inner_grid.grid_columnconfigure(1, weight=1)

        # Left Column: Detected Sign
        left_box = ctk.CTkFrame(inner_grid, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="w", padx=styles.PAD_SM)

        lbl_sign_tag = ctk.CTkLabel(
            left_box,
            text="DETECTED SIGN",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_sign_tag.pack(anchor="w")

        self.lbl_sign = ctk.CTkLabel(
            left_box,
            text="HELLO",
            font=("Segoe UI", 36, "bold"),
            text_color=styles.COLOR_TEXT_PRIMARY
        )
        self.lbl_sign.pack(anchor="w", pady=(4, 0))

        # Right Column: Translated Text
        right_box = ctk.CTkFrame(inner_grid, fg_color="transparent")
        right_box.grid(row=0, column=1, sticky="w", padx=styles.PAD_SM)

        lbl_trans_tag = ctk.CTkLabel(
            right_box,
            text="TRANSLATED TEXT",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_trans_tag.pack(anchor="w")

        self.lbl_translation = ctk.CTkLabel(
            right_box,
            text='"Hello"',
            font=("Segoe UI", 30, "italic"),
            text_color=styles.COLOR_STATUS_READY
        )
        self.lbl_translation.pack(anchor="w", pady=(4, 0))

        # Confidence Meter Bar
        confidence_row = ctk.CTkFrame(studio_card, fg_color="transparent")
        confidence_row.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_SM))

        self.lbl_confidence = ctk.CTkLabel(
            confidence_row,
            text="Confidence: 94% (Simulated)",
            font=styles.FONT_BODY_BOLD,
            text_color=styles.COLOR_STATUS_CONNECTED,
            width=180,
            anchor="w"
        )
        self.lbl_confidence.pack(side="left")

        self.progress_confidence = ctk.CTkProgressBar(
            confidence_row,
            height=10,
            corner_radius=5,
            progress_color=styles.COLOR_STATUS_CONNECTED,
            fg_color=styles.COLOR_BG_SUBTLE
        )
        self.progress_confidence.pack(side="left", fill="x", expand=True, padx=(10, 14))
        self.progress_confidence.set(0.94)

        self.lbl_quality = ctk.CTkLabel(
            confidence_row,
            text="High Confidence",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_SECONDARY
        )
        self.lbl_quality.pack(side="right")

        # Action Toolbar
        toolbar = ctk.CTkFrame(studio_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_MD))

        # Left Group: Detection Stream Controls
        self.btn_start = ActionButton(
            toolbar,
            text="▶  Start Detection",
            command=self._handle_start_detection,
            variant="primary",
            width=150
        )
        self.btn_start.pack(side="left", padx=(0, 8))

        self.btn_stop = ActionButton(
            toolbar,
            text="⏹  Stop Detection",
            command=self._handle_stop_detection,
            variant="secondary",
            width=140
        )
        self.btn_stop.pack(side="left", padx=(0, 8))
        self.btn_stop.configure(state="disabled")

        self.btn_simulate = ActionButton(
            toolbar,
            text="⚡  Simulate Sign",
            command=self._handle_simulate_sign,
            variant="secondary",
            width=140
        )
        self.btn_simulate.pack(side="left", padx=(0, 8))

        # Right Group: Audio & Save
        self.btn_save = ActionButton(
            toolbar,
            text="💾  Save",
            command=self._handle_save,
            variant="secondary",
            width=100
        )
        self.btn_save.pack(side="right")

        self.btn_clear = ActionButton(
            toolbar,
            text="🗑  Clear",
            command=self._handle_clear,
            variant="secondary",
            width=100
        )
        self.btn_clear.pack(side="right", padx=(0, 8))

        self.btn_speak = ActionButton(
            toolbar,
            text="🔊  Speak",
            command=self._handle_speak,
            variant="primary",
            width=110
        )
        self.btn_speak.pack(side="right", padx=(0, 8))

    def _build_sentence_builder(self):
        """Construct the Word / Sentence Builder section."""
        builder_card = Card(self)
        builder_card.pack(fill="both", expand=True)

        header_row = ctk.CTkFrame(builder_card, fg_color="transparent")
        header_row.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_b_title = ctk.CTkLabel(
            header_row,
            text="SENTENCE & WORD BUILDER",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_b_title.pack(side="left")

        self.switch_autoappend = ctk.CTkSwitch(
            header_row,
            text="Auto-append signs to sentence",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED,
            progress_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.switch_autoappend.pack(side="right")
        self.switch_autoappend.select()

        # Sentence Text View
        self.txt_sentence = ctk.CTkTextbox(
            builder_card,
            font=("Segoe UI", 15),
            fg_color=styles.COLOR_BG_SUBTLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            corner_radius=styles.RADIUS_BUTTON,
            border_width=1,
            border_color=styles.COLOR_BORDER_LIGHT,
            height=70,
            wrap="word"
        )
        self.txt_sentence.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))
        self._update_sentence_view()

        # Sentence Controls Row
        ctrl_row = ctk.CTkFrame(builder_card, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        btn_space = ActionButton(
            ctrl_row,
            text="␣  Space",
            command=self._handle_add_space,
            variant="secondary",
            width=95
        )
        btn_space.pack(side="left", padx=(0, 6))

        btn_backspace = ActionButton(
            ctrl_row,
            text="⌫  Backspace",
            command=self._handle_backspace,
            variant="secondary",
            width=115
        )
        btn_backspace.pack(side="left", padx=(0, 6))

        btn_clear_sent = ActionButton(
            ctrl_row,
            text="🗑  Clear Sentence",
            command=self._handle_clear_sentence,
            variant="secondary",
            width=140
        )
        btn_clear_sent.pack(side="left")

        btn_speak_sent = ActionButton(
            ctrl_row,
            text="🔊  Speak Full Sentence",
            command=self._handle_speak_sentence,
            variant="primary",
            width=180
        )
        btn_speak_sent.pack(side="right")

    def refresh_ui(self):
        """Update display with latest ApiClient values."""
        glove_info = api_client.get_glove_status()
        is_connected = glove_info["connected"]

        self.badge_glove.set_status(
            "connected" if is_connected else "disconnected",
            "Glove: Connected (Simulated)" if is_connected else "Glove: Disconnected"
        )

        if not is_connected:
            self.badge_detection.set_status("error", "Detection: Glove Offline")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
            self.btn_simulate.configure(state="disabled")
            return

        if not self.detecting:
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_simulate.configure(state="normal")
            self.badge_detection.set_status("ready", "Detection: Ready")
        else:
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.btn_simulate.configure(state="normal")

        # Load active translation
        curr = api_client.get_current_translation()
        self._render_translation(curr)

    def _render_translation(self, trans_dict: Dict[str, Any]):
        """Render sign, translation, confidence, and timestamp."""
        sign = trans_dict.get("sign", "—")
        text = trans_dict.get("translation", "Waiting for sign...")
        conf = trans_dict.get("confidence", 0.0)
        ts = trans_dict.get("timestamp", "")

        self.lbl_sign.configure(text=sign)
        self.lbl_translation.configure(text=f'"{text}"' if sign != "—" else text)

        conf_pct = int(conf * 100)
        self.lbl_confidence.configure(text=f"Confidence: {conf_pct}% (Simulated)")
        self.progress_confidence.set(conf)

        if conf >= 0.90:
            self.progress_confidence.configure(progress_color=styles.COLOR_STATUS_CONNECTED)
            self.lbl_quality.configure(text="High Confidence", text_color=styles.COLOR_STATUS_CONNECTED)
        elif conf >= 0.70:
            self.progress_confidence.configure(progress_color=styles.COLOR_STATUS_DETECTING)
            self.lbl_quality.configure(text="Moderate Confidence", text_color=styles.COLOR_STATUS_DETECTING)
        else:
            self.progress_confidence.configure(progress_color=styles.COLOR_STATUS_DISCONNECTED)
            self.lbl_quality.configure(text="Low / Calibration Required", text_color=styles.COLOR_STATUS_DISCONNECTED)

        if ts:
            self.lbl_timestamp.configure(text=f"Last Event: {ts}")

    def _handle_start_detection(self):
        """Start the simulated sign detection stream."""
        if not api_client.get_glove_status()["connected"]:
            return

        self.detecting = True
        api_client.start_detection()
        self.badge_detection.set_status("detecting", "Detection: Detecting...")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        if self.on_status_change:
            self.on_status_change()

        self._schedule_next_detection()

    def _handle_stop_detection(self):
        """Stop the sign detection stream."""
        self.detecting = False
        api_client.stop_detection()
        self._cancel_detection_jobs()

        self.badge_detection.set_status("ready", "Detection: Ready")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")

        if self.on_status_change:
            self.on_status_change()

    def _schedule_next_detection(self):
        """Schedule the next simulated detection pulse."""
        if not self.detecting:
            return

        # 1. Brief processing state
        def _to_processing():
            if not self.detecting:
                return
            self.badge_detection.set_status("processing", "Detection: Processing...")

            # 2. Complete recognition after 400ms
            def _resolve_sign():
                if not self.detecting:
                    return
                self._handle_simulate_sign()
                self.badge_detection.set_status("detecting", "Detection: Detecting...")
                # Schedule next detection cycle after 2.5 seconds
                self._detection_job = self.after(2500, self._schedule_next_detection)

            self._processing_job = self.after(400, _resolve_sign)

        self._detection_job = self.after(2000, _to_processing)

    def _cancel_detection_jobs(self):
        """Cancel all pending detection timer jobs."""
        if self._detection_job:
            self.after_cancel(self._detection_job)
            self._detection_job = None
        if self._processing_job:
            self.after_cancel(self._processing_job)
            self._processing_job = None

    def _handle_simulate_sign(self):
        """Step to the next mock sign manually or via timer."""
        item = api_client.get_next_mock_sign()
        self._render_translation(item)

        # Auto-append to sentence builder if toggled
        if bool(self.switch_autoappend.get()) and item.get("translation"):
            word_builder.add_sign(item["translation"])
            self._update_sentence_view()

        # Auto-speak if toggled
        if bool(self.switch_autospeak.get()) and item.get("translation"):
            tts_service.speak(item["translation"])

        if self.on_status_change:
            self.on_status_change()

    def _handle_speak(self):
        """Speak the currently displayed translation."""
        curr = api_client.get_current_translation()
        text = curr.get("translation", "")
        if text and text != "—":
            tts_service.speak(text)

    def _handle_clear(self):
        """Clear active sign translation display."""
        api_client.clear_current_translation()
        self._render_translation(api_client.get_current_translation())

    def _handle_save(self):
        """Save active translation to history."""
        saved = api_client.save_current_translation()
        if saved:
            self.btn_save.configure(text="✓ Saved!", state="disabled")

            def _restore_btn():
                self.btn_save.configure(text="💾  Save", state="normal")

            self.after(1000, _restore_btn)
            if self.on_status_change:
                self.on_status_change()

    # --- Sentence / Word Builder Handlers ---
    def _update_sentence_view(self):
        """Refresh sentence text box."""
        self.txt_sentence.configure(state="normal")
        self.txt_sentence.delete("1.0", "end")
        text = word_builder.get_text()
        if text:
            self.txt_sentence.insert("1.0", text)
        else:
            self.txt_sentence.insert("1.0", "[No sentence assembled yet. Detected signs will appear here...]")
        self.txt_sentence.configure(state="disabled")

    def _handle_add_space(self):
        """Add space delimiter to sentence."""
        word_builder.add_space()
        self._update_sentence_view()

    def _handle_backspace(self):
        """Backspace last token/character."""
        word_builder.backspace()
        self._update_sentence_view()

    def _handle_clear_sentence(self):
        """Clear entire assembled sentence."""
        word_builder.clear()
        self._update_sentence_view()

    def _handle_speak_sentence(self):
        """Speak the full assembled sentence."""
        sentence = word_builder.get_text()
        if sentence:
            tts_service.speak(sentence)

    # --- Page Lifecycle ---
    def on_page_show(self):
        """Invoked when navigating to this page."""
        self.refresh_ui()

    def on_page_hide(self):
        """Invoked when navigating away from this page."""
        if self.detecting:
            self._handle_stop_detection()
