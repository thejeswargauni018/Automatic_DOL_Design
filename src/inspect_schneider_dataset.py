import pandas as pd


DATASET_PATH = "data/schneider_dol_coordination_dataset.csv"

print("\n================================")
print("SCHNEIDER DATASET QUALITY CHECK")
print("================================")

df = pd.read_csv(DATASET_PATH)

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\n--------------------------------")
print("Missing values")
print("--------------------------------")

print(df.isnull().sum())

print("\n--------------------------------")
print("Duplicate rows")
print("--------------------------------")

print("Duplicates:", df.duplicated().sum())

print("\n--------------------------------")
print("Voltage distribution")
print("--------------------------------")

print(df["Voltage_V"].value_counts().sort_index())

print("\n--------------------------------")
print("Starter types")
print("--------------------------------")

print(df["Starter_Type"].value_counts())

print("\n--------------------------------")
print("Starting types")
print("--------------------------------")

print(df["Starting_Type"].value_counts())

print("\n--------------------------------")
print("Coordination types")
print("--------------------------------")

print(df["Coordination_Type"].value_counts())

print("\n--------------------------------")
print("Invalid overload ranges")
print("--------------------------------")

invalid_ranges = df[
    df["Overload_Min_A"] > df["Overload_Max_A"]
]

print("Invalid rows:", len(invalid_ranges))

print("\n--------------------------------")
print("Motor current outside overload range")
print("--------------------------------")

outside_range = df[
    (df["Motor_Current_A"] < df["Overload_Min_A"])
    |
    (df["Motor_Current_A"] > df["Overload_Max_A"])
]

print("Rows outside range:", len(outside_range))

print("\n--------------------------------")
print("Manufacturers")
print("--------------------------------")

print(df["Manufacturer"].value_counts())

print("\n================================")
print("QUALITY CHECK COMPLETE")
print("================================")
print("\n--------------------------------")
print("ROW OUTSIDE OVERLOAD RANGE")
print("--------------------------------")

print(
    outside_range.to_string(index=False)
)