"""
Sensor Monitoring & Telemetry Page for the Sign Language Translator GUI.
Provides configurable sensor channel visualization, bend meters,
optional orientation metrics, stream controls, and raw packet diagnostics.
"""

import json
import random
import customtkinter as ctk
from typing import Dict, Any, List, Optional

import frontend.config as config
import frontend.ui.styles as styles
from frontend.ui.components import Card, StatusBadge, ActionButton
from frontend.services.api_client import api_client


class SensorChannelRow(ctk.CTkFrame):
    """
    Modular row displaying a single configurable sensor channel
    with high-contrast progress meter, percentage, and simulated ADC values.
    """

    def __init__(self, master, channel_id: str, name: str, value: int = 0, raw_adc: int = 0, **kwargs):
        super().__init__(master, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_BUTTON, **kwargs)

        self.channel_id = channel_id
        self.channel_name = name
        self.current_val = value

        self.pack(fill="x", pady=4, padx=styles.PAD_LG)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        # Top row: Channel Name, ID Tag, Value
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 6))

        # Left: Channel ID badge + Name
        lbl_tag = ctk.CTkLabel(
            top_row,
            text=f" {channel_id} ",
            font=styles.FONT_BADGE,
            fg_color=styles.COLOR_ACCENT_BG,
            text_color=styles.COLOR_STATUS_READY,
            corner_radius=4
        )
        lbl_tag.pack(side="left", padx=(0, 8))

        self.lbl_name = ctk.CTkLabel(
            top_row,
            text=name,
            font=styles.FONT_BODY_BOLD,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_name.pack(side="left")

        # Right: Value Readout
        self.lbl_readout = ctk.CTkLabel(
            top_row,
            text=f"{value}%  (ADC: {raw_adc})",
            font=styles.FONT_MONO,
            text_color=styles.COLOR_STATUS_READY,
            anchor="e"
        )
        self.lbl_readout.pack(side="right")

        # Middle: High-Contrast Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            inner,
            height=12,
            corner_radius=6,
            progress_color=styles.COLOR_ACCENT_PRIMARY,
            fg_color=styles.COLOR_BG_CARD
        )
        self.progress_bar.pack(fill="x", pady=(0, 4))
        self.progress_bar.set(max(0.0, min(1.0, value / 100.0)))

        # Bottom row: Min/Max calibration markers
        marker_row = ctk.CTkFrame(inner, fg_color="transparent")
        marker_row.pack(fill="x")

        lbl_min = ctk.CTkLabel(marker_row, text="0% (Rest)", font=styles.FONT_SMALL, text_color=styles.COLOR_TEXT_MUTED)
        lbl_min.pack(side="left")

        lbl_mid = ctk.CTkLabel(marker_row, text="50%", font=styles.FONT_SMALL, text_color=styles.COLOR_TEXT_MUTED)
        lbl_mid.pack(side="left", expand=True)

        lbl_max = ctk.CTkLabel(marker_row, text="100% (Flexed)", font=styles.FONT_SMALL, text_color=styles.COLOR_TEXT_MUTED)
        lbl_max.pack(side="right")

    def update_value(self, value: int, raw_adc: Optional[int] = None):
        """Update channel readout and progress bar smoothly."""
        self.current_val = value
        adc = raw_adc if raw_adc is not None else int(value * 40.95)
        self.lbl_readout.configure(text=f"{value}%  (ADC: {adc})")
        self.progress_bar.set(max(0.0, min(1.0, value / 100.0)))

        # Color-shift if highly flexed
        if value > 80:
            self.progress_bar.configure(progress_color=styles.COLOR_STATUS_CONNECTED)
        elif value > 40:
            self.progress_bar.configure(progress_color=styles.COLOR_ACCENT_PRIMARY)
        else:
            self.progress_bar.configure(progress_color=styles.COLOR_STATUS_READY)


