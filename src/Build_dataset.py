import pandas as pd
import requests
from io import StringIO


ABB_TABLES = {
    3976: "https://www.lowvoltage-tools.abb.com/soc/Page/CoordinationTable.aspx?Id=3976",
    3951: "https://www.lowvoltage-tools.abb.com/soc/Page/CoordinationTable.aspx?Id=3951",
    5717: "https://www.lowvoltage-tools.abb.com/soc/Page/CoordinationTable.aspx?Id=5717",
    5140: "https://www.lowvoltage-tools.abb.com/soc/Page/CoordinationTable.aspx?Id=5140",
}


def load_abb_table(table_id, url):

    print(f"\nLoading ABB Table {table_id}...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        print("ABB page downloaded.")

        tables = pd.read_html(StringIO(response.text))

        print("HTML tables found:", len(tables))

        for i, table in enumerate(tables):

            table_text = " ".join(
                str(column)
                for column in table.columns
            )

            if "Motor" in table_text:

                print(
                    f"Selected HTML table {i}"
                )

                table["Source_Manufacturer"] = "ABB"
                table["Source_Table"] = table_id
                table["Source_URL"] = url

                return table

        print(
            f"Could not identify the coordination table "
            f"for ABB Table {table_id}."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            f"TIMEOUT: ABB Table {table_id} "
            f"did not respond within 15 seconds."
        )

        return None

    except Exception as e:

        print(
            f"ERROR loading Table {table_id}:"
        )

        print(e)

        return None


def main():

    all_tables = []

    for table_id, url in ABB_TABLES.items():

        table = load_abb_table(
            table_id,
            url
        )

        if table is not None:

            all_tables.append(table)

    if not all_tables:

        print("\nNo ABB tables were loaded.")
        return

    combined = pd.concat(
        all_tables,
        ignore_index=True
    )

    print("\n================================")
    print("ABB DATASET CREATED")
    print("================================")

    print(
        "Rows:",
        len(combined)
    )

    print(
        "Columns:",
        len(combined.columns)
    )

    print("\nSource table distribution:")

    print(
        combined["Source_Table"].value_counts()
    )

    output_path = (
        "data/abb_dol_coordination_raw.csv"
    )

    combined.to_csv(
        output_path,
        index=False
    )

    print("\nDataset saved to:")

    print(output_path)


if __name__ == "__main__":
    main()