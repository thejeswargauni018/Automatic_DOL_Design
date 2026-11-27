import pdfplumber
import pandas as pd
import os


PDF_PATH = "data/schneider_source_document.pdf"
OUTPUT_PATH = "data/schneider_extracted_raw.csv"


print("\n================================")
print("SCHNEIDER PDF TABLE EXTRACTION")
print("================================")

if not os.path.exists(PDF_PATH):
    print("ERROR: Schneider PDF not found.")
    print(PDF_PATH)
    exit()

print("\nOpening Schneider PDF...")

all_tables = []

with pdfplumber.open(PDF_PATH) as pdf:

    print(f"Total pages: {len(pdf.pages)}")

    for page_number, page in enumerate(pdf.pages, start=1):

        print(f"Checking page {page_number}...")

        tables = page.extract_tables()

        if tables:

            print(
                f"  Found {len(tables)} table(s)"
            )

            for table_number, table in enumerate(
                tables,
                start=1
            ):

                if table:

                    print(
                        f"  Saving table {table_number}"
                    )

                    df = pd.DataFrame(table)

                    df["Page"] = page_number
                    df["Table_Number"] = table_number

                    all_tables.append(df)


if not all_tables:

    print("\nERROR: No tables were detected.")
    print(
        "The PDF may require visual/table extraction."
    )
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
    f"Extracted rows: {len(combined)}"
)

print(
    f"Extracted columns: {len(combined.columns)}"
)

print(
    f"Saved to: {OUTPUT_PATH}"
)

print("\nFirst rows:")
print(combined.head(10).to_string())