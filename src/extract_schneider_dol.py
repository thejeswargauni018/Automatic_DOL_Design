import pdfplumber
import pandas as pd
import os


PDF_PATH = "data/schneider_source_document.pdf"
OUTPUT_PATH = "data/schneider_dol_pages_raw.csv"

TARGET_PAGES = [15, 16]


print("\n================================")
print("SCHNEIDER DOL EXTRACTION")
print("================================")

if not os.path.exists(PDF_PATH):
    print("ERROR: Schneider PDF not found.")
    exit()


all_tables = []


with pdfplumber.open(PDF_PATH) as pdf:

    print("\nTotal PDF pages:", len(pdf.pages))

    for page_number in TARGET_PAGES:

        print(
            f"\nReading PDF page {page_number}..."
        )

        page = pdf.pages[page_number - 1]

        tables = page.extract_tables()

        print(
            "Tables found:",
            len(tables)
        )

        for table_number, table in enumerate(
            tables,
            start=1
        ):

            if not table:
                continue

            df = pd.DataFrame(table)

            df["Source_Page"] = page_number
            df["Table_Number"] = table_number

            all_tables.append(df)


if not all_tables:

    print("\nERROR: No tables extracted.")
    exit()


combined = pd.concat(
    all_tables,
    ignore_index=True
)


combined.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n================================")
print("EXTRACTION COMPLETE")
print("================================")

print(
    "Rows extracted:",
    len(combined)
)

print(
    "Columns:",
    len(combined.columns)
)

print(
    "Saved to:",
    OUTPUT_PATH
)

print("\nFirst 20 rows:")
print(
    combined.head(20).to_string()
)