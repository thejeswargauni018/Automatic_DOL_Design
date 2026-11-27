import pymupdf
import pandas as pd
import os
import re


PDF_PATH = "data/schneider_source_document.pdf"
OUTPUT_PATH = "data/schneider_dol_coordination_dataset.csv"

# Schneider DOL coordination pages
PAGES = [15, 16]


# -------------------------------------------------
# VOLTAGE GROUPS
# -------------------------------------------------

VOLTAGE_COLUMNS = [
    ("220/230", 0, 1),
    ("380", 2, 3),
    ("415", 4, 5),
    ("440", 6, 7),
    ("500/525", 8, 9),
    ("660/690", 10, 11),
]


# -------------------------------------------------
# NUMBER CLEANING
# -------------------------------------------------

def clean_number(value):

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    value = value.replace(",", ".")

    try:
        return float(value)

    except ValueError:
        return None


# -------------------------------------------------
# OVERLOAD RANGE
# -------------------------------------------------

def parse_range(value):

    if value is None:
        return None, None

    value = str(value).strip()

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)",
        value
    )

    if not match:
        return None, None

    minimum = float(match.group(1))
    maximum = float(match.group(2))

    return minimum, maximum


# -------------------------------------------------
# GET PDF WORDS
# -------------------------------------------------

def get_words(page):

    words = page.get_text("words")

    result = []

    for word in words:

        x0, y0, x1, y1, text = word[:5]

        text = text.strip()

        if text == "":
            continue

        result.append({
            "x": x0,
            "y": y0,
            "text": text
        })

    return result


# -------------------------------------------------
# GROUP WORDS INTO ROWS
# -------------------------------------------------

def group_rows(words):

    rows = []

    tolerance = 2.0

    for word in sorted(
        words,
        key=lambda item: (item["y"], item["x"])
    ):

        placed = False

        for row in rows:

            if abs(
                row["y"] - word["y"]
            ) <= tolerance:

                row["words"].append(word)

                placed = True

                break

        if not placed:

            rows.append({
                "y": word["y"],
                "words": [word]
            })


    for row in rows:

        row["words"].sort(
            key=lambda item: item["x"]
        )


    return rows


# -------------------------------------------------
# GET SINGLE COLUMN VALUE
# -------------------------------------------------

def get_single_value(
    words,
    center_x,
    tolerance=8
):

    candidates = []

    for word in words:

        distance = abs(
            word["x"] - center_x
        )

        if distance <= tolerance:

            candidates.append(
                (
                    distance,
                    word["text"]
                )
            )


    if not candidates:

        return None


    candidates.sort(
        key=lambda item: item[0]
    )


    return candidates[0][1]


# -------------------------------------------------
# GET MULTIPLE WORDS FROM A COLUMN
# -------------------------------------------------

