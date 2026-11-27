import pandas as pd


def validate_dol_configuration(
    motor_current,
    voltage,
    starter_type,
    recommendation
):

    print("\n================================")
    print("ENGINEERING VALIDATION")
    print("================================")

    valid = True

    # --------------------------------
    # OVERLOAD
    # --------------------------------

    overload_min = recommendation.get(
        "Overload_Min_A"
    )

    overload_max = recommendation.get(
        "Overload_Max_A"
    )

    print(
        f"Motor current:       {motor_current:.2f} A"
    )

    if (
        overload_min is not None
        and overload_max is not None
        and pd.notna(overload_min)
        and pd.notna(overload_max)
    ):

        print(
            f"Overload range:      "
            f"{float(overload_min):.2f}–"
            f"{float(overload_max):.2f} A"
        )

        print(
            "Overload check:      "
            "Manufacturer configuration"
        )

    else:

        print("Overload range:      Not available")
        print("Overload check:      NOT AVAILABLE")

    # --------------------------------
    # CONTACTOR
    # --------------------------------

    contactor_rating = recommendation.get(
        "Contactor_Rating_A"
    )

    print(
        f"\nContactor rating:    "
        f"{contactor_rating}"
    )

    if (
        contactor_rating is not None
        and pd.notna(contactor_rating)
    ):

        try:

            if float(contactor_rating) >= float(motor_current):

                print("Contactor check:     PASS")

            else:

                print("Contactor check:     FAIL")
                valid = False

        except (ValueError, TypeError):

            print(
                "Contactor check:     NOT AVAILABLE"
            )

    else:

        print(
            "Contactor check:     NOT AVAILABLE"
        )

    # --------------------------------
    # PROTECTION
    # --------------------------------

    protection = recommendation.get(
        "Protection_Type"
    )

    protection_model = recommendation.get(
        "Protection_Model"
    )

    print(
        f"\nProtection:          "
        f"{protection}"
    )

    print(
        f"Protection model:    "
        f"{protection_model}"
    )

    if (
        protection is not None
        and str(protection).strip() != ""
        and pd.notna(protection)
    ):

        print("Protection check:    PASS")

    else:

        print("Protection check:    FAIL")
        valid = False

    # --------------------------------
    # STARTER TYPE
    # --------------------------------

    recommended_starter = recommendation.get(
        "Starter_Type"
    )

    print(
        f"\nStarter type:        "
        f"{recommended_starter}"
    )

    print(
        f"Requested starter:   "
        f"{starter_type}"
    )

    if (
        recommended_starter is not None
        and pd.notna(recommended_starter)
        and str(recommended_starter).strip().lower()
        ==
        str(starter_type).strip().lower()
    ):

        print("Starter check:       PASS")

    else:

        print("Starter check:       FAIL")
        valid = False

    # --------------------------------
    # VOLTAGE
    # --------------------------------

    recommended_voltage = recommendation.get(
        "Voltage_V"
    )

    print(
        f"\nRequested voltage:   "
        f"{voltage} V"
    )

    print(
        f"Configuration:       "
        f"{recommended_voltage} V"
    )

    voltage_match = False

    try:

        requested_voltage = float(voltage)

        if (
            recommended_voltage is not None
            and pd.notna(recommended_voltage)
        ):

            voltage_text = str(
                recommended_voltage
            ).strip()

            if "/" not in voltage_text:

                configuration_voltage = float(
                    voltage_text
                )

                if (
                    requested_voltage
                    == configuration_voltage
                ):

                    voltage_match = True

            else:

                voltage_values = (
                    voltage_text.split("/")
                )

                for value in voltage_values:

                    try:

                        if (
                            requested_voltage
                            == float(value.strip())
                        ):

                            voltage_match = True
                            break

                    except ValueError:

                        continue

    except (ValueError, TypeError):

        voltage_match = False

    if voltage_match:

        print("Voltage check:       PASS")

    else:

        print("Voltage check:       FAIL")
        valid = False

    # --------------------------------
    # FINAL STATUS
    # --------------------------------

    print("\n--------------------------------")

    if valid:

        print("FINAL STATUS: VALID")

    else:

        print("FINAL STATUS: INVALID")

    print("--------------------------------")

    return valid