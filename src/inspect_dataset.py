import pandas as pd

DATASET_PATH = "data/abb_dol_coordination_raw.csv"

df = pd.read_csv(DATASET_PATH)

print("\n================================")
print("ABB RAW DATASET INSPECTION")
print("================================")

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nCOLUMN NAMES:")
print("----------------------------")

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

print("\nFIRST 3 ROWS:")
print("----------------------------")

print(df.head(3).to_string())

print("\nMISSING VALUES:")
print("----------------------------")

print(df.isna().sum())