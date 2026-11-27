from engineering import calculate_motor_current


print("\n================================")
print("ENGINEERING TEST")
print("================================")


# Test 1: Calculate current
current_calculated = calculate_motor_current(
    power_kw=5.5,
    voltage_v=415
)

print("\nTest 1 - Calculated current:")
print(current_calculated, "A")


# Test 2: Use nameplate current
current_nameplate = calculate_motor_current(
    power_kw=5.5,
    voltage_v=415,
    nameplate_current=11.5
)

print("\nTest 2 - Nameplate current:")
print(current_nameplate, "A")