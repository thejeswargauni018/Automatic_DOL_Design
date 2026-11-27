import pandas as pd
import os


ABB_PATH = "data/abb_dol_coordination_dataset.csv"
SCHNEIDER_PATH = "data/schneider_dol_coordination_dataset.csv"

OUTPUT_PATH = "data/intellipanel_master_dataset.csv"


print("\n================================")
print("INTELLIPANEL MASTER DATASET")
print("================================")


# --------------------------------
# CHECK FILES
# --------------------------------

if not os.path.exists(ABB_PATH):

    print("\nERROR: ABB dataset not found.")
    print(ABB_PATH)
    exit()


if not os.path.exists(SCHNEIDER_PATH):

    print("\nERROR: Schneider dataset not found.")
    print(SCHNEIDER_PATH)
    exit()


# --------------------------------
# LOAD DATASETS
# --------------------------------

print("\nLoading ABB dataset...")

abb = pd.read_csv(ABB_PATH)

print("ABB rows:", len(abb))


print("\nLoading Schneider dataset...")

schneider = pd.read_csv(SCHNEIDER_PATH)

print("Schneider rows:", len(schneider))


# --------------------------------
# STANDARDIZE ABB COLUMN NAMES
# --------------------------------

print("\nStandardizing ABB columns...")

abb = abb.rename(
    columns={
        "Source_Manufacturer": "Manufacturer",
        "Source_Table": "Source_Table"
    }
)


# --------------------------------
# ADD SOURCE INFORMATION
# --------------------------------

if "Source_Page" not in abb.columns:

    abb["Source_Page"] = None


if "Source_Document" not in abb.columns:

    abb["Source_Document"] = None


if "Frequency_Hz" not in abb.columns:

    abb["Frequency_Hz"] = None


if "Phase" not in abb.columns:

    abb["Phase"] = None


# --------------------------------
# ADD ABB SOURCE DOCUMENT
# --------------------------------

abb["Source_Document"] = abb[
    "Source_Table"
].apply(
    lambda x: f"ABB Coordination Table {x}"
    if pd.notna(x)
    else None
)


# --------------------------------
# STANDARDIZE SCHNEIDER
# --------------------------------

print("\nStandardizing Schneider columns...")

if "Source_URL" not in schneider.columns:

    schneider["Source_URL"] = None

if "Source_Table" not in schneider.columns:

    schneider["Source_Table"] = None

if "Protection_Trip_Current_A" not in schneider.columns:

    schneider["Protection_Trip_Current_A"] = None

if "Trip_Class" not in schneider.columns:

    schneider["Trip_Class"] = None


# --------------------------------
# VOLTAGE STANDARDIZATION
# --------------------------------

def standardize_voltage(value):

    if pd.isna(value):

        return None

    value = str(value).strip()

    # Convert numeric-looking values such as
    # 415.0 into 415

    try:

        numeric_value = float(value)

        if numeric_value.is_integer():

            return str(int(numeric_value))

        return str(numeric_value)

    except ValueError:

        pass

    # Preserve voltage ranges such as:
    # 220/230
    # 500/525
    # 660/690

    return value


abb["Voltage_V"] = abb[
    "Voltage_V"
].apply(standardize_voltage)


schneider["Voltage_V"] = schneider[
    "Voltage_V"
].apply(standardize_voltage)


# --------------------------------
# REQUIRED COLUMNS
# --------------------------------

required_columns = [

    "Manufacturer",

    "Motor_Power_kW",
    "Motor_Current_A",
    "Voltage_V",

    "Frequency_Hz",
    "Phase",

    "Starter_Type",
    "Starting_Type",

    "Protection_Type",
    "Protection_Model",
    "Protection_Rating_A",
    "Protection_Trip_Current_A",

    "Contactor_Model",
    "Contactor_Rating_A",

    "Overload_Model",
    "Overload_Min_A",
    "Overload_Max_A",

    "Trip_Class",
    "Coordination_Type",

    "Source_URL",
    "Source_Table",
    "Source_Page",
    "Source_Document"
]


# --------------------------------
# CREATE MISSING COLUMNS
# --------------------------------

for column in required_columns:

    if column not in abb.columns:

        abb[column] = None

    if column not in schneider.columns:

        schneider[column] = None


# --------------------------------
# SAME COLUMN ORDER
# --------------------------------

abb = abb[
    required_columns
]

schneider = schneider[
    required_columns
]


# --------------------------------
# COMBINE DATASETS
# --------------------------------

print("\nCombining datasets...")

master = pd.concat(
    [abb, schneider],
    ignore_index=True
)


# --------------------------------
# REMOVE EXACT DUPLICATES
# --------------------------------

before_duplicates = len(master)

master = master.drop_duplicates()

after_duplicates = len(master)

duplicates_removed = (
    before_duplicates - after_duplicates
)


# --------------------------------
# SAVE MASTER DATASET
# --------------------------------

master.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------
# RESULTS
# --------------------------------

print("\n================================")
print("MASTER DATASET CREATED")
print("================================")

print("\nABB rows loaded:")
print(len(abb))

print("\nSchneider rows loaded:")
print(len(schneider))

print("\nCombined rows:")
print(before_duplicates)

print("\nDuplicates removed:")
print(duplicates_removed)

print("\nFinal rows:")
print(len(master))

print("\nFinal columns:")
print(len(master.columns))


# --------------------------------
# MANUFACTURER DISTRIBUTION
# --------------------------------

print("\n--------------------------------")
print("Manufacturer distribution")
print("--------------------------------")

print(
    master["Manufacturer"]
    .value_counts(dropna=False)
)


# --------------------------------
# STARTER DISTRIBUTION
# --------------------------------

print("\n--------------------------------")
print("Starter distribution")
print("--------------------------------")

print(
    master["Starter_Type"]
    .value_counts(dropna=False)
)


# --------------------------------
# COORDINATION DISTRIBUTION
# --------------------------------

print("\n--------------------------------")
print("Coordination distribution")
print("--------------------------------")

print(
    master["Coordination_Type"]
    .value_counts(dropna=False)
)


# --------------------------------
# VOLTAGE DISTRIBUTION
# --------------------------------

print("\n--------------------------------")
print("Voltage distribution")
print("--------------------------------")

print(
    master["Voltage_V"]
    .value_counts(dropna=False)
    .sort_index()
)


# --------------------------------
# MISSING VALUES
# --------------------------------

print("\n--------------------------------")
print("Missing values")
print("--------------------------------")

print(
    master.isnull().sum()
)


# --------------------------------
# SAMPLE DATA
# --------------------------------

print("\n--------------------------------")
print("First 10 rows")
print("--------------------------------")

print(
    master[
        [
            "Manufacturer",
            "Motor_Power_kW",
            "Motor_Current_A",
            "Voltage_V",
            "Starter_Type",
            "Protection_Model",
            "Contactor_Model",
            "Overload_Model",
            "Coordination_Type"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\n--------------------------------")
print("Saved to")
print("--------------------------------")

print(OUTPUT_PATH)


print("\n================================")
print("MERGE COMPLETE")
print("================================")