import math


def calculate_motor_current(
    power_kw,
    voltage_v,
    efficiency=0.85,
    power_factor=0.80,
    phases=3,
    nameplate_current=None
):
    """
    Calculate or use the motor full-load current.

    If nameplate_current is provided, it is used directly.
    Otherwise, current is calculated using:

    I = P / (sqrt(3) × V × efficiency × power factor)
    """

    # Basic validation
    if power_kw <= 0:
        raise ValueError("Motor power must be greater than zero.")

    if voltage_v <= 0:
        raise ValueError("Voltage must be greater than zero.")

    if phases != 3:
        raise ValueError("This prototype supports 3-phase motors.")

    if not 0 < efficiency <= 1:
        raise ValueError("Efficiency must be between 0 and 1.")

    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be between 0 and 1.")

    # Use actual motor nameplate current if provided
    if nameplate_current is not None:

        if nameplate_current <= 0:
            raise ValueError(
                "Nameplate current must be greater than zero."
            )

        return round(nameplate_current, 2)

    # Otherwise calculate current
    power_watts = power_kw * 1000

    current = power_watts / (
        math.sqrt(3)
        * voltage_v
        * efficiency
        * power_factor
    )

    return round(current, 2)