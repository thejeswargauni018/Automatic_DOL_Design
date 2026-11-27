import pandas as pd
import re


INPUT_PATH = "data/abb_dol_coordination_raw.csv"
OUTPUT_PATH = "data/abb_dol_coordination_dataset.csv"


# Information specific to each ABB coordination table
TABLE_INFO = {
    3976: {
        "Starter_Type": "DOL",
        "Starting_Type": "Normal",
        "Voltage_V": 415,
        "Protection_Type": "MCCB",
        "Coordination_Type": "IEC Type 2",
    },

    3951: {
        "Starter_Type": "DOL",
        "Starting_Type": "Normal",
        "Voltage_V": 415,
        "Protection_Type": "MCCB",
        "Coordination_Type": "IEC Type 2",
    },

    5717: {
        "Starter_Type": "DOL",
        "Starting_Type": "Heavy duty",
        "Voltage_V": 400,
        "Protection_Type": "Switch fuse",
        "Coordination_Type": "IEC Type 2",
    },

    5140: {
        "Starter_Type": "DOL",
        "Starting_Type": "Heavy duty",
        "Voltage_V": 400,
        "Protection_Type": "Fuse",
        "Coordination_Type": "IEC Type 2",
    },
}


def extract_number(value):
    """Extract first numerical value from text."""

    if pd.isna(value):
        return None

    match = re.search(r"\d+(?:\.\d+)?", str(value))

    if match:
        return float(match.group())

    return None


def extract_range(value):
    """Extract lower and upper values from an overload range."""

    if pd.isna(value):
        return None, None

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        str(value)
    )

    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])

    return None, None


def extract_motor_power(value):
    """Convert '5.5 kW' into 5.5."""

    return extract_number(value)


def extract_motor_current(value):
    """Convert '11.5 A' into 11.5."""

    return extract_number(value)


def extract_mccb_rating(value):
    """
    Extract MCCB In rating.

    Example:
    XT2S 160 MF In 12.5 -> 12.5
    """

    if pd.isna(value):
        return None

    match = re.search(
        r"In\s+(\d+(?:\.\d+)?)",
        str(value),
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def clean_dataset():

    print("\n================================")
    print("CLEANING ABB DATASET")
    print("================================")

    df = pd.read_csv(INPUT_PATH)

    print("Raw rows:", len(df))

    # Remove the HTML header row
    df = df[
        pd.to_numeric(
            df["Source_Table"],
            errors="coerce"
        ).notna()
    ].copy()

    df["Source_Table"] = df["Source_Table"].astype(int)

    print("Valid ABB rows:", len(df))

    clean_rows = []

    for _, row in df.iterrows():

        table_id = row["Source_Table"]

        info = TABLE_INFO[table_id]

        motor_power = extract_motor_power(
            row["Motor"]
        )

        motor_current = extract_motor_current(
            row["Motor.1"]
        )

        # ---------------------------------
        # Determine protection information
        # ---------------------------------

        if table_id in [3976, 3951]:

            protection_model = row[
                "Molded case circuit-breaker"
            ]

            protection_rating = extract_mccb_rating(
                protection_model
            )

            protection_trip_current = (
                extract_number(
                    row[
                        "Molded case circuit-breaker.1"
                    ]
                )
            )

        elif table_id == 5717:

            protection_model = row[
                "Switch fuse.3"
            ]

            protection_rating = extract_number(
                row["Switch fuse.2"]
            )

            protection_trip_current = None

        elif table_id == 5140:

            protection_model = row[
                "Fuse.2"
            ]

            protection_rating = extract_number(
                row["Fuse.1"]
            )

            protection_trip_current = None

        else:

            protection_model = None
            protection_rating = None
            protection_trip_current = None

        # ---------------------------------
        # Contactor
        # ---------------------------------

        contactor_model = row["Contactor"]

        # Extract contactor rating from model
        # Examples: AF09 -> 9, AF26 -> 26, AF30 -> 30
        contactor_rating = extract_number(
            contactor_model
        )

        # ---------------------------------
        # Overload
        # ---------------------------------

        overload_model = row[
            "Overload protection"
        ]

        trip_class = row[
            "Overload protection.1"
        ]

        overload_range = row[
            "Overload protection.2"
        ]

        overload_min, overload_max = extract_range(
            overload_range
        )

        # ---------------------------------
        # Create standardized row
        # ---------------------------------

        clean_rows.append({

            "Motor_Power_kW": motor_power,

            "Motor_Current_A": motor_current,

            "Voltage_V": info["Voltage_V"],

            "Starter_Type": info["Starter_Type"],

            "Starting_Type": info["Starting_Type"],

            "Protection_Type": info["Protection_Type"],

            "Protection_Model": protection_model,

            "Protection_Rating_A": protection_rating,

            "Protection_Trip_Current_A":
                protection_trip_current,

            "Contactor_Model": contactor_model,

            "Contactor_Rating_A":
                contactor_rating,

            "Overload_Model": overload_model,

            "Overload_Min_A":
                overload_min,

            "Overload_Max_A":
                overload_max,

            "Trip_Class": trip_class,

            "Coordination_Type":
                info["Coordination_Type"],

            "Source_Manufacturer":
                "ABB",

            "Source_Table":
                table_id,

            "Source_URL":
                row["Source_URL"],
        })

    clean_df = pd.DataFrame(clean_rows)

    # Save cleaned dataset
    clean_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n================================")
    print("CLEAN DATASET CREATED")
    print("================================")

    print("Rows:", len(clean_df))

    print(
        "Columns:",
        len(clean_df.columns)
    )

    print("\nColumns:")
    for column in clean_df.columns:
        print("-", column)

    print("\nRows by ABB table:")
    print(
        clean_df["Source_Table"]
        .value_counts()
        .sort_index()
    )

    print("\nMissing values:")
    print(
        clean_df.isna().sum()
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    clean_dataset()