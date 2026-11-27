import os
import math

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, Rectangle


class DOLSchematic:

    def __init__(
        self,
        configuration,
        motor_current=None,
        frequency=None,
        control_voltage=None,
        phase=3,
        coordination_type=None
    ):

        self.configuration = configuration

        # =====================================================
        # DESIGN INFORMATION
        # =====================================================

        self.manufacturer = self.clean_value(
            configuration.get("Manufacturer"),
            default="Not specified"
        )

        self.protection = self.clean_value(
            configuration.get("Protection_Model"),
            default="Protection"
        )

        self.contactor = self.clean_value(
            configuration.get("Contactor_Model"),
            default="Contactor"
        )

        self.overload = self.clean_value(
            configuration.get("Overload_Model"),
            default="Overload"
        )

        self.motor_power = self.clean_value(
            configuration.get("Motor_Power_kW"),
            default="?"
        )

        self.voltage = self.clean_value(
            configuration.get("Voltage_V"),
            default="?"
        )

        self.motor_current = self.clean_value(
            motor_current,
            configuration.get("Motor_Current_A"),
            default="?"
        )

        self.frequency = self.clean_value(
            frequency,
            configuration.get("Frequency_Hz"),
            default="50"
        )

        self.control_voltage = self.clean_value(
            control_voltage,
            configuration.get("Control_Voltage"),
            default="Not specified"
        )

        self.phase = self.clean_value(
            phase,
            configuration.get("Phase"),
            default="3"
        )

        self.coordination_type = self.clean_value(
            coordination_type,
            configuration.get("Coordination_Type"),
            default="Not specified"
        )

    # =========================================================
    # VALUE CLEANING
    # =========================================================

    @staticmethod
    def clean_value(
        primary=None,
        secondary=None,
        default="Not specified"
    ):

        for value in [primary, secondary]:

            if value is None:
                continue

            try:
                if isinstance(value, float) and math.isnan(value):
                    continue
            except TypeError:
                pass

            text = str(value).strip()

            if text == "":
                continue

            if text.lower() in {
                "nan",
                "none",
                "null"
            }:
                continue

            return text

        return default

    # =========================================================
    # BASIC DRAWING
    # =========================================================

    def wire(
        self,
        ax,
        x1,
        y1,
        x2,
        y2,
        lw=1.5
    ):

        ax.plot(
            [x1, x2],
            [y1, y2],
            color="black",
            linewidth=lw,
            solid_capstyle="butt"
        )

    def text(
        self,
        ax,
        x,
        y,
        value,
        size=8,
        weight="normal",
        ha="center",
        va="center"
    ):

        ax.text(
            x,
            y,
            str(value),
            fontsize=size,
            fontweight=weight,
            ha=ha,
            va=va,
            color="black"
        )

    def junction(
        self,
        ax,
        x,
        y
    ):

        ax.plot(
            x,
            y,
            marker="o",
            markersize=3.5,
            color="black"
        )

    # =========================================================
    # POWER DEVICE
    # =========================================================

    def draw_three_pole_device(
        self,
        ax,
        x,
        ys,
        tag,
        model,
        device_type
    ):

        # Device tag
        self.text(
            ax,
            x,
            max(ys) + 0.055,
            tag,
            size=9,
            weight="bold"
        )

        # Device body
        body_bottom = min(ys) - 0.025
        body_top = max(ys) + 0.025

        body = Rectangle(
            (
                x - 0.025,
                body_bottom
            ),
            0.050,
            body_top - body_bottom,
            fill=False,
            linewidth=0.9
        )

        ax.add_patch(body)

        # Three poles
        for y in ys:

            self.wire(
                ax,
                x - 0.075,
                y,
                x - 0.025,
                y
            )

            self.wire(
                ax,
                x + 0.025,
                y,
                x + 0.075,
                y
            )

            if device_type == "breaker":

                ax.plot(
                    [
                        x - 0.013,
                        x + 0.013
                    ],
                    [
                        y - 0.010,
                        y + 0.010
                    ],
                    color="black",
                    linewidth=1.5
                )

            elif device_type == "contactor":

                ax.plot(
                    [
                        x - 0.014,
                        x + 0.014
                    ],
                    [
                        y,
                        y
                    ],
                    color="black",
                    linewidth=1.6
                )

            elif device_type == "overload":

                ax.plot(
                    [
                        x - 0.013,
                        x + 0.013
                    ],
                    [
                        y - 0.009,
                        y + 0.009
                    ],
                    color="black",
                    linewidth=1.5
                )

        # Model label
        model_text = str(model)

        if len(model_text) > 28:

            first_line = model_text[:28]
            second_line = model_text[28:56]

            if len(model_text) > 56:
                second_line += "..."

            model_display = (
                first_line
                + "\n"
                + second_line
            )

            model_size = 5.2

        elif len(model_text) > 20:

            model_display = model_text
            model_size = 5.5

        else:

            model_display = model_text
            model_size = 6.0

        self.text(
            ax,
            x,
            body_bottom - 0.032,
            model_display,
            size=model_size
        )

    # =========================================================
    # MOTOR
    # =========================================================

    def draw_motor(
        self,
        ax,
        x,
        y
    ):

        radius = 0.065

        motor = Circle(
            (x, y),
            radius,
            fill=False,
            linewidth=1.7
        )

        ax.add_patch(motor)

        # Motor symbol
        self.text(
            ax,
            x,
            y + 0.010,
            "M",
            size=16,
            weight="bold"
        )

        self.text(
            ax,
            x,
            y - 0.019,
            "3~",
            size=7.5,
            weight="bold"
        )

        # Designation
        self.text(
            ax,
            x,
            y - 0.087,
            "M1",
            size=8.5,
            weight="bold"
        )

        self.text(
            ax,
            x,
            y - 0.108,
            f"{self.motor_power} kW",
            size=6.7
        )

        self.text(
            ax,
            x,
            y - 0.128,
            f"{self.motor_current} A",
            size=6.7
        )

    # =========================================================
    # EARTH
    # =========================================================

    def draw_earth(
        self,
        ax,
        x,
        y
    ):

        self.wire(
            ax,
            x,
            y + 0.025,
            x,
            y
        )

        ax.plot(
            [
                x - 0.022,
                x + 0.022
            ],
            [
                y,
                y
            ],
            color="black",
            linewidth=1.3
        )

        ax.plot(
            [
                x - 0.015,
                x + 0.015
            ],
            [
                y - 0.012,
                y - 0.012
            ],
            color="black",
            linewidth=1.3
        )

        ax.plot(
            [
                x - 0.008,
                x + 0.008
            ],
            [
                y - 0.024,
                y - 0.024
            ],
            color="black",
            linewidth=1.3
        )

        self.text(
            ax,
            x,
            y + 0.040,
            "PE",
            size=7,
            weight="bold"
        )

    # =========================================================
    # POWER CIRCUIT
    # =========================================================

    def draw_power_circuit(
        self,
        ax
    ):

        self.text(
            ax,
            0.50,
            0.865,
            "POWER CIRCUIT",
            size=12.5,
            weight="bold"
        )

        # -----------------------------------------------------
        # PHASE POSITIONS
        # -----------------------------------------------------

        ys = [
            0.720,
            0.625,
            0.530
        ]

        # -----------------------------------------------------
        # DEVICE POSITIONS
        # -----------------------------------------------------

        qf_x = 0.230
        km_x = 0.400
        fr_x = 0.570

        # Motor is further right
        motor_x = 0.825
        motor_y = 0.625

        motor_radius = 0.065

        # -----------------------------------------------------
        # PHASE LABELS
        # -----------------------------------------------------

        for label, y in zip(
            ["L1", "L2", "L3"],
            ys
        ):

            self.text(
                ax,
                0.065,
                y,
                label,
                size=8.5,
                weight="bold"
            )

            self.wire(
                ax,
                0.085,
                y,
                qf_x - 0.075,
                y
            )

        # -----------------------------------------------------
        # DEVICES
        # -----------------------------------------------------

        self.draw_three_pole_device(
            ax,
            qf_x,
            ys,
            "QF1",
            self.protection,
            "breaker"
        )

        self.draw_three_pole_device(
            ax,
            km_x,
            ys,
            "KM1",
            self.contactor,
            "contactor"
        )

        self.draw_three_pole_device(
            ax,
            fr_x,
            ys,
            "FR1",
            self.overload,
            "overload"
        )

        # -----------------------------------------------------
        # QF1 → KM1
        # -----------------------------------------------------

        for y in ys:

            self.wire(
                ax,
                qf_x + 0.075,
                y,
                km_x - 0.075,
                y
            )

        # -----------------------------------------------------
        # KM1 → FR1
        # -----------------------------------------------------

        for y in ys:

            self.wire(
                ax,
                km_x + 0.075,
                y,
                fr_x - 0.075,
                y
            )

        # -----------------------------------------------------
        # FR1 → MOTOR TERMINALS
        #
        # All three conductors remain horizontal.
        # -----------------------------------------------------

        terminal_x = motor_x - motor_radius

        terminal_positions = [
            motor_y + 0.040,
            motor_y,
            motor_y - 0.040
        ]

        terminal_labels = [
            "U1",
            "V1",
            "W1"
        ]

        for y_source, y_target, terminal in zip(
            ys,
            terminal_positions,
            terminal_labels
        ):

            # First horizontal section
            self.wire(
                ax,
                fr_x + 0.075,
                y_source,
                terminal_x - 0.030,
                y_source
            )

            # Short vertical transition only when required
            if abs(y_source - y_target) > 0.001:

                self.wire(
                    ax,
                    terminal_x - 0.030,
                    y_source,
                    terminal_x - 0.030,
                    y_target
                )

            # Final horizontal section into motor
            self.wire(
                ax,
                terminal_x - 0.030,
                y_target,
                terminal_x,
                y_target
            )

            self.text(
                ax,
                terminal_x - 0.040,
                y_target + 0.016,
                terminal,
                size=6.3,
                ha="right"
            )

        # -----------------------------------------------------
        # MOTOR
        # -----------------------------------------------------

        self.draw_motor(
            ax,
            motor_x,
            motor_y
        )

        # -----------------------------------------------------
        # PE
        # -----------------------------------------------------

        self.draw_earth(
            ax,
            motor_x + 0.105,
            motor_y - 0.075
        )

        # -----------------------------------------------------
        # SUPPLY INFORMATION
        # -----------------------------------------------------

        self.text(
            ax,
            0.50,
            0.435,
            (
                f"SUPPLY: {self.voltage} V  |  "
                f"{self.phase}~  |  "
                f"{self.frequency} Hz"
            ),
            size=7
        )

    # =========================================================
    # NC CONTACT
    # =========================================================

    def draw_nc_contact(
        self,
        ax,
        x,
        y,
        label,
        terminals
    ):

        self.wire(
            ax,
            x - 0.060,
            y,
            x - 0.018,
            y
        )

        self.wire(
            ax,
            x + 0.018,
            y,
            x + 0.060,
            y
        )

        ax.plot(
            [
                x - 0.018,
                x + 0.018
            ],
            [
                y + 0.018,
                y - 0.018
            ],
            color="black",
            linewidth=1.5
        )

        self.text(
            ax,
            x,
            y + 0.045,
            label,
            size=6.8,
            weight="bold"
        )

        self.text(
            ax,
            x - 0.028,
            y - 0.035,
            terminals[0],
            size=5.7
        )

        self.text(
            ax,
            x + 0.028,
            y - 0.035,
            terminals[1],
            size=5.7
        )

    # =========================================================
    # NO CONTACT
    # =========================================================

    def draw_no_contact(
        self,
        ax,
        x,
        y,
        label,
        terminals=None
    ):

        self.wire(
            ax,
            x - 0.060,
            y,
            x - 0.018,
            y
        )

        self.wire(
            ax,
            x + 0.018,
            y,
            x + 0.060,
            y
        )

        ax.plot(
            [
                x - 0.018,
                x - 0.018
            ],
            [
                y - 0.020,
                y + 0.020
            ],
            color="black",
            linewidth=1.5
        )

        ax.plot(
            [
                x + 0.018,
                x + 0.018
            ],
            [
                y - 0.020,
                y + 0.020
            ],
            color="black",
            linewidth=1.5
        )

        self.text(
            ax,
            x,
            y + 0.045,
            label,
            size=6.8,
            weight="bold"
        )

        if terminals:

            self.text(
                ax,
                x - 0.028,
                y - 0.035,
                terminals[0],
                size=5.7
            )

            self.text(
                ax,
                x + 0.028,
                y - 0.035,
                terminals[1],
                size=5.7
            )

    # =========================================================
    # CONTACTOR COIL
    # =========================================================

    def draw_coil(
        self,
        ax,
        x,
        y
    ):

        self.wire(
            ax,
            x - 0.070,
            y,
            x - 0.030,
            y
        )

        self.wire(
            ax,
            x + 0.030,
            y,
            x + 0.070,
            y
        )

        arc1 = Arc(
            (
                x - 0.015,
                y
            ),
            0.040,
            0.060,
            theta1=-90,
            theta2=90,
            linewidth=1.5
        )

        arc2 = Arc(
            (
                x + 0.015,
                y
            ),
            0.040,
            0.060,
            theta1=90,
            theta2=270,
            linewidth=1.5
        )

        ax.add_patch(arc1)
        ax.add_patch(arc2)

        self.text(
            ax,
            x,
            y + 0.045,
            "KM1",
            size=7.5,
            weight="bold"
        )

        self.text(
            ax,
            x - 0.040,
            y - 0.035,
            "A1",
            size=5.7
        )

        self.text(
            ax,
            x + 0.040,
            y - 0.035,
            "A2",
            size=5.7
        )

    # =========================================================
    # CONTROL CIRCUIT
    # =========================================================

    def draw_control_circuit(
        self,
        ax
    ):

        self.text(
            ax,
            0.50,
            0.365,
            "CONTROL CIRCUIT",
            size=12.5,
            weight="bold"
        )

        # -----------------------------------------------------
        # CONTROL RAILS
        # -----------------------------------------------------

        left_rail = 0.095
        right_rail = 0.905

        main_y = 0.235

        # Left rail
        self.wire(
            ax,
            left_rail,
            0.300,
            left_rail,
            0.150,
            lw=1.8
        )

        # Right rail
        self.wire(
            ax,
            right_rail,
            0.300,
            right_rail,
            0.150,
            lw=1.8
        )

        self.text(
            ax,
            left_rail,
            0.320,
            "L",
            size=9,
            weight="bold"
        )

        self.text(
            ax,
            right_rail,
            0.320,
            "N",
            size=9,
            weight="bold"
        )

        # -----------------------------------------------------
        # L → STOP
        # -----------------------------------------------------

        self.wire(
            ax,
            left_rail,
            main_y,
            0.165,
            main_y
        )

        self.draw_nc_contact(
            ax,
            0.210,
            main_y,
            "S0 STOP",
            ("11", "12")
        )

        # -----------------------------------------------------
        # STOP → OVERLOAD
        # -----------------------------------------------------

        self.wire(
            ax,
            0.270,
            main_y,
            0.335,
            main_y
        )

        self.draw_nc_contact(
            ax,
            0.380,
            main_y,
            "FR1",
            ("95", "96")
        )

        # -----------------------------------------------------
        # PARALLEL START / SEAL-IN BRANCH
        # -----------------------------------------------------

        branch_left = 0.445
        branch_right = 0.660

        branch_top = 0.285
        branch_bottom = 0.185

        # Main line into branch
        self.wire(
            ax,
            0.440,
            main_y,
            branch_left,
            main_y
        )

        # Left branch
        self.wire(
            ax,
            branch_left,
            branch_top,
            branch_left,
            branch_bottom
        )

        # Right branch
        self.wire(
            ax,
            branch_right,
            branch_top,
            branch_right,
            branch_bottom
        )

        # Top branch
        self.wire(
            ax,
            branch_left,
            branch_top,
            0.495,
            branch_top
        )

        self.draw_no_contact(
            ax,
            0.555,
            branch_top,
            "S1 START",
            ("3", "4")
        )

        self.wire(
            ax,
            0.615,
            branch_top,
            branch_right,
            branch_top
        )

        # Bottom branch
        self.wire(
            ax,
            branch_left,
            branch_bottom,
            0.495,
            branch_bottom
        )

        self.draw_no_contact(
            ax,
            0.555,
            branch_bottom,
            "KM1",
            ("13", "14")
        )

        self.wire(
            ax,
            0.615,
            branch_bottom,
            branch_right,
            branch_bottom
        )

        # Junctions
        self.junction(
            ax,
            branch_left,
            main_y
        )

        self.junction(
            ax,
            branch_right,
            main_y
        )

        # -----------------------------------------------------
        # BRANCH → COIL
        # -----------------------------------------------------

        self.wire(
            ax,
            branch_right,
            main_y,
            0.730,
            main_y
        )

        self.draw_coil(
            ax,
            0.800,
            main_y
        )

        self.wire(
            ax,
            0.870,
            main_y,
            right_rail,
            main_y
        )

        # -----------------------------------------------------
        # CONTROL SUPPLY
        # -----------------------------------------------------

        self.text(
            ax,
            0.50,
            0.135,
            (
                f"CONTROL SUPPLY: "
                f"{self.control_voltage} V AC"
            ),
            size=6.8
        )

    # =========================================================
    # TITLE BLOCK
    # =========================================================

    def draw_title_block(
        self,
        ax
    ):

        left = 0.055
        bottom = 0.035

        width = 0.890
        height = 0.065

        # Outer box
        outer = Rectangle(
            (
                left,
                bottom
            ),
            width,
            height,
            fill=False,
            linewidth=1.1
        )

        ax.add_patch(outer)

        middle_y = bottom + 0.0325

        # Horizontal separator
        ax.plot(
            [
                left,
                left + width
            ],
            [
                middle_y,
                middle_y
            ],
            color="black",
            linewidth=0.7
        )

        # Top row
        top_divisions = [
            0.205,
            0.350,
            0.500,
            0.650,
            0.800
        ]

        for x in top_divisions:

            ax.plot(
                [
                    x,
                    x
                ],
                [
                    middle_y,
                    bottom + height
                ],
                color="black",
                linewidth=0.7
            )

        # Bottom row
        bottom_divisions = [
            0.240,
            0.435,
            0.625,
            0.785
        ]

        for x in bottom_divisions:

            ax.plot(
                [
                    x,
                    x
                ],
                [
                    bottom,
                    middle_y
                ],
                color="black",
                linewidth=0.7
            )

        # -----------------------------------------------------
        # TOP ROW
        # -----------------------------------------------------

        self.text(
            ax,
            0.130,
            bottom + 0.048,
            "INTELLIPANEL",
            size=7.0,
            weight="bold"
        )

        self.text(
            ax,
            0.277,
            bottom + 0.048,
            "DOL STARTER",
            size=6.0
        )

        self.text(
            ax,
            0.425,
            bottom + 0.048,
            f"MOTOR {self.motor_power} kW",
            size=5.8
        )

        self.text(
            ax,
            0.575,
            bottom + 0.048,
            f"{self.voltage} V / {self.phase}~",
            size=5.8
        )

        self.text(
            ax,
            0.725,
            bottom + 0.048,
            f"{self.frequency} Hz",
            size=5.8
        )

        manufacturer_text = self.manufacturer

        if len(manufacturer_text) > 20:
            manufacturer_text = (
                manufacturer_text[:20]
                + "..."
            )

        self.text(
            ax,
            0.885,
            bottom + 0.048,
            manufacturer_text,
            size=5.2
        )

        # -----------------------------------------------------
        # BOTTOM ROW
        # -----------------------------------------------------

        self.text(
            ax,
            0.147,
            bottom + 0.016,
            f"CURRENT {self.motor_current} A",
            size=5.5
        )

        self.text(
            ax,
            0.337,
            bottom + 0.016,
            f"CONTROL {self.control_voltage} V",
            size=5.4
        )

        self.text(
            ax,
            0.530,
            bottom + 0.016,
            f"COORD. {self.coordination_type}",
            size=5.3
        )

        self.text(
            ax,
            0.705,
            bottom + 0.016,
            "DRAWING IP-DOL-001",
            size=5.3
        )

        self.text(
            ax,
            0.865,
            bottom + 0.016,
            "REV 01 | SHEET 1/1",
            size=5.3
        )

    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate(
        self
    ):

        os.makedirs(
            "output",
            exist_ok=True
        )

        fig, ax = plt.subplots(
            figsize=(16, 10)
        )

        ax.set_xlim(
            0,
            1
        )

        ax.set_ylim(
            0,
            1
        )

        ax.set_aspect(
            "equal"
        )

        ax.axis("off")

        # =====================================================
        # DRAWING BORDER
        # =====================================================

        border = Rectangle(
            (
                0.025,
                0.020
            ),
            0.950,
            0.940,
            fill=False,
            linewidth=1.2
        )

        ax.add_patch(border)

        # =====================================================
        # MAIN TITLE
        # =====================================================

        self.text(
            ax,
            0.50,
            0.925,
            "DIRECT-ON-LINE MOTOR STARTER",
            size=15,
            weight="bold"
        )

        self.text(
            ax,
            0.50,
            0.900,
            "DOL POWER & CONTROL SCHEMATIC",
            size=8.5
        )

        # =====================================================
        # CIRCUITS
        # =====================================================

        self.draw_power_circuit(
            ax
        )

        self.draw_control_circuit(
            ax
        )

        # =====================================================
        # TITLE BLOCK
        # =====================================================

        self.draw_title_block(
            ax
        )

        # =====================================================
        # SAVE
        # =====================================================

        output_path = (
            "output/intellipanel_dol_schematic.png"
        )

        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white"
        )

        plt.close(fig)

        print(
            "\nElectrical schematic saved to:"
        )

        print(
            output_path
        )

        return output_path