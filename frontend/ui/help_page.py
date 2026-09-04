"""
Help & Documentation Page for the Sign Language Translator GUI.
Provides step-by-step user instructions, sensor glove architecture explanation,
system status indicator reference, and troubleshooting guidance.
"""

import customtkinter as ctk
import frontend.ui.styles as styles
from frontend.ui.components import Card, StatusBadge


class HelpPage(ctk.CTkFrame):
    """
    Page 7: User Help, Operating Guide, and System Reference.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._build_header()
        self._build_content()

    def _build_header(self):
        """Render page title and subtitle."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, styles.PAD_MD))

        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Help & User Instructions",
            font=styles.FONT_TITLE,
            text_color=styles.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Step-by-step operation guide, sensor glove architecture, and system troubleshooting.",
            font=styles.FONT_SUBTITLE,
            text_color=styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def _build_content(self):
        """Construct scrollable guide sections."""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # ==========================================
        # SECTION 1: 8-Step Quick Start Workflow
        # ==========================================
        card_steps = Card(scroll)
        card_steps.pack(fill="x", pady=(0, styles.PAD_MD))

        h1 = ctk.CTkFrame(card_steps, fg_color="transparent")
        h1.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_s_title = ctk.CTkLabel(h1, text="QUICK START WORKFLOW (8 STEPS)", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_s_title.pack(side="left")

        steps_container = ctk.CTkFrame(card_steps, fg_color="transparent")
        steps_container.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        workflow_steps = [
            ("1", "Connect Sensor Glove", "Open the Glove Status page and click [ Connect Glove ] to initiate telemetry."),
            ("2", "Confirm System Readiness", "Verify that the top header displays 'Glove: Connected' and battery level is adequate."),
            ("3", "Open Translation Studio", "Navigate to the Translation tab via the sidebar navigation menu."),
            ("4", "Start Gesture Detection", "Press [ Start Detection ] to activate real-time telemetry streaming."),
            ("5", "Perform Sign Gestures", "Articulate signs naturally using the sensor-equipped glove."),
            ("6", "Review Recognition Result", "Observe the recognized sign symbol, translation, and confidence percentage."),
            ("7", "Assemble Sentences", "Allow signs to accumulate in the Word Builder or manually edit spaces and punctuation."),
            ("8", "Audible Speech Output", "Press [ Speak ] or enable 'Auto-Speak Signs' in the studio or Settings."),
        ]

        for num, title, desc in workflow_steps:
            row = ctk.CTkFrame(steps_container, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_BUTTON)
            row.pack(fill="x", pady=3)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=8)

            badge = ctk.CTkLabel(
                inner,
                text=f" Step {num} ",
                font=styles.FONT_BADGE,
                fg_color=styles.COLOR_ACCENT_BG,
                text_color=styles.COLOR_STATUS_READY,
                corner_radius=4
            )
            badge.pack(side="left", padx=(0, 10))

            lbl_step_title = ctk.CTkLabel(inner, text=title, font=styles.FONT_BODY_BOLD, text_color=styles.COLOR_TEXT_PRIMARY)
            lbl_step_title.pack(side="left", padx=(0, 10))

            lbl_step_desc = ctk.CTkLabel(inner, text=desc, font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_MUTED, anchor="w")
            lbl_step_desc.pack(side="left", fill="x", expand=True)

        # ==========================================
        # SECTION 2: Why a Sensor Glove? (Hardware vs Camera)
        # ==========================================
        card_arch = Card(scroll)
        card_arch.pack(fill="x", pady=(0, styles.PAD_MD))

        h2 = ctk.CTkFrame(card_arch, fg_color="transparent")
        h2.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_a_title = ctk.CTkLabel(h2, text="HARDWARE ARCHITECTURE: SENSOR GLOVE VS. CAMERA", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_a_title.pack(side="left")

        body_arch = ctk.CTkFrame(card_arch, fg_color="transparent")
        body_arch.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        lbl_arch_text = ctk.CTkLabel(
            body_arch,
            text=(
                "Important System Distinction:\n"
                "This translation system is NOT camera-based. Traditional computer-vision approaches suffer from "
                "visual occlusion, poor lighting, background clutter, and privacy limitations.\n\n"
                "Instead, our system collects tactile movement and finger flexion directly from a sensor-equipped glove:\n"
                "• Finger bend sensors record precise joint articulation angles directly from the hand.\n"
                "• Onboard microcontrollers sample and transmit data packets at high frequency.\n"
                "• Machine learning models classify gestures based on real sensor vectors rather than pixels.\n"
                "• The Frontend GUI receives, visualizes, and communicates the resulting translation seamlessly."
            ),
            font=styles.FONT_BODY,
            text_color=styles.COLOR_TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        lbl_arch_text.pack(fill="x")

        # ==========================================
        # SECTION 3: System Status Indicator Cheat Sheet
        # ==========================================
        card_status = Card(scroll)
        card_status.pack(fill="x", pady=(0, styles.PAD_MD))

        h3 = ctk.CTkFrame(card_status, fg_color="transparent")
        h3.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_st_title = ctk.CTkLabel(h3, text="SYSTEM STATUS REFERENCE GUIDE", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_st_title.pack(side="left")

        grid_status = ctk.CTkFrame(card_status, fg_color="transparent")
        grid_status.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        status_defs = [
            ("ready", "Status: Ready", "Glove is paired and idle; system is ready for detection."),
            ("detecting", "Status: Detecting...", "Stream active; model is evaluating incoming sensor movements."),
            ("processing", "Status: Processing...", "Gesture trajectory recognized; model resolving prediction."),
            ("connected", "Glove: Connected", "Hardware link established and telemetry packets receiving."),
            ("disconnected", "Glove: Disconnected", "No hardware communication detected; check pairing."),
        ]

        for stype, stext, sdesc in status_defs:
            row_st = ctk.CTkFrame(grid_status, fg_color="transparent")
            row_st.pack(fill="x", pady=4)

            badge = StatusBadge(row_st, status_type=stype, text=stext)
            badge.pack(side="left", padx=(0, 14))

            lbl_d = ctk.CTkLabel(row_st, text=sdesc, font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_MUTED, anchor="w")
            lbl_d.pack(side="left", fill="x", expand=True)

        # ==========================================
        # SECTION 4: Troubleshooting FAQ
        # ==========================================
        card_faq = Card(scroll)
        card_faq.pack(fill="x", pady=(0, styles.PAD_XL))

        h4 = ctk.CTkFrame(card_faq, fg_color="transparent")
        h4.pack(fill="x", padx=styles.PAD_LG, pady=(styles.PAD_MD, styles.PAD_SM))

        lbl_f_title = ctk.CTkLabel(h4, text="FREQUENTLY ASKED QUESTIONS (FAQ)", font=styles.FONT_CARD_TITLE, text_color=styles.COLOR_TEXT_SECONDARY)
        lbl_f_title.pack(side="left")

        faq_box = ctk.CTkFrame(card_faq, fg_color="transparent")
        faq_box.pack(fill="x", padx=styles.PAD_LG, pady=(0, styles.PAD_MD))

        faqs = [
            ("Q: How do I calibrate the glove sensors if readings seem off?",
             "A: Navigate to the Sensors tab and click [ Calibrate Baseline ]. Keep your hand relaxed in a flat resting position during calibration."),
            ("Q: Why is speech output not playing?",
             "A: Check the Settings tab to confirm 'Enable Audio Speech Output' is toggled ON, and test audio playback using the [ Test Voice Output ] button."),
            ("Q: How can I save or export my translated sentences?",
             "A: In the Translation Studio, click [ Save ] to record translations into History. Open the History tab to search records or click [ Copy Log ] to export a text transcript."),
        ]

        for q, a in faqs:
            fq_row = ctk.CTkFrame(faq_box, fg_color=styles.COLOR_BG_SUBTLE, corner_radius=styles.RADIUS_BUTTON)
            fq_row.pack(fill="x", pady=4)

            inner_fq = ctk.CTkFrame(fq_row, fg_color="transparent")
            inner_fq.pack(fill="x", padx=12, pady=10)

            ctk.CTkLabel(inner_fq, text=q, font=styles.FONT_BODY_BOLD, text_color=styles.COLOR_TEXT_PRIMARY, anchor="w").pack(anchor="w")
            ctk.CTkLabel(inner_fq, text=a, font=styles.FONT_BODY, text_color=styles.COLOR_TEXT_MUTED, anchor="w", wraplength=700).pack(anchor="w", pady=(2, 0))