class SensorsPage(ctk.CTkFrame):
    """
    Page 3: Sensor Monitoring & Telemetry Studio.
    Displays dynamic bend sensor channel rows, orientation meters,
    stream controls, and raw packet diagnostics.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.stream_active = True
        self.orientation_enabled = True
        self.channel_rows: Dict[str, SensorChannelRow] = {}
        self._polling_job = None

        self._build_header()
        self._build_stream_toolbar()
        self._build_body()
        self.refresh_ui()

    def _build_header(self):
        """Render page title and subtitle."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Live Sensor Telemetry",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Real-time sensor channels, bend meters, and telemetry diagnostics (Simulated).",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def _build_stream_toolbar(self):
        """Render stream control toolbar with Pause, Resume, Calibrate, and Status."""
        toolbar = Card(self)
        toolbar.pack(fill="x", pady=(0, styles.PAD_MD))

        inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        inner.pack(fill="x", padx=styles.PAD_LG, pady=10)

        # Left: Stream Status Badge
        self.badge_stream = StatusBadge(inner, status_type="connected", text="Stream: Active (Simulated)")
        self.badge_stream.pack(side="left", padx=(0, 12))

        # Stream Pause / Resume Button
        self.btn_pause = ActionButton(
            inner,
            text="⏸  Pause Stream",
            command=self._toggle_stream,
            variant="secondary",
            width=140
        )
        self.btn_pause.pack(side="left", padx=(0, 8))

        # Baseline Calibration Button
        self.btn_calibrate = ActionButton(
            inner,
            text="🎯  Calibrate Baseline",
            command=self._handle_calibrate,
            variant="secondary",
            width=160
        )
        self.btn_calibrate.pack(side="left", padx=(0, 8))

        # Right: Polling Frequency Dropdown
        right_f = ctk.CTkFrame(inner, fg_color="transparent")
        right_f.pack(side="right")

        lbl_rate = ctk.CTkLabel(right_f, text="Sampling Rate:", font=styles.FONT_SMALL, text_color=styles.COLOR_TEXT_MUTED)
        lbl_rate.pack(side="left", padx=(0, 6))

        self.rate_combo = ctk.CTkOptionMenu(
            right_f,
            values=["50 Hz (Default)", "20 Hz", "10 Hz"],
            font=styles.FONT_SMALL,
            fg_color=styles.COLOR_BG_SUBTLE,
            button_color=styles.COLOR_BTN_SECONDARY_HOVER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=30,
            width=120,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.rate_combo.pack(side="left")

    def _build_body(self):
        """Construct the 2-column layout (Channels on left, Orientation & Packet Inspector on right)."""
        body_grid = ctk.CTkFrame(self, fg_color="transparent")
        body_grid.pack(fill="both", expand=True)
        body_grid.grid_columnconfigure(0, weight=5, uniform="sensor_cols")
        body_grid.grid_columnconfigure(1, weight=4, uniform="sensor_cols")
        body_grid.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT COLUMN: Configurable Sensor Channels
        # ==========================================
        left_card = Card(body_grid)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Header of Left Card
        ch_header = ctk.CTkFrame(left_card, fg_color="transparent")
        ch_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_ch_title = ctk.CTkLabel(
            ch_header,
            text="CONFIGURABLE SENSOR CHANNELS",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_ch_title.pack(side="left")

        lbl_ch_count = ctk.CTkLabel(
            ch_header,
            text="5 Active Channels",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_STATUS_READY
        )
        lbl_ch_count.pack(side="right")

        # Scrollable / Packing Container for Channel Rows
        self.channels_container = ctk.CTkScrollableFrame(
            left_card,
            fg_color="transparent",
            corner_radius=0
        )
        self.channels_container.pack(fill="both", expand=True, pady=(0, styles.PAD_SM))

        # Instantiate dynamic channel rows from ApiClient
        channel_data = api_client.get_sensor_channels()
        for ch in channel_data:
            cid = ch["channel_id"]
            row = SensorChannelRow(
                self.channels_container,
                channel_id=cid,
                name=ch["name"],
                value=ch["value"],
                raw_adc=ch["raw_adc"]
            )
            self.channel_rows[cid] = row

        # Disclaimer footer
        ch_footer = ctk.CTkFrame(left_card, fg_color="transparent")
        ch_footer.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        lbl_ch_note = ctk.CTkLabel(
            ch_footer,
            text="ⓘ Channels are dynamically reconfigurable once physical sensor specs are confirmed.",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED,
            anchor="w"
        )
        lbl_ch_note.pack(fill="x")

        # ==========================================
        # RIGHT COLUMN: Orientation & Raw Inspector
        # ==========================================
        right_container = ctk.CTkFrame(body_grid, fg_color="transparent")
        right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- Sub-Card 1: Orientation & Motion Telemetry ---
        self.imu_card = Card(right_container)
        self.imu_card.pack(fill="x", pady=(0, styles.PAD_MD))

        imu_header = ctk.CTkFrame(self.imu_card, fg_color="transparent")
        imu_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_imu_title = ctk.CTkLabel(
            imu_header,
            text="ORIENTATION & MOTION (SIMULATED)",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_imu_title.pack(side="left")

        # Switch to enable/disable IMU display
        self.switch_imu = ctk.CTkSwitch(
            imu_header,
            text="Enable IMU",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED,
            command=self._toggle_imu
        )
        self.switch_imu.pack(side="right")
        self.switch_imu.select()

        # IMU Axis Container
        self.imu_body = ctk.CTkFrame(self.imu_card, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_BUTTON)
        self.imu_body.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))

        self.axis_labels: Dict[str, ctk.CTkLabel] = {}
        self.axis_bars: Dict[str, ctk.CTkProgressBar] = {}

        orientation_data = api_client.get_orientation_data()
        for axis_name in ["X", "Y", "Z"]:
            axis_val = orientation_data.get(axis_name, 0.0)

            row_f = ctk.CTkFrame(self.imu_body, fg_color="transparent")
            row_f.pack(fill="x", padx=12, pady=6)

            lbl_a = ctk.CTkLabel(
                row_f,
                text=f"Axis {axis_name}",
                font=styles.FONT_BODY_BOLD,
                text_color=styles.COLOR_TEXT_PRIMARY,
                width=60,
                anchor="w"
            )
            lbl_a.pack(side="left")

            bar_a = ctk.CTkProgressBar(
                row_f,
                height=10,
                corner_radius=5,
                progress_color=styles.COLOR_STATUS_READY,
                fg_color=styles.COLOR_BG_CARD
            )
            bar_a.pack(side="left", fill="x", expand=True, padx=8)
            bar_a.set(max(0.0, min(1.0, (axis_val + 1.0) / 2.0)))  # Map -1.0..1.0 to 0.0..1.0
            self.axis_bars[axis_name] = bar_a

            val_a = ctk.CTkLabel(
                row_f,
                text=f"{axis_val:+.2f}",
                font=styles.FONT_MONO,
                text_color=styles.COLOR_STATUS_READY,
                width=55,
                anchor="e"
            )
            val_a.pack(side="right")
            self.axis_labels[axis_name] = val_a

        # IMU Disclaimer
        lbl_imu_note = ctk.CTkLabel(
            self.imu_card,
            text="ⓘ Optional module; hardware teammate will confirm accelerometer/gyro inclusion.",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        lbl_imu_note.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        # --- Sub-Card 2: Telemetry Packet Inspector ---
        raw_card = Card(right_container)
        raw_card.pack(fill="both", expand=True)

        raw_header = ctk.CTkFrame(raw_card, fg_color="transparent")
        raw_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_raw_title = ctk.CTkLabel(
            raw_header,
            text="RAW PACKET INSPECTOR (SIMULATED)",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_raw_title.pack(side="left")

        lbl_format = ctk.CTkLabel(
            raw_header,
            text="JSON Frame",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED
        )
        lbl_format.pack(side="right")

        # Monospace Text Box for JSON payload
        self.txt_inspector = ctk.CTkTextbox(
            raw_card,
            font=styles.FONT_MONO,
            fg_color=styles.COLOR_BG_SUBTLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            corner_radius=styles.RADIUS_BUTTON,
            border_width=1,
            border_color=styles.COLOR_BORDER_LIGHT,
            wrap="none",
            height=130
        )
        self.txt_inspector.pack(fill="both", expand=True, padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

    def refresh_ui(self):
        """Update all sensor meters and packet inspector with latest values."""
        glove_info = api_client.get_glove_status()
        is_connected = glove_info["connected"]

        if not is_connected:
            self.badge_stream.set_status("disconnected", "Stream: Offline (Glove Disconnected)")
            for row in self.channel_rows.values():
                row.update_value(0, 0)
            self._update_inspector({"error": "Glove disconnected", "status": "No active telemetry"})
            return

        if not self.stream_active:
            self.badge_stream.set_status("detecting", "Stream: Paused")
            return

        self.badge_stream.set_status("connected", "Stream: Active (Simulated)")

        # Fetch sensor channels with realistic subtle live jitter for visualization
        channels = api_client.get_sensor_channels()
        for ch in channels:
            cid = ch["channel_id"]
            if cid in self.channel_rows:
                # Add tiny realistic fluctuation (+/- 1) to show live heartbeat
                jitter = random.choice([-1, 0, 1]) if self.stream_active else 0
                val = max(0, min(100, ch["value"] + jitter))
                adc = int(val * 40.95)
                self.channel_rows[cid].update_value(val, adc)

        # Update Orientation
        if self.orientation_enabled:
            orient = api_client.get_orientation_data()
            for axis_name, bar in self.axis_bars.items():
                base_val = orient.get(axis_name, 0.0)
                jitter_val = base_val + (random.uniform(-0.02, 0.02) if self.stream_active else 0.0)
                norm_val = max(0.0, min(1.0, (jitter_val + 1.0) / 2.0))
                bar.set(norm_val)
                self.axis_labels[axis_name].configure(text=f"{jitter_val:+.2f}")

        # Update Packet Inspector
        packet = api_client.get_raw_packet()
        self._update_inspector(packet)

    def _update_inspector(self, packet_dict: Dict[str, Any]):
        """Format and display JSON packet in the monospace viewer."""
        self.txt_inspector.configure(state="normal")
        self.txt_inspector.delete("1.0", "end")
        formatted = json.dumps(packet_dict, indent=2)
        self.txt_inspector.insert("1.0", formatted)
        self.txt_inspector.configure(state="disabled")

    def _toggle_stream(self):
        """Toggle stream pause and resume."""
        self.stream_active = not self.stream_active
        if self.stream_active:
            self.btn_pause.configure(text="⏸  Pause Stream")
            self.refresh_ui()
            self._start_polling()
        else:
            self.btn_pause.configure(text="▶  Resume Stream")
            self.badge_stream.set_status("detecting", "Stream: Paused")
            self._stop_polling()

    def _toggle_imu(self):
        """Toggle visibility/processing of orientation IMU data."""
        self.orientation_enabled = bool(self.switch_imu.get())
        if self.orientation_enabled:
            self.imu_body.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))
        else:
            self.imu_body.pack_forget()

    def _handle_calibrate(self):
        """Trigger baseline calibration event."""
        api_client.calibrate_sensors()
        self.btn_calibrate.configure(text="✓ Calibrated!", state="disabled")

        def _reset_btn():
            self.btn_calibrate.configure(text="🎯  Calibrate Baseline", state="normal")

        self.after(1000, _reset_btn)

    def on_page_show(self):
        """Lifecycle hook when navigating to this page."""
        self.refresh_ui()
        self._start_polling()

    def on_page_hide(self):
        """Lifecycle hook when navigating away from this page."""
        self._stop_polling()

    def _start_polling(self):
        """Start periodic refresh loop."""
        self._stop_polling()
        if self.stream_active:
            self.refresh_ui()
            self._polling_job = self.after(config.POLL_INTERVAL_MS, self._start_polling)

    def _stop_polling(self):
        """Stop periodic refresh loop."""
        if self._polling_job:
            self.after_cancel(self._polling_job)
            self._polling_job = None
