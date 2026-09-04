"""
Glove Status & Pairing Page for the Sign Language Translator GUI.
Provides connection controls, battery telemetry, hardware diagnostics,
and a procedural vector glove graphic without external image dependencies.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any

import frontend.config as config
import frontend.ui.styles as styles
from frontend.ui.components import Card, StatusBadge, ActionButton
from frontend.services.api_client import api_client


class GloveCanvasWidget(ctk.CTkFrame):
    """
    Procedural vector graphic representing the sensor glove.
    Draws a responsive dark-themed hand silhouette with articulated joints,
    circuit traces, and dynamic connection states.
    """

    def __init__(self, master, width: int = 320, height: int = 360, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            width=width,
            height=height,
            **kwargs
        )
        self.canvas_width = width
        self.canvas_height = height
        self.pack_propagate(False)

        # Embedded Tkinter Canvas with dark background
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=styles.COLOR_BG_CARD,
            highlightthickness=1,
            highlightbackground=styles.COLOR_BORDER,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self._connected = False
        self.draw_glove(connected=False)

    def draw_glove(self, connected: bool):
        """Redraw the vector glove reflecting current connection status."""
        self._connected = connected
        self.canvas.delete("all")

        # Color scheme based on state
        if connected:
            color_trace = "#1f4b7a"
            color_wire = "#2f81f7"
            color_joint = "#3fb950"
            color_hub = "#58a6ff"
            color_hub_bg = "#13233a"
            status_text = "● TELEMETRY ACTIVE (SIMULATED)"
            status_color = styles.COLOR_STATUS_CONNECTED
        else:
            color_trace = "#161b22"
            color_wire = "#30363d"
            color_joint = "#21262d"
            color_hub = "#30363d"
            color_hub_bg = "#161b22"
            status_text = "⏻ GLOVE OFFLINE"
            status_color = styles.COLOR_TEXT_MUTED

        # --- 1. Background Grid Subtle Matrix ---
        grid_step = 30
        for x in range(0, self.canvas_width, grid_step):
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="#12161d", width=1)
        for y in range(0, self.canvas_height, grid_step):
            self.canvas.create_line(0, y, self.canvas_width, y, fill="#12161d", width=1)

        # --- 2. Palm & Hand Silhouette (Polygon) ---
        palm_points = [
            (105, 305),  # Wrist left
            (85, 240),   # Thumb base side
            (65, 210),   # Thumb joint 1
            (48, 175),   # Thumb joint 2
            (38, 150),   # Thumb tip
            (56, 142),   # Thumb inner tip
            (78, 180),   # Thumb web
            (95, 170),   # Index base
            (96, 115),   # Index joint
            (98, 70),    # Index tip
            (114, 70),
            (115, 115),
            (122, 160),  # Web Index-Middle
            (138, 155),  # Middle base
            (140, 100),  # Middle joint
            (142, 50),   # Middle tip
            (158, 50),
            (160, 100),
            (165, 158),  # Web Middle-Ring
            (180, 165),  # Ring base
            (182, 115),  # Ring joint
            (184, 75),   # Ring tip
            (198, 77),
            (198, 120),
            (204, 180),  # Web Ring-Little
            (218, 190),  # Little base
            (225, 150),  # Little joint
            (230, 115),  # Little tip
            (242, 120),
            (236, 160),
            (226, 215),  # Little base outer
            (215, 260),  # Palm outer edge
            (205, 305),  # Wrist right
        ]
        self.canvas.create_polygon(
            palm_points,
            fill="#0d1219",
            outline=color_wire,
            width=2,
            smooth=True
        )

        # --- 3. Microcontroller / Sensor Hub on Wrist/Palm ---
        hub_x, hub_y = 150, 245
        self.canvas.create_rectangle(
            hub_x - 30, hub_y - 20, hub_x + 30, hub_y + 20,
            fill=color_hub_bg,
            outline=color_hub,
            width=2
        )
        self.canvas.create_text(
            hub_x, hub_y,
            text="MCU HUB",
            fill=color_hub,
            font=("Segoe UI", 9, "bold")
        )

        # --- 4. Articulated Joint Nodes & Sensor Channels ---
        # Generic channel nodes on fingers
        sensor_nodes = [
            (48, 150, "C1"),   # Thumb
            (106, 75, "C2"),   # Index
            (150, 55, "C3"),   # Middle
            (191, 80, "C4"),   # Ring
            (236, 120, "C5"),  # Little
        ]

        # Draw circuit traces from MCU Hub to each sensor node
        for (nx, ny, ch_id) in sensor_nodes:
            self.canvas.create_line(
                hub_x, hub_y, nx, ny,
                fill=color_trace,
                width=2,
                dash=(4, 2) if connected else None
            )

            # Outer node halo
            if connected:
                self.canvas.create_oval(
                    nx - 10, ny - 10, nx + 10, ny + 10,
                    outline="#1f4b7a",
                    width=1
                )

            # Center sensor node circle
            self.canvas.create_oval(
                nx - 6, ny - 6, nx + 6, ny + 6,
                fill=color_joint,
                outline=color_wire,
                width=1.5
            )

        # --- 5. Wrist Connector Cuff ---
        self.canvas.create_rectangle(
            110, 310, 200, 332,
            fill="#161b22",
            outline=color_wire,
            width=1.5
        )
        self.canvas.create_text(
            155, 321,
            text="BUS INTERFACE",
            fill=styles.COLOR_TEXT_MUTED,
            font=("Segoe UI", 8)
        )

        # --- 6. In-Canvas Status Legend ---
        self.canvas.create_text(
            self.canvas_width // 2, 25,
            text=status_text,
            fill=status_color,
            font=("Segoe UI", 10, "bold")
        )


class GlovePage(ctk.CTkFrame):
    """
    Page 2: Glove Status & Pairing Management.
    Displays device connectivity, hardware diagnostics, battery health,
    and responsive pairing controls.
    """

    def __init__(self, master, on_status_change: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_status_change = on_status_change

        self._build_header()
        self._build_body()
        self.refresh_ui()

    def _build_header(self):
        """Render top section title and subtitle."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Glove Status & Pairing",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Manage hardware pairing, battery diagnostics, and telemetry link (Simulated).",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def _build_body(self):
        """Construct the 2-column layout (Vector illustration on left, pairing & diagnostics on right)."""
        body_grid = ctk.CTkFrame(self, fg_color="transparent")
        body_grid.pack(fill="both", expand=True)
        body_grid.grid_columnconfigure(0, weight=4, uniform="glove_cols")
        body_grid.grid_columnconfigure(1, weight=5, uniform="glove_cols")
        body_grid.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT COLUMN: Device Vector Visualization
        # ==========================================
        left_card = Card(body_grid)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Card Title
        lbl_vis_title = ctk.CTkLabel(
            left_card,
            text="DEVICE VISUALIZATION",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_vis_title.pack(anchor="w", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        # Vector Glove Canvas
        self.glove_canvas = GloveCanvasWidget(left_card, width=320, height=340)
        self.glove_canvas.pack(padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        # Battery Bar Container
        battery_frame = ctk.CTkFrame(left_card, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_BUTTON)
        battery_frame.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        batt_inner = ctk.CTkFrame(battery_frame, fg_color="transparent")
        batt_inner.pack(fill="x", padx=12, pady=10)

        batt_label_row = ctk.CTkFrame(batt_inner, fg_color="transparent")
        batt_label_row.pack(fill="x", pady=(0, 6))

        self.lbl_batt_title = ctk.CTkLabel(
            batt_label_row,
            text="BATTERY LEVEL",
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_batt_title.pack(side="left")

        self.lbl_batt_val = ctk.CTkLabel(
            batt_label_row,
            text="87%",
            font=styles.FONT_BODY_BOLD,
            text_color=styles.COLOR_STATUS_CONNECTED,
            anchor="e"
        )
        self.lbl_batt_val.pack(side="right")

        self.progress_batt = ctk.CTkProgressBar(batt_inner, height=10, corner_radius=5)
        self.progress_batt.pack(fill="x")
        self.progress_batt.set(0.87)

        # ==========================================
        # RIGHT COLUMN: Connection & Diagnostics
        # ==========================================
        right_container = ctk.CTkFrame(body_grid, fg_color="transparent")
        right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- Sub-Card 1: Connection & Pairing ---
        pairing_card = Card(right_container)
        pairing_card.pack(fill="x", pady=(0, styles.PAD_MD))

        # Header Row inside Pairing Card
        p_header = ctk.CTkFrame(pairing_card, fg_color="transparent")
        p_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_p_title = ctk.CTkLabel(
            p_header,
            text="PAIRING & CONNECTION",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_p_title.pack(side="left")

        self.badge_glove_status = StatusBadge(p_header, status_type="connected", text="Connected")
        self.badge_glove_status.pack(side="right")

        # Device Selection Row
        dev_row = ctk.CTkFrame(pairing_card, fg_color="transparent")
        dev_row.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))

        lbl_dev_select = ctk.CTkLabel(
            dev_row,
            text="Select Hardware Device:",
            font=styles.FONT_BODY,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_dev_select.pack(anchor="w", pady=(0, 4))

        self.device_combo = ctk.CTkOptionMenu(
            dev_row,
            values=["Glove-01 (Simulated)", "Glove-02 (Virtual)"],
            font=styles.FONT_BODY,
            fg_color=styles.COLOR_BG_SUBTLE,
            button_color=styles.COLOR_BTN_SECONDARY_HOVER,
            text_color=styles.COLOR_TEXT_PRIMARY,
            height=36,
            corner_radius=styles.RADIUS_BUTTON
        )
        self.device_combo.pack(fill="x")

        # Action Buttons Row
        btn_row = ctk.CTkFrame(pairing_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=styles.PAD_LG, pady=styles.PAD_SM)
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)
        btn_row.grid_columnconfigure(2, weight=1)

        self.btn_connect = ActionButton(
            btn_row,
            text="Connect Glove",
            command=self._handle_connect,
            variant="success"
        )
        self.btn_connect.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_disconnect = ActionButton(
            btn_row,
            text="Disconnect",
            command=self._handle_disconnect,
            variant="danger"
        )
        self.btn_disconnect.grid(row=0, column=1, padx=4, sticky="ew")

        self.btn_scan = ActionButton(
            btn_row,
            text="Scan Devices",
            command=self._handle_scan,
            variant="secondary"
        )
        self.btn_scan.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # Auto-Connect Toggle Switch
        pref_row = ctk.CTkFrame(pairing_card, fg_color="transparent")
        pref_row.pack(fill="x", padx=styles.PAD_LG, pady=(4, styles.PAD_MD))

        self.switch_autoconnect = ctk.CTkSwitch(
            pref_row,
            text="Auto-connect to default glove on application startup",
            font=styles.FONT_BODY,
            text_color=styles.COLOR_TEXT_SECONDARY,
            progress_color=styles.COLOR_ACCENT_PRIMARY
        )
        self.switch_autoconnect.pack(anchor="w")
        if config.AUTO_CONNECT:
            self.switch_autoconnect.select()

        # --- Sub-Card 2: Hardware Diagnostics & Telemetry ---
        diag_card = Card(right_container)
        diag_card.pack(fill="x")

        diag_header = ctk.CTkFrame(diag_card, fg_color="transparent")
        diag_header.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_diag_title = ctk.CTkLabel(
            diag_header,
            text="TELEMETRY & PROTOCOL (SIMULATED)",
            font=styles.FONT_CARD_TITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_diag_title.pack(side="left")

        # Telemetry metrics table
        table_frame = ctk.CTkFrame(diag_card, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_BUTTON)
        table_frame.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_SM))

        self.metrics_data = [
            ("Hardware Device ID", "Glove-01 (Simulated)"),
            ("Communication Port", "Virtual COM3 (Simulated)"),
            ("Transmission Frequency", "50 Hz (Simulated)"),
            ("Latency Estimate", "< 10 ms (Simulated)"),
            ("Protocol Spec", "Awaiting teammate confirmation"),
            ("Packet Integrity", "100% (Simulated)"),
        ]

        self.metric_labels: Dict[str, ctk.CTkLabel] = {}
        for idx, (lbl_key, lbl_val) in enumerate(self.metrics_data):
            row_f = ctk.CTkFrame(table_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=12, pady=5)

            k_lbl = ctk.CTkLabel(
                row_f,
                text=lbl_key,
                font=styles.FONT_BODY,
                text_color=styles.COLOR_TEXT_MUTED,
                anchor="w"
            )
            k_lbl.pack(side="left")

            v_lbl = ctk.CTkLabel(
                row_f,
                text=lbl_val,
                font=styles.FONT_BODY_BOLD,
                text_color=styles.COLOR_TEXT_PRIMARY,
                anchor="e"
            )
            v_lbl.pack(side="right")
            self.metric_labels[lbl_key] = v_lbl

        # Disclaimer Notice Box
        notice_box = ctk.CTkFrame(diag_card, fg_color="transparent")
        notice_box.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_SM, styles.PAD_MD))

        lbl_notice = ctk.CTkLabel(
            notice_box,
            text=(
                "ⓘ Hardware-Agnostic Note: Actual sensor arrays, microcontrollers, and communication "
                "protocols will be connected to this interface once finalized by the hardware teammate."
            ),
            font=styles.FONT_SMALL,
            text_color=styles.COLOR_TEXT_MUTED,
            justify="left",
            wraplength=460,
            anchor="w"
        )
        lbl_notice.pack(fill="x")

    def refresh_ui(self):
        """Update all visual indicators based on the current ApiClient state."""
        glove_info = api_client.get_glove_status()
        is_connected = glove_info["connected"]
        battery = glove_info["battery"]

        # Update vector glove canvas
        self.glove_canvas.draw_glove(connected=is_connected)

        # Update status badge
        self.badge_glove_status.set_status(
            "connected" if is_connected else "disconnected",
            "Connected" if is_connected else "Disconnected"
        )

        # Update battery UI
        if is_connected:
            self.lbl_batt_val.configure(
                text=f"{battery}%",
                text_color=styles.COLOR_STATUS_CONNECTED if battery > 20 else styles.COLOR_DANGER
            )
            self.progress_batt.set(max(0.0, min(1.0, battery / 100.0)))
            self.progress_batt.configure(
                progress_color=styles.COLOR_STATUS_CONNECTED if battery > 20 else styles.COLOR_DANGER
            )
        else:
            self.lbl_batt_val.configure(text="Offline", text_color=styles.COLOR_TEXT_MUTED)
            self.progress_batt.set(0.0)
            self.progress_batt.configure(progress_color=styles.COLOR_BORDER)

        # Update buttons enabled/disabled states
        if is_connected:
            self.btn_connect.configure(state="disabled")
            self.btn_disconnect.configure(state="normal")
        else:
            self.btn_connect.configure(state="normal")
            self.btn_disconnect.configure(state="disabled")

        # Update metrics table
        if is_connected:
            self.metric_labels["Communication Port"].configure(text="Virtual COM3 (Simulated)")
            self.metric_labels["Transmission Frequency"].configure(text="50 Hz (Simulated)")
            self.metric_labels["Latency Estimate"].configure(text="< 10 ms (Simulated)")
            self.metric_labels["Packet Integrity"].configure(text="100% (Simulated)")
        else:
            self.metric_labels["Communication Port"].configure(text="Disconnected")
            self.metric_labels["Transmission Frequency"].configure(text="0 Hz")
            self.metric_labels["Latency Estimate"].configure(text="—")
            self.metric_labels["Packet Integrity"].configure(text="0%")

    def _handle_connect(self):
        """Trigger glove connection via ApiClient."""
        selected_dev = self.device_combo.get().split(" ")[0]
        api_client.connect_glove(selected_dev)
        self.refresh_ui()
        if self.on_status_change:
            self.on_status_change()

    def _handle_disconnect(self):
        """Trigger glove disconnection via ApiClient."""
        api_client.disconnect_glove()
        self.refresh_ui()
        if self.on_status_change:
            self.on_status_change()

    def _handle_scan(self):
        """Simulate scanning for available hardware devices."""
        self.btn_scan.configure(text="Scanning...", state="disabled")

        def _finish_scan():
            self.device_combo.configure(values=["Glove-01 (Simulated)", "Glove-02 (Virtual)"])
            self.btn_scan.configure(text="Scan Devices", state="normal")

        self.after(600, _finish_scan)
