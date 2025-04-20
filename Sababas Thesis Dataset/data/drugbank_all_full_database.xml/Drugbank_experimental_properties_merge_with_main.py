import pandas as pd

# Load both CSV files
exp_props = pd.read_csv("drug_data_cleaned/experimental_properties.csv")
main_db = pd.read_csv("drug_data_cleaned/main_database.csv")

# Drop source column
exp_props = exp_props.drop(columns=['source'])

# Drop molecular_weight column
if 'molecular_weight' in main_db.columns:
    main_db = main_db.drop(columns=['molecular_weight'])

# Pivot the experimental_properties table
pivoted_props = exp_props.pivot_table(
    index='primary_drugbank_id',
    columns='kind',
    values='value',
    aggfunc='first'  # If multiple values exist, pick the first
).reset_index()

# Merge with main_database on primary_drugbank_id
merged = pd.merge(main_db, pivoted_props, on="primary_drugbank_id", how="left")

# Save to a new CSV
merged.to_csv("drug_data_cleaned/main_database_with_properties.csv", index=False)

print("✅ Merged successfully! Output file: main_database_with_properties.csv")

#--------------
# counting how many drugs have complete data.


# Load the merged dataset
df = pd.read_csv("drug_data_cleaned/main_database_with_properties.csv")

# Count complete rows (no NaN values at all)
complete_rows = df.dropna().shape[0]
total_rows = df.shape[0]

print(f"✅ Complete rows (no missing values): {complete_rows}")
print(f"🧮 Total rows: {total_rows}")
print(f"📉 Percentage of complete rows: {100 * complete_rows / total_rows:.2f}%")