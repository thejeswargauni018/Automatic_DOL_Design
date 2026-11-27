import os
import time
from io import BytesIO

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# CONFIGURATION
# ============================================================

URL = (
    "https://ckm-content.se.com/ckmContent/"
    "sfc/servlet.shepherd/document/download/"
    "0698V00000YG0vXQAT"
)

OUTPUT_FILE = (
    "data/schneider_dol_coordination_dataset.csv"
)

SOURCE_FILE = (
    "data/schneider_source_document"
)


# ============================================================
# CREATE DATA FOLDER
# ============================================================

os.makedirs("data", exist_ok=True)


print("\n================================")
print("SCHNEIDER DOL DATASET BUILDER")
print("================================")


# ============================================================
# DOWNLOAD SCHNEIDER DOCUMENT
# ============================================================

print("\nDownloading Schneider document...")


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}


# Retry temporary server errors
retry_strategy = Retry(
    total=4,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(
    max_retries=retry_strategy
)

session = requests.Session()

session.mount(
    "https://",
    adapter
)

session.mount(
    "http://",
    adapter
)


try:

    response = session.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

except requests.exceptions.HTTPError as error:

    print("\nERROR: Schneider server rejected the request.")

    print(
        "HTTP status:",
        response.status_code
    )

    print(
        "\nThe Schneider document server may be temporarily "
        "unavailable."
    )

    print(
        "No fake or manually generated dataset will be created."
    )

    raise SystemExit


except requests.exceptions.RequestException as error:

    print("\nERROR: Could not download Schneider document.")

    print(error)

    raise SystemExit


print("Schneider document downloaded.")

print(
    "Downloaded size:",
    len(response.content),
    "bytes"
)


# ============================================================
# SAVE ORIGINAL DOCUMENT
# ============================================================

content_type = response.headers.get(
    "Content-Type",
    ""
).lower()


if "pdf" in content_type:

    source_path = SOURCE_FILE + ".pdf"

else:

    source_path = SOURCE_FILE + ".html"


with open(
    source_path,
    "wb"
) as file:

    file.write(
        response.content
    )


print(
    "Source saved to:",
    source_path
)


# ============================================================
# FIND TABLES
# ============================================================

print("\nReading Schneider tables...")


tables = []


# Try lxml first
try:

    tables = pd.read_html(
        BytesIO(response.content),
        flavor="lxml"
    )

    print(
        "Tables found using lxml:",
        len(tables)
    )

except Exception as error:

    print(
        "lxml parser could not read the document."
    )

    print(
        "Trying html5lib..."
    )

    try:

        tables = pd.read_html(
            BytesIO(response.content),
            flavor="html5lib"
        )

        print(
            "Tables found using html5lib:",
            len(tables)
        )

    except Exception as second_error:

        print(
            "\nERROR: No readable HTML tables were found."
        )

        print(
            "This Schneider document may be a PDF rather "
            "than an HTML table."
        )

        print(
            "\nThe downloaded source has been preserved at:"
        )

        print(
            source_path
        )

        raise SystemExit


if len(tables) == 0:

    print(
        "\nNo tables were found."
    )

    print(
        "No dataset was created."
    )

    raise SystemExit


# ============================================================
# INSPECT TABLES
# ============================================================

print("\n================================")
print("TABLE INSPECTION")
print("================================")


for index, table in enumerate(tables):

    print(
        f"\nTable {index}: "
        f"{table.shape[0]} rows × "
        f"{table.shape[1]} columns"
    )

    print(
        table.head(3).to_string(
            index=False
        )
    )


# ============================================================
# FIND MOST RELEVANT TABLE
# ============================================================

selected_table = None
selected_index = None


keywords = [
    "motor",
    "contactor",
    "thermal",
    "circuit breaker",
    "breaker",
    "380",
    "415",
    "kw"
]


for index, table in enumerate(tables):

    table_text = (
        table.astype(str)
        .to_string()
        .lower()
    )

    score = 0

    for keyword in keywords:

        if keyword in table_text:

            score += 1


    if score >= 3:

        selected_table = table.copy()

        selected_index = index

        print(
            "\nSelected Schneider table:",
            index
        )

        break


if selected_table is None:

    print(
        "\nCould not automatically identify "
        "the DOL coordination table."
    )

    print(
        "No dataset was created because we do not "
        "want to guess the Schneider columns."
    )

    raise SystemExit


df = selected_table.copy()


# ============================================================
# FLATTEN MULTI-LEVEL COLUMNS
# ============================================================

if isinstance(
    df.columns,
    pd.MultiIndex
):

    df.columns = [

        "_".join(
            str(value)
            for value in column
            if str(value) != "nan"
        ).strip()

        for column in df.columns
    ]


print("\nSchneider columns:")

for column in df.columns:

    print(
        "-",
        column
    )


# ============================================================
# SAVE RAW EXTRACTED TABLE
# ============================================================

raw_file = (
    "data/schneider_extracted_raw.csv"
)

df.to_csv(
    raw_file,
    index=False
)

print(
    "\nRaw Schneider table saved to:"
)

print(
    raw_file
)


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

rename_map = {}


for column in df.columns:

    text = str(column).lower()


    # Motor power
    if (
        "p (kw)" in text
        or "power" in text
        or "kw" in text
    ):

        if "Motor_Power_kW" not in rename_map.values():

            rename_map[column] = (
                "Motor_Power_kW"
            )


    # 415 V current
    elif (
        "415" in text
        and (
            "current" in text
            or "i (a)" in text
            or "amp" in text
        )
    ):

        rename_map[column] = (
            "Motor_Current_415V_A"
        )


    # 380 V current
    elif (
        "380" in text
        and (
            "current" in text
            or "i (a)" in text
            or "amp" in text
        )
    ):

        rename_map[column] = (
            "Motor_Current_380V_A"
        )


    # Protection / breaker
    elif (
        "circuit breaker" in text
        or "breaker" in text
    ):

        rename_map[column] = (
            "Protection_Model"
        )


    # Contactor
    elif "contactor" in text:

        rename_map[column] = (
            "Contactor_Model"
        )


    # Thermal relay
    elif (
        "thermal relay" in text
        or "thermal" in text
        or "overload" in text
    ):

        rename_map[column] = (
            "Overload_Model"
        )


df = df.rename(
    columns=rename_map
)


print("\nDetected standardized columns:")

for column in df.columns:

    print(
        "-",
        column
    )


# ============================================================
# REQUIRED DATA CHECK
# ============================================================

if "Motor_Power_kW" not in df.columns:

    print(
        "\nERROR: Motor power column could not "
        "be identified."
    )

    print(
        "Dataset was NOT created."
    )

    raise SystemExit


if (
    "Motor_Current_415V_A" not in df.columns
    and
    "Motor_Current_380V_A" not in df.columns
):

    print(
        "\nERROR: Motor current column could "
        "not be identified."
    )

    print(
        "Dataset was NOT created."
    )

    raise SystemExit


# ============================================================
# CREATE STANDARD CURRENT COLUMN
# ============================================================

if "Motor_Current_415V_A" in df.columns:

    df["Motor_Current_A"] = df[
        "Motor_Current_415V_A"
    ]

else:

    df["Motor_Current_A"] = df[
        "Motor_Current_380V_A"
    ]


# ============================================================
# STANDARD INTELLIPANEL INFORMATION
# ============================================================

df["Voltage_V"] = 415

df["Frequency_Hz"] = 50

df["Phase"] = 3

df["Starter_Type"] = "DOL"

df["Starting_Type"] = "Normal"

df["Protection_Type"] = (
    "Circuit Breaker"
)

df["Coordination_Type"] = (
    "Type 2"
)

df["Source_Manufacturer"] = (
    "Schneider Electric"
)

df["Source_URL"] = URL


# ============================================================
# CONVERT NUMERIC FIELDS
# ============================================================

numeric_columns = [
    "Motor_Power_kW",
    "Motor_Current_A"
]


for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# REMOVE INVALID ROWS
# ============================================================

df = df.dropna(
    subset=[
        "Motor_Power_kW",
        "Motor_Current_A"
    ]
)


# Remove obviously empty rows

df = df[
    df["Motor_Power_kW"] > 0
]

df = df[
    df["Motor_Current_A"] > 0
]


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

final_columns = [
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
    "Contactor_Model",
    "Contactor_Rating_A",
    "Overload_Model",
    "Overload_Range",
    "Coordination_Type",
    "Source_Manufacturer",
    "Source_URL"
]


# Only use columns that actually exist

final_columns = [
    column
    for column in final_columns
    if column in df.columns
]


df = df[
    final_columns
]


# ============================================================
# SAVE FINAL DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n================================")
print("SCHNEIDER DATASET CREATED")
print("================================")

print(
    "Rows:",
    len(df)
)

print(
    "Columns:",
    len(df.columns)
)

print("\nFinal columns:")

for column in df.columns:

    print(
        "-",
        column
    )


print("\nPreview:")

print(
    df.head(10).to_string(
        index=False
    )
)


print("\nSaved to:")

print(
    OUTPUT_FILE
)

print(
    "\nSchneider dataset extraction complete."
)