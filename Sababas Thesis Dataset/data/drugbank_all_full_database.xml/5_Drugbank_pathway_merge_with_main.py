import pandas as pd

# Load your main database and pathways data
main_df = pd.read_csv("drug_data_cleaned/main_database_with_properties.csv",low_memory=False)
pathways_df = pd.read_csv("drug_data_cleaned/pathways.csv")

# Fill NA with empty strings to avoid join/agg errors
pathways_df.fillna("", inplace=True)

# Group pathway info by primary_drugbank_id
pathway_summary = pathways_df.groupby("primary_drugbank_id").agg({
    "pathway_smpdb_id": "count",
    "pathway_category": lambda x: ",".join(set([i.strip() for i in x if i])),
    "pathway_enzymes": lambda x: len(set(",".join(x).replace(" ", "").split(","))) if x.any() else 0
}).reset_index()

# Rename columns for clarity
pathway_summary.rename(columns={
    "pathway_smpdb_id": "pathway_count",
    "pathway_category": "unique_pathway_categories",
    "pathway_enzymes": "unique_enzyme_count"
}, inplace=True)

# Add flag column
pathway_summary["has_pathway_info"] = 1

# Merge into main dataframe
merged_df = main_df.merge(pathway_summary, how="left", on="primary_drugbank_id")

# Fill missing values for drugs that had no pathway entry
merged_df["pathway_count"] = merged_df["pathway_count"].fillna(0).astype(int)
merged_df["unique_enzyme_count"] = merged_df["unique_enzyme_count"].fillna(0).astype(int)
merged_df["has_pathway_info"] = merged_df["has_pathway_info"].fillna(0).astype(int)
merged_df["unique_pathway_categories"] = merged_df["unique_pathway_categories"].fillna("")

# Save the merged file
merged_df.to_csv("drug_data_cleaned/main_database_with_properties_and_pathways.csv", index=False)
print("✅ Merged pathway data into 'drug_data_cleaned/main_database_with_properties_and_pathways.csv'")