def get_column_words(
    words,
    center_x,
    left_tolerance=8,
    right_tolerance=38
):

    selected = []

    for word in words:

        if (
            center_x - left_tolerance
            <= word["x"]
            <= center_x + right_tolerance
        ):

            selected.append(word)


    selected.sort(
        key=lambda item: item["x"]
    )


    return selected


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():

    print("\n================================")
    print("SCHNEIDER CLEAN DOL DATASET")
    print("================================")


    if not os.path.exists(PDF_PATH):

        print(
            "\nERROR: Schneider PDF not found."
        )

        print(
            "Expected:",
            PDF_PATH
        )

        return


    print(
        "\nOpening:",
        PDF_PATH
    )


    pdf = pymupdf.open(
        PDF_PATH
    )


    dataset = []


    # -------------------------------------------------
    # PAGE-SPECIFIC COORDINATES
    # -------------------------------------------------

    coordinates = {

        15: {

            "power": [
                56.4,
                104.6,
                152.8,
                201.0,
                249.2,
                297.4
            ],

            "current": [
                80.5,
                128.7,
                176.9,
                225.1,
                273.3,
                321.5
            ],

            "breaker": 345.6,

            "breaker_rating": 393.8,

            "contactor": 424.9,

            "overload": 473.1,

            "overload_range": 521.3
        },


        16: {

            "power": [
                45.1,
                91.8,
                138.5,
                185.2,
                231.9,
                278.6
            ],

            "current": [
                68.4,
                115.2,
                161.9,
                208.6,
                255.3,
                302.0
            ],

            "breaker": 325.3,

            "breaker_rating": 408.3,

            "contactor": 434.4,

            "overload": 475.7,

            "overload_range": 517.0
        }
    }


    # -------------------------------------------------
    # PROCESS PAGES
    # -------------------------------------------------

    for page_number in PAGES:

        print(
            f"\nProcessing page {page_number}..."
        )


        page = pdf[
            page_number - 1
        ]


        words = get_words(
            page
        )


        rows = group_rows(
            words
        )


        coord = coordinates[
            page_number
        ]


        valid_component_rows = 0


        # -------------------------------------------------
        # PROCESS EACH TABLE ROW
        # -------------------------------------------------

        for row in rows:

            row_words = row["words"]


            # Skip headers
            if row["y"] < 285:

                continue


            # -------------------------------------------------
            # BREAKER
            # -------------------------------------------------

            breaker = get_single_value(
                row_words,
                coord["breaker"],
                tolerance=8
            )


            # -------------------------------------------------
            # BREAKER RATING
            # -------------------------------------------------

            breaker_rating = get_single_value(
                row_words,
                coord["breaker_rating"],
                tolerance=8
            )


            # -------------------------------------------------
            # CONTACTOR
            # -------------------------------------------------

            contactor = get_single_value(
                row_words,
                coord["contactor"],
                tolerance=8
            )


            # -------------------------------------------------
            # OVERLOAD MODEL
            #
            # Some models are split across multiple
            # PDF words, such as:
            #
            # LRD-33 12
            # LRD-33 21
            # LRD-33 57
            # -------------------------------------------------

            overload_words = get_column_words(
                row_words,
                coord["overload"],
                left_tolerance=8,
                right_tolerance=38
            )


            if overload_words:

                overload = " ".join(
                    word["text"]
                    for word in overload_words
                )

            else:

                overload = None


            # -------------------------------------------------
            # OVERLOAD RANGE
            # -------------------------------------------------

            overload_range = get_single_value(
                row_words,
                coord["overload_range"],
                tolerance=8
            )


            # -------------------------------------------------
            # VALID COMPONENT ROW
            # -------------------------------------------------

            if (
                breaker is None
                or contactor is None
                or overload is None
            ):

                continue


            valid_component_rows += 1


            # -------------------------------------------------
            # OVERLOAD RANGE
            # -------------------------------------------------

            overload_min, overload_max = parse_range(
                overload_range
            )


            # -------------------------------------------------
            # PROCESS SIX VOLTAGE GROUPS
            # -------------------------------------------------

            for index, voltage_info in enumerate(
                VOLTAGE_COLUMNS
            ):

                voltage_label = voltage_info[0]


                # Motor power column
                power_x = coord[
                    "power"
                ][index]


                # Motor current column
                current_x = coord[
                    "current"
                ][index]


                power = get_single_value(
                    row_words,
                    power_x,
                    tolerance=5
                )


                current = get_single_value(
                    row_words,
                    current_x,
                    tolerance=5
                )


                power_value = clean_number(
                    power
                )


                current_value = clean_number(
                    current
                )


                # Skip blank voltage cells
                if (
                    power_value is None
                    or current_value is None
                ):

                    continue


                # -------------------------------------------------
                # CREATE DATASET ROW
                # -------------------------------------------------

                dataset.append({

                    "Manufacturer":
                        "Schneider Electric",

                    "Motor_Power_kW":
                        power_value,

                    "Motor_Current_A":
                        current_value,

                    "Voltage_V":
                        voltage_label,

                    # Source does not explicitly establish
                    # these fields in our extraction.
                    "Frequency_Hz":
                        None,

                    "Phase":
                        None,

                    "Starter_Type":
                        "DOL",

                    "Starting_Type":
                        "Normal",

                    "Protection_Type":
                        "Circuit Breaker",

                    "Protection_Model":
                        breaker,

                    "Protection_Rating_A":
                        clean_number(
                            breaker_rating
                        ),

                    "Contactor_Model":
                        contactor,

                    # No explicit contactor current rating
                    # was extracted from this table.
                    "Contactor_Rating_A":
                        None,

                    "Overload_Model":
                        overload,

                    "Overload_Min_A":
                        overload_min,

                    "Overload_Max_A":
                        overload_max,

                    "Coordination_Type":
                        "Type 1",

                    "Source_Page":
                        page_number,

                    "Source_Document":
                        "schneider_source_document.pdf"
                })


        print(
            "  Valid component rows found:",
            valid_component_rows
        )


    pdf.close()


    # -------------------------------------------------
    # CHECK RESULTS
    # -------------------------------------------------

    if not dataset:

        print(
            "\nERROR: No Schneider DOL configurations found."
        )

        return


    df = pd.DataFrame(
        dataset
    )


    # Remove exact duplicate rows
    df = df.drop_duplicates()


    # Sort dataset
    df = df.sort_values(
        by=[
            "Voltage_V",
            "Motor_Power_kW",
            "Source_Page"
        ]
    ).reset_index(
        drop=True
    )


    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    print("\n================================")
    print("DATASET CREATED")
    print("================================")


    print(
        "Rows:",
        len(df)
    )


    print(
        "Columns:",
        len(df.columns)
    )


    print(
        "\nSaved to:",
        OUTPUT_PATH
    )


    print("\nVoltage distribution:")

    print(
        df[
            "Voltage_V"
        ]
        .value_counts()
        .sort_index()
    )


    print("\nOverload models found:")

    print(
        df[
            "Overload_Model"
        ]
        .value_counts()
        .head(25)
    )


    print("\nStarter types:")

    print(
        df[
            "Starter_Type"
        ]
        .value_counts()
    )


    print("\nStarting types:")

    print(
        df[
            "Starting_Type"
        ]
        .value_counts()
    )


    print("\nFirst 20 rows:")

    print(
        df.head(20).to_string(
            index=False
        )
    )


if __name__ == "__main__":

    main()