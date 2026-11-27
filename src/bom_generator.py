class BOMGenerator:

    def __init__(
        self,
        configuration,
        control_voltage=None
    ):

        self.configuration = configuration
        self.control_voltage = control_voltage

    def generate(self):

        manufacturer = self.configuration.get(
            "Manufacturer",
            "Not specified"
        )

        motor_power = self.configuration.get(
            "Motor_Power_kW"
        )

        motor_current = self.configuration.get(
            "Motor_Current_A"
        )

        voltage = self.configuration.get(
            "Voltage_V"
        )

        protection_model = self.configuration.get(
            "Protection_Model",
            "Not specified"
        )

        protection_type = self.configuration.get(
            "Protection_Type",
            "Not specified"
        )

        protection_rating = self.configuration.get(
            "Protection_Rating_A"
        )

        contactor_model = self.configuration.get(
            "Contactor_Model",
            "Not specified"
        )

        contactor_rating = self.configuration.get(
            "Contactor_Rating_A"
        )

        overload_model = self.configuration.get(
            "Overload_Model",
            "Not specified"
        )

        overload_min = self.configuration.get(
            "Overload_Min_A"
        )

        overload_max = self.configuration.get(
            "Overload_Max_A"
        )

        # -----------------------------
        # Protection rating
        # -----------------------------

        if (
            protection_rating is not None
            and str(protection_rating).lower() != "nan"
        ):

            protection_rating_text = (
                f"{protection_rating} A"
            )

        else:

            protection_rating_text = (
                "Not specified"
            )

        # -----------------------------
        # Contactor rating
        # -----------------------------

        if (
            contactor_rating is not None
            and str(contactor_rating).lower() != "nan"
        ):

            contactor_rating_text = (
                f"{contactor_rating} A"
            )

        else:

            contactor_rating_text = (
                "Not specified"
            )

        # -----------------------------
        # Overload range
        # -----------------------------

        if (
            overload_min is not None
            and overload_max is not None
            and str(overload_min).lower() != "nan"
            and str(overload_max).lower() != "nan"
        ):

            overload_range = (
                f"{overload_min}–"
                f"{overload_max} A"
            )

        else:

            overload_range = (
                "Not specified"
            )

        # -----------------------------
        # Control voltage
        # -----------------------------

        if self.control_voltage is not None:

            control_voltage_text = (
                f"{self.control_voltage} V"
            )

        else:

            control_voltage_text = (
                "Not specified"
            )

        # -----------------------------
        # BOM
        # -----------------------------

        bom = [

            {
                "Quantity": 1,
                "Component": "Motor",
                "Model": f"{motor_power} kW Motor",
                "Rating": (
                    f"{motor_current} A, "
                    f"{voltage} V"
                ),
                "Manufacturer": "User specified"
            },

            {
                "Quantity": 1,
                "Component": protection_type,
                "Model": protection_model,
                "Rating": protection_rating_text,
                "Manufacturer": manufacturer
            },

            {
                "Quantity": 1,
                "Component": "Contactor",
                "Model": contactor_model,
                "Rating": contactor_rating_text,
                "Manufacturer": manufacturer
            },

            {
                "Quantity": 1,
                "Component": "Overload Relay",
                "Model": overload_model,
                "Rating": overload_range,
                "Manufacturer": manufacturer
            },

            {
                "Quantity": 1,
                "Component": "START Push Button",
                "Model": "NO",
                "Rating": "Control circuit",
                "Manufacturer": "Not specified"
            },

            {
                "Quantity": 1,
                "Component": "STOP Push Button",
                "Model": "NC",
                "Rating": "Control circuit",
                "Manufacturer": "Not specified"
            },

            {
                "Quantity": 1,
                "Component": "Contactor Auxiliary Contact",
                "Model": "13-14 NO",
                "Rating": "Seal-in contact",
                "Manufacturer": manufacturer
            },

            {
                "Quantity": 1,
                "Component": "Overload Auxiliary Contact",
                "Model": "95-96 NC",
                "Rating": "Trip contact",
                "Manufacturer": manufacturer
            },

            {
                "Quantity": 1,
                "Component": "Contactor Coil",
                "Model": contactor_model,
                "Rating": control_voltage_text,
                "Manufacturer": manufacturer
            }
        ]

        return bom

    def display(self):

        bom = self.generate()

        print("\n================================")
        print("        BILL OF MATERIALS")
        print("================================")

        print(
            f"{'Qty':<5}"
            f"{'Component':<32}"
            f"{'Model':<30}"
            f"{'Rating':<22}"
            f"Manufacturer"
        )

        print("-" * 125)

        for item in bom:

            print(
                f"{item['Quantity']:<5}"
                f"{item['Component']:<32}"
                f"{item['Model']:<30}"
                f"{item['Rating']:<22}"
                f"{item['Manufacturer']}"
            )

        print("-" * 125)