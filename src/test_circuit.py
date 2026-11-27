from circuit_generator import DOLCircuitGenerator


configuration = {
    "Protection_Model": "XT2S 160 MF In 12.5",
    "Contactor_Model": "AF30",
    "Overload_Model": "EF19-18.9"
}


generator = DOLCircuitGenerator(configuration)

circuit = generator.generate()


print("\n================================")
print("DOL CIRCUIT GENERATED")
print("================================")


print("\nPOWER CIRCUIT")
print("--------------------------------")

for phase in circuit["power_circuit"]["phases"]:

    print(
        phase["phase"],
        "->",
        " -> ".join(phase["path"])
    )


print("\nCONTROL CIRCUIT")
print("--------------------------------")

for component in circuit["control_circuit"]["components"]:

    print("->", component)