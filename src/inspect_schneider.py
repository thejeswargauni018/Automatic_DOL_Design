import pandas as pd

FILE_PATH = "data/schneider_extracted_raw.csv"

df = pd.read_csv(FILE_PATH)

print("\n================================")
print("SCHNEIDER DATA INSPECTION")
print("================================")

print("\nTotal rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

print("\nRows containing LC-:")
matches = df[
    df.astype(str)
      .apply(
          lambda row: row.str.contains(
              "LC-",
              case=False,
              na=False
          ).any(),
          axis=1
      )
]

print(
    matches.to_string(index=True)
)

print("\nRows containing LRD-:")
matches = df[
    df.astype(str)
      .apply(
          lambda row: row.str.contains(
              "LRD-",
              case=False,
              na=False
          ).any(),
          axis=1
      )
]

print(
    matches.to_string(index=True)
)
