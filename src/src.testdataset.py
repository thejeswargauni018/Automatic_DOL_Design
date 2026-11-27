import pandas as pd

DATASET_PATH = "data/abb_dol_coordination_dataset.csv"

try:
    df = pd.read_csv(DATASET_PATH)

    print("\nDataset loaded successfully!")
    print("----------------------------")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")
    for column in df.columns:
        print("-", column)

    print("\nFirst 5 rows:")
    print(df.head())

except FileNotFoundError:
    print("ERROR: Dataset file was not found.")
    print("Check that the CSV is inside the data folder.")

except Exception as e:
    print("ERROR:", e)