"""
Translation History Page for the Sign Language Translator GUI.
Provides a searchable and filterable archive of past translation records,
confidence tracking, per-row audio speech playback, and export/clear controls.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any, List

import frontend.config as config
import frontend.ui.styles as styles
from frontend.ui.components import Card, StatusBadge, ActionButton, StatCard
from frontend.services.api_client import api_client
from frontend.services.tts_service import tts_service


class HistoryRecordRow(ctk.CTkFrame):
    """
    Tabular row representing a single translation history record.
    """

    def __init__(self, master, record: Dict[str, Any], on_speak: Optional[callable] = None, **kwargs):
        super().__init__(
            master,
            fg_color=styles.COLOR_BG_SUBTLE,
            corner_radius=styles.RADIUS_BUTTON,
            height=46,
            **kwargs
        )
        self.pack_propagate(False)
        self.record = record
        self.on_speak = on_speak

        self.pack(fill="x", pady=3, padx=styles.PAD_LG)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12)

        # 1. Timestamp Column
        time_str = record.get("time", "--:--")
        lbl_time = ctk.CTkLabel(
            inner,
            text=time_str,
            font=styles.FONT_MONO,
            text_color=styles.COLOR_TEXT_MUTED,
            width=80,
            anchor="w"
        )
        lbl_time.pack(side="left")

        # 2. Detected Sign Column
        sign_str = record.get("sign", "—")
        lbl_sign = ctk.CTkLabel(
            inner,
            text=sign_str,
            font=styles.FONT_BODY_BOLD,
            text_color=styles.COLOR_TEXT_PRIMARY,
            width=150,
            anchor="w"
        )
        lbl_sign.pack(side="left")

        # 3. Translation Text Column
        trans_str = record.get("translation", "—")
        lbl_trans = ctk.CTkLabel(
            inner,
            text=f'"{trans_str}"',
            font=("Segoe UI", 12, "italic"),
            text_color=styles.COLOR_STATUS_READY,
            anchor="w"
        )
        lbl_trans.pack(side="left", fill="x", expand=True, padx=8)

        # 4. Confidence Chip Column
        conf = record.get("confidence", 0.0)
        conf_pct = int(conf * 100)
        conf_color = styles.COLOR_STATUS_CONNECTED if conf >= 0.90 else (
            styles.COLOR_STATUS_DETECTING if conf >= 0.70 else styles.COLOR_DANGER
        )
        conf_bg = styles.COLOR_STATUS_CONNECTED_BG if conf >= 0.90 else (
            styles.COLOR_STATUS_DETECTING_BG if conf >= 0.70 else styles.COLOR_DANGER_BG
        )

        conf_frame = ctk.CTkFrame(
            inner,
            fg_color=conf_bg,
            corner_radius=styles.RADIUS_BADGE,
            border_width=1,
            border_color=conf_color,
            width=120,
            height=26
        )
        conf_frame.pack_propagate(False)
        conf_frame.pack(side="left", padx=10)

        lbl_conf = ctk.CTkLabel(
            conf_frame,
            text=f"{conf_pct}% (Simulated)",
            font=styles.FONT_BADGE,
            text_color=conf_color
        )
        lbl_conf.pack(expand=True)

        # 5. Audio Playback Action Button
        btn_speak = ActionButton(
            inner,
            text="🔊 Speak",
            command=self._handle_speak,
            variant="secondary",
            width=85,
            height=28
        )
        btn_speak.pack(side="right")

    def _handle_speak(self):
        text = self.record.get("translation", "")
        if text and text != "—":
            tts_service.speak(text)


class HistoryPage(ctk.CTkFrame):
    """
    Page 5: Translation History and Session Archive.
    """

    def __init__(self, master, on_status_change: Optional[callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_status_change = on_status_change

        self.rendered_rows: List[HistoryRecordRow] = []

        self._build_header()
        self._build_summary_kpis()
        self._build_toolbar()
        self._build_records_table()
        self.refresh_ui()

    def _build_header(self):
        """Render page header title and subtitle."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Translation History",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Search, filter, and review captured signs and translation records (Simulated).",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def _build_summary_kpis(self):
        """Render top 3 metric cards summarizing session history."""
        kpi_grid = ctk.CTkFrame(self, fg_color="transparent")
        kpi_grid.pack(fill="x", pady=(0, styles.PAD_MD))
        for col_idx in range(3):
            kpi_grid.grid_columnconfigure(col_idx, weight=1, uniform="hist_kpi")

        self.card_total = StatCard(
            kpi_grid,
            title="Total Translations",
            value="4 Saved",
            subtext="Captured in current session",
            accent_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.card_total.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        self.card_avg_conf = StatCard(
            kpi_grid,
            title="Average Confidence",
            value="94% (Simulated)",
            subtext="High recognition consistency",
            accent_color=styles.COLOR_STATUS_CONNECTED
        )
        self.card_avg_conf.grid(row=0, column=1, padx=4, sticky="nsew")

        self.card_session = StatCard(
            kpi_grid,
            title="Session Archive",
            value="Active (Simulated)",
            subtext="Local memory storage",
            accent_color=styles.COLOR_STATUS_READY
        )
        self.card_session.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

    def _build_toolbar(self):
        """Render search entry, filter option menu, and export/clear controls."""
        toolbar_card = Card(self)
        toolbar_card.pack(fill="x", pady=(0, styles.PAD_MD))

        inner = ctk.CTkFrame(toolbar_card, fg_color="transparent")
        inner.pack(fill="x", padx=styles.PAD_LG, pady=10)

        # Left: Search Entry
        self.entry_search = ctk.CTkEntry(
            inner,
            placeholder_text="🔍  Search signs, translations, or timestamps...",
            font=styles.FONT_BODY,
            fg_color=styles.COLOR_BG_SUBTLE,
            border_color=styles.COLOR_BORDER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=36,
            width=320,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda event: self._filter_records())

        # Filter OptionMenu
        self.combo_filter = ctk.CTkOptionMenu(
            inner,
            values=["All Records", "High Confidence (≥90%)", "Moderate (<90%)"],
            command=lambda val: self._filter_records(),
            font=styles.FONT_BODY,
            fg_color=styles.COLOR_BG_SUBTLE,
            button_color=styles.COLOR_BTN_SECONDARY_HOVER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=36,
            width=180,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.combo_filter.pack(side="left")

        # Right: Export & Clear Buttons
        self.btn_clear = ActionButton(
            inner,
            text="🗑  Clear History",
            command=self._handle_clear_history,
            variant="danger",
            width=130
        )
        self.btn_clear.pack(side="right")

        self.btn_export = ActionButton(
            inner,
            text="📋  Copy Log",
            command=self._handle_export_log,
            variant="secondary",
            width=110
        )
        self.btn_export.pack(side="right", padx=(0, 8))

    def _build_records_table(self):
        """Construct the table structure with fixed header and scrollable records frame."""
        self.table_card = Card(self)
        self.table_card.pack(fill="both", expand=True)

        # Table Column Headers
        header_row = ctk.CTkFrame(self.table_card, fg_color="transparent")
        header_row.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_h_time = ctk.CTkLabel(header_row, text="TIME", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_MUTED, width=80, anchor="w")
        lbl_h_time.pack(side="left")

        lbl_h_sign = ctk.CTkLabel(header_row, text="DETECTED SIGN", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_MUTED, width=150, anchor="w")
        lbl_h_sign.pack(side="left")

        lbl_h_trans = ctk.CTkLabel(header_row, text="TRANSLATION", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_MUTED, anchor="w")
        lbl_h_trans.pack(side="left", fill="x", expand=True, padx=8)

        lbl_h_conf = ctk.CTkLabel(header_row, text="CONFIDENCE", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_MUTED, width=120, anchor="center")
        lbl_h_conf.pack(side="left", padx=10)

        lbl_h_action = ctk.CTkLabel(header_row, text="ACTION", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_MUTED, width=85, anchor="e")
        lbl_h_action.pack(side="right")

        # Divider
        divider = ctk.CTkFrame(self.table_card, height=1, fg_color=styles.COLOR_BORDER_LIGHT)
        divider.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))

        # Scrollable Container for Rows
        self.records_scroll = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent", corner_radius=0)
        self.records_scroll.pack(fill="both", expand=True, pady=(0, styles.PAD_SM))

        # Empty State Placeholder Frame
        self.empty_frame = ctk.CTkFrame(self.records_scroll, fg_color="transparent")
        lbl_empty_icon = ctk.CTkLabel(self.empty_frame, text="🕒", font=("Segoe UI", 36))
        lbl_empty_icon.pack(pady=(40, 8))

        lbl_empty_title = ctk.CTkLabel(self.empty_frame, text="No Translation Records Found", font=styles.FONT_TITLE, text_color=styles.COLOR_TEXT_PRIMARY)
        lbl_empty_title.pack(pady=2)

        lbl_empty_sub = ctk.CTkLabel(
            self.empty_frame,
            text="Saved translations from active detection sessions will be archived here.",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_empty_sub.pack(pady=4)

    def refresh_ui(self):
        """Reload records from ApiClient and update summary KPIs."""
        records = api_client.get_history()

        # Update Summary KPIs
        total_count = len(records)
        self.card_total.update_value(f"{total_count} Saved", "Captured in current session")

        if total_count > 0:
            avg_c = sum(r.get("confidence", 0.0) for r in records) / total_count
            self.card_avg_conf.update_value(f"{int(avg_c * 100)}% (Simulated)", "High recognition consistency")
        else:
            self.card_avg_conf.update_value("—", "No data")

        self._filter_records()

    def _filter_records(self):
        """Filter records by search keyword and confidence category."""
        query = self.entry_search.get().strip().lower()
        filter_mode = self.combo_filter.get()

        # Clear existing row widgets
        for row in self.rendered_rows:
            row.destroy()
        self.rendered_rows.clear()

        all_records = api_client.get_history()
        filtered = []

        for r in all_records:
            sign = r.get("sign", "").lower()
            trans = r.get("translation", "").lower()
            t_str = r.get("time", "").lower()
            conf = r.get("confidence", 0.0)

            # Query check
            if query and not (query in sign or query in trans or query in t_str):
                continue

            # Category check
            if "High" in filter_mode and conf < 0.90:
                continue
            elif "Moderate" in filter_mode and conf >= 0.90:
                continue

            filtered.append(r)

        # Render rows or show empty state
        if not filtered:
            self.empty_frame.pack(fill="both", expand=True)
        else:
            self.empty_frame.pack_forget()
            for rec in filtered:
                row_w = HistoryRecordRow(self.records_scroll, record=rec)
                self.rendered_rows.append(row_w)

    def _handle_clear_history(self):
        """Clear all historical records."""
        api_client.clear_history()
        self.refresh_ui()
        if self.on_status_change:
            self.on_status_change()

    def _handle_export_log(self):
        """Copy formatted transcript to clipboard."""
        records = api_client.get_history()
        lines = [f"{config.APP_NAME} — Translation History Log (Simulated)"]
        lines.append("=" * 60)
        for r in records:
            lines.append(f"[{r.get('time', '--:--')}] {r.get('sign', '—')} -> \"{r.get('translation', '—')}\" (Confidence: {int(r.get('confidence', 0.0) * 100)}%)")
        lines.append("=" * 60)
        lines.append(f"Total Records: {len(records)}")

        transcript_text = "\n".join(lines)
        try:
            self.clipboard_clear()
            self.clipboard_append(transcript_text)
            self.btn_export.configure(text="✓ Copied!", state="disabled")

            def _reset_btn():
                self.btn_export.configure(text="📋  Copy Log", state="normal")

            self.after(1000, _reset_btn)
        except Exception:
            pass

    def on_page_show(self):
        """Lifecycle hook when navigating to History page."""
        self.refresh_ui()
