import pandas as pd
import re

# Load the interaction file
df = pd.read_csv("drug_data_cleaned/drug_interactions.csv", dtype=str)
df = df.fillna("")

# Merge in the actual names of DRUG_A from main_database if needed
main = pd.read_csv("drug_data_cleaned/main_database_with_properties.csv", usecols=["primary_drugbank_id", "name"])
id2name = dict(zip(main["primary_drugbank_id"], main["name"]))

# Function to clean description using DRUG_A and DRUG_B placeholders
def normalize_description(row):
    desc = row["description"]
    drug_a_id = row["primary_drugbank_id"]
    drug_b_name = row["name"]

    # Try to get the actual name of the primary drug
    drug_a_name = id2name.get(drug_a_id, "")

    # Remove both names from the description
    desc = re.sub(re.escape(drug_a_name), "DRUG_A", desc, flags=re.IGNORECASE)
    desc = re.sub(re.escape(drug_b_name), "DRUG_B", desc, flags=re.IGNORECASE)
    
    return desc.strip()

# Apply function to get interaction template
df["interaction_template"] = df.apply(normalize_description, axis=1)

# Encode to integer labels
df["interaction_type"] = df["interaction_template"].astype("category").cat.codes

# Save updated version
df.to_csv("drug_data_cleaned/drug_interactions_encoded.csv", index=False)

print("✅ Template normalization complete.")
print(df[["primary_drugbank_id", "drugbank_id", "interaction_template", "interaction_type"]].head(10))
