from engineering import calculate_motor_current
from ml_model import DOLRecommendationModel
from circuit_generator import DOLCircuitGenerator
from bom_generator import BOMGenerator
from circuit_drawing import DOLSchematic


def main():

    print("\n================================")
    print("        INTELLIPANEL")
    print("     DOL CIRCUIT DESIGNER")
    print("================================")

    # =========================================================
    # MOTOR INPUT
    # =========================================================

    motor_power = float(
        input("\nEnter motor power (kW): ")
    )

    voltage = float(
        input("Enter supply voltage (V): ")
    )

    frequency = float(
        input("Enter frequency (Hz): ")
    )

    phase = int(
        input("Enter number of phases: ")
    )

    # =========================================================
    # MOTOR CURRENT
    # =========================================================

    print("\nMotor current option:")
    print("1. Enter motor nameplate current")
    print("2. Calculate automatically")

    current_option = input(
        "Select option (1/2): "
    )

    if current_option == "1":

        nameplate_current = float(
            input("Enter nameplate current (A): ")
        )

        motor_current = calculate_motor_current(
            power_kw=motor_power,
            voltage_v=voltage,
            phases=phase,
            nameplate_current=nameplate_current
        )

        current_source = "Nameplate"

    elif current_option == "2":

        motor_current = calculate_motor_current(
            power_kw=motor_power,
            voltage_v=voltage,
            phases=phase
        )

        current_source = "Calculated"

    else:

        print("\nInvalid current option.")
        return

    # =========================================================
    # STARTING / CONTROL INPUT
    # =========================================================

    starter_type = input(
        "\nEnter starting method (DOL): "
    )

    starting_type = input(
        "Enter starting duty (Normal/Heavy duty): "
    )

    control_voltage = float(
        input("Enter control voltage (V): ")
    )

    coordination_type = input(
        "Enter coordination type (Type 1/Type 2): "
    )

    # =========================================================
    # INPUT SUMMARY
    # =========================================================

    print("\n================================")
    print("        INPUT SUMMARY")
    print("================================")

    print(f"Motor power:       {motor_power} kW")
    print(f"Supply voltage:    {voltage} V")
    print(f"Frequency:         {frequency} Hz")
    print(f"Phases:            {phase}")
    print(f"Motor current:     {motor_current} A")
    print(f"Current source:    {current_source}")
    print(f"Starting method:   {starter_type}")
    print(f"Starting duty:     {starting_type}")
    print(f"Control voltage:   {control_voltage} V")
    print(f"Coordination:      {coordination_type}")

    # =========================================================
    # ENGINEERING CALCULATION
    # =========================================================

    print("\n================================")
    print("ENGINEERING CALCULATION")
    print("================================")

    print(
        "Motor current:",
        motor_current,
        "A"
    )

    # =========================================================
    # RANDOM FOREST
    # =========================================================

    print("\n================================")
    print("      ML RECOMMENDATION")
    print("================================")

    model = DOLRecommendationModel()

    model.load_dataset()

    model.train()

    recommendation, validation = model.recommend(
        motor_power_kw=motor_power,
        motor_current_a=motor_current,
        voltage_v=voltage,
        starter_type=starter_type,
        starting_type=starting_type,
        coordination_type=coordination_type
    )

    # =========================================================
    # CHECK RECOMMENDATION
    # =========================================================

    if recommendation is None:

        print("\nDesign cannot continue.")

        print(
            "No compatible manufacturer "
            "configuration was found."
        )

        return

    if not validation:

        print("\nDesign cannot continue.")

        print(
            "The recommended configuration "
            "failed engineering validation."
        )

        return

    # =========================================================
    # STORE USER INPUTS IN CONFIGURATION
    # =========================================================

    recommendation["Control_Voltage_V"] = control_voltage
    recommendation["Frequency_Hz"] = frequency
    recommendation["Phase"] = phase

    # =========================================================
    # GENERATE DOL CIRCUIT
    # =========================================================

    print("\n================================")
    print("GENERATING DOL CIRCUIT")
    print("================================")

    # IMPORTANT:
    # Pass control_voltage explicitly
    # to the circuit generator.

    generator = DOLCircuitGenerator(
        recommendation,
        control_voltage=control_voltage
    )

    circuit = generator.generate()

    # =========================================================
    # DISPLAY POWER CIRCUIT
    # =========================================================

    print("\nPOWER CIRCUIT")
    print("--------------------------------")

    for phase_data in circuit[
        "power_circuit"
    ]["connections"]:

        print(
            phase_data["phase"],
            "->",
            " -> ".join(
                phase_data["path"]
            )
        )

    # =========================================================
    # DISPLAY CONTROL CIRCUIT
    # =========================================================

    print("\nCONTROL CIRCUIT")
    print("--------------------------------")

    for key, device in circuit[
        "control_circuit"
    ]["devices"].items():

        print(
            key,
            "->",
            device
        )

    # =========================================================
    # GENERATE BOM
    # =========================================================

    print("\n================================")
    print("GENERATING BILL OF MATERIALS")
    print("================================")

    # IMPORTANT:
    # Pass control_voltage explicitly
    # to the BOM generator.

    bom_generator = BOMGenerator(
        recommendation,
        control_voltage=control_voltage
    )

    bom_generator.display()

    # =========================================================
    # GENERATE ELECTRICAL SCHEMATIC
    # =========================================================

    print("\n================================")
    print("GENERATING ELECTRICAL SCHEMATIC")
    print("================================")

    schematic = DOLSchematic(
        recommendation,
        motor_current=motor_current,
        frequency=frequency,
        control_voltage=control_voltage,
        phase=phase,
        coordination_type=coordination_type
    )

    schematic.generate()

    # =========================================================
    # COMPLETE
    # =========================================================

    print("\n================================")
    print("INTELLIPANEL DESIGN COMPLETE")
    print("================================")

    print("\nSchematic saved to:")

    print(
        "output\\intellipanel_dol_schematic.png"
    )


if __name__ == "__main__":
    main()