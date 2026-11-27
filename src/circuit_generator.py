class DOLCircuitGenerator:

    def __init__(
        self,
        configuration,
        control_voltage=None
    ):

        self.configuration = configuration
        self.control_voltage = control_voltage

        self.protection_model = configuration.get(
            "Protection_Model",
            "Protection"
        )

        self.contactor_model = configuration.get(
            "Contactor_Model",
            "Contactor"
        )

        self.overload_model = configuration.get(
            "Overload_Model",
            "Overload"
        )

        self.manufacturer = configuration.get(
            "Manufacturer",
            "Not specified"
        )

        self.motor_power = configuration.get(
            "Motor_Power_kW",
            None
        )

        self.motor_current = configuration.get(
            "Motor_Current_A",
            None
        )

        self.voltage = configuration.get(
            "Voltage_V",
            None
        )

    def generate_power_circuit(self):

        power_circuit = {
            "type": "POWER",

            "supply": {
                "phases": ["L1", "L2", "L3"],
                "voltage": self.voltage
            },

            "devices": {

                "QF1": {
                    "type": "PROTECTION",
                    "model": self.protection_model,
                    "manufacturer": self.manufacturer
                },

                "KM1": {
                    "type": "CONTACTOR",
                    "model": self.contactor_model,
                    "manufacturer": self.manufacturer
                },

                "FR1": {
                    "type": "OVERLOAD",
                    "model": self.overload_model,
                    "manufacturer": self.manufacturer
                },

                "M1": {
                    "type": "MOTOR",
                    "power_kw": self.motor_power,
                    "current_a": self.motor_current,
                    "voltage_v": self.voltage
                }
            },

            "connections": [
                {
                    "phase": "L1",
                    "path": ["L1", "QF1", "KM1", "FR1", "U1"]
                },

                {
                    "phase": "L2",
                    "path": ["L2", "QF1", "KM1", "FR1", "V1"]
                },

                {
                    "phase": "L3",
                    "path": ["L3", "QF1", "KM1", "FR1", "W1"]
                }
            ],

            "motor": {
                "designation": "M1",
                "terminals": ["U1", "V1", "W1"],
                "protective_earth": "PE"
            }
        }

        return power_circuit

    def generate_control_circuit(self):

        control_circuit = {

            "type": "CONTROL",

            "supply": {
                "line": "L",
                "neutral": "N",
                "voltage": self.control_voltage
            },

            "devices": {

                "S0": {
                    "type": "PUSH_BUTTON",
                    "function": "STOP",
                    "contact": "NC",
                    "terminals": ["11", "12"]
                },

                "FR1_AUX": {
                    "type": "OVERLOAD_AUXILIARY",
                    "function": "OVERLOAD_TRIP",
                    "contact": "NC",
                    "terminals": ["95", "96"]
                },

                "S1": {
                    "type": "PUSH_BUTTON",
                    "function": "START",
                    "contact": "NO",
                    "terminals": ["3", "4"]
                },

                "KM1_AUX": {
                    "type": "CONTACTOR_AUXILIARY",
                    "function": "SEAL_IN",
                    "contact": "NO",
                    "terminals": ["13", "14"]
                },

                "KM1_COIL": {
                    "type": "CONTACTOR_COIL",
                    "function": "MAIN_CONTACTOR",
                    "control_voltage": self.control_voltage,
                    "terminals": ["A1", "A2"]
                }
            },

            "logic": {
                "series_devices": [
                    "S0",
                    "FR1_AUX"
                ],

                "parallel_devices": [
                    "S1",
                    "KM1_AUX"
                ],

                "coil": "KM1_COIL"
            },

            "connections": [

                {
                    "from": "L",
                    "to": "S0.11"
                },

                {
                    "from": "S0.12",
                    "to": "FR1_AUX.95"
                },

                {
                    "from": "FR1_AUX.96",
                    "to": "START_SEAL_IN_INPUT"
                },

                {
                    "from": "START_SEAL_IN_INPUT",
                    "to": "S1.3"
                },

                {
                    "from": "S1.4",
                    "to": "KM1_COIL.A1"
                },

                {
                    "from": "START_SEAL_IN_INPUT",
                    "to": "KM1_AUX.13"
                },

                {
                    "from": "KM1_AUX.14",
                    "to": "KM1_COIL.A1"
                },

                {
                    "from": "KM1_COIL.A2",
                    "to": "N"
                }
            ]
        }

        return control_circuit

    def generate(self):

        return {
            "circuit_type": "DOL",

            "description": (
                "Direct-On-Line motor starter "
                "with overload protection and "
                "contactor seal-in control."
            ),

            "power_circuit":
                self.generate_power_circuit(),

            "control_circuit":
                self.generate_control_circuit()
        }