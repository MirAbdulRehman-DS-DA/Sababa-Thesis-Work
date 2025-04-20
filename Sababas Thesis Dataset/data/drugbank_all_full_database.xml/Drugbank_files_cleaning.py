import pandas as pd

#-----------------------------
####### Cleaning The main.database.csv file and removing unncecssary empty rows

# Load CSV file
file_path = "drug_data/main_database.csv"
df = pd.read_csv(file_path)

# Drop rows where the first three columns are empty
df_cleaned = df.dropna(subset=df.columns[:3], how="all")

# Save the cleaned data back to CSV
output_path = "drug_data_cleaned/main_database.csv"
df_cleaned.to_csv(output_path, index=False)

print(f"Cleaned (main_database.csv) saved as '{output_path}'")
#-----------------------------

#-----------------------------
####### Cleaning The drug_categories.csv file and removing unncecssary empty rows all fo the rows where mis ID is mpty

# Load CSV file
file_path = "drug_data/drug_categories.csv"
df = pd.read_csv(file_path)

# Drop rows where the first three columns are empty
df_cleaned = df.dropna(subset=df.columns[2], how="all")

# Save the cleaned data back to CSV
output_path = "drug_data_cleaned/drug_categories.csv"
df_cleaned.to_csv(output_path, index=False)

print(f"Cleaned (drug_categories.csv) saved as '{output_path}'")
#-----------------------------

#-----------------------------
####### Bring the remaining datafiles to the new folder

# Load CSV file - drug_interactions
file_path = "drug_data/drug_interactions.csv"
df = pd.read_csv(file_path)

# Save data back to CSV
output_path = "drug_data_cleaned/drug_interactions.csv"
df.to_csv(output_path, index=False)

#-----------------------------------------

# Load CSV file - experimental_properties
file_path = "drug_data/experimental_properties.csv"
df = pd.read_csv(file_path)

# Save data back to CSV
output_path = "drug_data_cleaned/experimental_properties.csv"
df.to_csv(output_path, index=False)

#-----------------------------------------

# Load CSV file - pathways.csv
file_path = "drug_data/pathways.csv"
df = pd.read_csv(file_path)

# Save data back to CSV
output_path = "drug_data_cleaned/pathways.csv"
df.to_csv(output_path, index=False)