import pandas as pd
import numpy as np
import re
import hashlib
import os
from collections import defaultdict
import shutil
from typing import List, Dict, Tuple, Union

# Extracting Float
def extract_float(text):
    if pd.isna(text): return None
    text = str(text)
    match = re.findall(r"[-+]?\d*\.\d+|\d+", text.replace("Â", "").replace("â", ""))
    try:
        return sum(float(x) for x in match) / len(match) if match else None
    except ValueError:
        return None

# Boiling Point
def extract_boiling_point(value):
    if pd.isna(value):
        return None
    value = str(value)
    # Find numbers with optional decimal
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", value)
    try:
        # Convert to float if numbers exist and are valid
        valid = [float(m) for m in matches if m.strip() not in [".", ""]]
        if valid:
            return sum(valid) / len(valid)  # return average if range or multiple
    except ValueError:
        pass
    return None

# Isoelectric Point
def extract_isoelectric_point(value):
    if pd.isna(value):
        return None
    value = str(value).lower()
    if "no distinct" in value or "does not" in value:
        return None
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", value)
    try:
        nums = [float(x) for x in matches if x.strip() not in [".", ""]]
        return np.mean(nums) if nums else None
    except:
        return None

# Melting Point
def extract_melting_point(value):
    if pd.isna(value):
        return None
    value = str(value).lower()
    if "decompose" in value:
        return None
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", value)
    try:
        nums = [float(x) for x in matches if x.strip() not in [".", ""]]
        return np.mean(nums) if nums else None
    except:
        return None

# Water Solubility
def extract_water_solubility(value):
    if pd.isna(value):
        return None
    value = str(value).lower()
    if "insoluble" in value or "practically insoluble" in value:
        return 0.0
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", value)
    try:
        nums = [float(x) for x in matches if x.strip() not in [".", ""]]
        if "mg/ml" in value:
            return nums[0] * 1.0 if nums else None
        elif "mg/l" in value:
            return nums[0] / 1000.0 if nums else None
        elif "g/l" in value:
            return nums[0]
        else:
            return np.mean(nums)  # fallback
    except:
        return None

# pKa
def extract_pka(value):
    if pd.isna(value):
        return None
    value = str(value).lower()
    if "strongest acidic" in value or "strongest basic" in value or "not available" in value:
        return None
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", value)
    try:
        nums = [float(x) for x in matches if x.strip() not in [".", ""]]
        return np.mean(nums) if nums else None
    except:
        return None

# SMILES (Encode to fixed-length hash/embedding)
def encode_smiles(smile):
    if pd.isna(smile): return None
    return int(hashlib.sha256(smile.encode()).hexdigest(), 16) % (10**8)  # 8-digit hash

# SMILE
def extract_smiles_features(smiles):
    if pd.isna(smiles) or not isinstance(smiles, str):
        return pd.Series({
            "smiles_length": 0,
            "smiles_num_branches": 0,
            "smiles_num_rings": 0,
            "smiles_num_aromatic": 0,
        })
    return pd.Series({
        "smiles_length": len(smiles),
        "smiles_num_branches": smiles.count("("),
        "smiles_num_rings": sum(smiles.count(x) for x in "123456789"),
        "smiles_num_aromatic": sum(smiles.count(x) for x in "cnops"),
    })

# Main feature extraction function for toxicity text
def extract_toxicity_features(text: str) -> Dict[str, Union[bool, str, float, List, Dict]]:
    if pd.isna(text) or not isinstance(text, str):
        return {
            "tox_tested_animals": [],
            "tox_dose_by_route": {},
            "observed_effects": [],
            "tox_threshold_by_species": {},
            "mutagenic_or_carcinogenic": None,
            "ld50_values": [],
            "human_toxicity_notes": [],
            "overdose_treatment": False,
            "adverse_effect_frequency": None,
            "special_population_caution": [],
            "tox_ref_ids": []
        }

    animals = re.findall(r"\b(mouse|mice|rat|rats|monkey|monkeys|dog|dogs|rabbit|rabbits|hamster|hamsters)\b", text, re.I)
    tox_tested_animals = list(set([a.lower().rstrip('s') for a in animals]))

    routes = ['intravenous', 'subcutaneous', 'oral', 'topical', 'intramuscular']
    tox_dose_by_route = {}
    for route in routes:
        pattern = rf"{route}.*?\b(?:in|of)?\s?(mice|rats|monkeys|dogs|rabbits|hamsters)[^\.]*?\((?:[><]\s*)?(\d+\.?\d*)(?:\s*-\s*(\d+\.?\d*))?\s*mg/kg(?:\s*[><])?\)"
        matches = re.findall(pattern, text, re.I)
        for animal, low, high in matches:
            animal = animal.lower().rstrip('s')
            if high:
                tox_dose_by_route.setdefault(route, []).append((animal, float(low), float(high)))
            else:
                tox_dose_by_route.setdefault(route, []).append((animal, float(low), "unspecified"))

    observed_effects = re.findall(r"(hemorrhage|hematoma|nodule|fever|rash|dyspnea|chest pain|urticaria|conjunctivitis|voice alteration|pharyngitis|laryngitis|rhinitis)", text, re.I)
    observed_effects = list(set([e.lower() for e in observed_effects]))

    threshold_matches = re.findall(r"(\d+\.?\d*)\s*mg/kg.*?(mouse|mice|rat|rats|monkey|monkeys)", text, re.I)
    tox_threshold_by_species = {}
    for dose, species in threshold_matches:
        species = species.lower().rstrip('s')
        dose = float(dose)
        tox_threshold_by_species[species] = min(dose, tox_threshold_by_species.get(species, float("inf")))

    mutagenicity = None
    if re.search(r"not.*mutagenic", text, re.I):
        mutagenicity = "non-mutagenic"
    elif re.search(r"mutagenic", text, re.I):
        mutagenicity = "mutagenic"
    if re.search(r"not.*carcinogenic", text, re.I):
        mutagenicity = mutagenicity or "non-carcinogenic"
    elif re.search(r"carcinogenic", text, re.I):
        mutagenicity = mutagenicity or "carcinogenic"

    ld50_matches = re.findall(r"(mouse|mice|rat|rats|monkey|monkeys).*?LD<sub>50</sub>.*?([><=])\s*(\d+\.?\d*)\s*mg/kg", text, re.I)
    ld50_values = [(sp.lower().rstrip('s'), "unspecified", float(val), comp) for sp, comp, val in ld50_matches]

    overdose_phrases = re.findall(r"(stop.*?lepirudin|transfusion|shock|aPTT|hemodialysis|hemofiltration)", text, re.I)
    overdose_treatment = bool(overdose_phrases)

    human_toxicity = []
    for sentence in re.split(r"(?<=[.])\s+", text):
        if any(word in sentence.lower() for word in ["renal impairment", "antidote", "bleeding", "transfusion", "aPTT"]):
            human_toxicity.append(sentence.strip())

    adverse_effect_freq = None
    freq_match = re.search(r"frequency.*?(<\s*1/\d+|\d+\s*%)", text, re.I)
    if freq_match:
        adverse_effect_freq = freq_match.group(1)

    special_population = []
    for pop in ["pregnant women", "nursing women", "children", "elderly"]:
        if pop in text.lower():
            special_population.append(pop)

    ref_ids = list(set(re.findall(r"\[L\d+\]", text)))

    return {
        "tox_tested_animals": tox_tested_animals,
        "tox_dose_by_route": tox_dose_by_route,
        "observed_effects": observed_effects,
        "tox_threshold_by_species": tox_threshold_by_species,
        "mutagenic_or_carcinogenic": mutagenicity,
        "ld50_values": ld50_values,
        "human_toxicity_notes": human_toxicity,
        "overdose_treatment": overdose_treatment,
        "adverse_effect_frequency": adverse_effect_freq,
        "special_population_caution": special_population,
        "tox_ref_ids": ref_ids
    }

# Implementation
df = pd.read_csv("drug_data_cleaned/main_database_with_properties_and_pathways.csv",low_memory=False)

# Apply feature cleaners
df["Boiling Point"] = df["Boiling Point"].apply(extract_boiling_point)
df["Melting Point"] = df["Melting Point"].apply(extract_melting_point)
df["Isoelectric Point"] = df["Isoelectric Point"].apply(extract_isoelectric_point)
df["Water Solubility (g/L)"] = df["Water Solubility"].apply(lambda x: extract_float(x) if "mg" in str(x) or "g" in str(x) else None)
df["pKa"] = df["pKa"].apply(extract_pka)
tox_features_df = df['toxicity'].apply(extract_toxicity_features).apply(pd.Series)
df = pd.concat([df, tox_features_df], axis=1)

# SMILES encoding and structural feature extraction
df["SMILES_hash"] = df["SMILES"].apply(encode_smiles)
smiles_features = df["SMILES"].apply(extract_smiles_features)
df = pd.concat([df, smiles_features], axis=1)

# (Optional) Drop the original messy columns
df.drop(columns=[col for col in ["Water Solubility"] if col in df.columns], inplace=True)

df.to_csv("drug_data_cleaned/main_database_cleaned_and_encoded.csv", index=False)
print("✅ Cleaned and saved: main_database_cleaned_and_encoded.csv")

# Source and destination folders
source_folder = "drug_data_cleaned"
destination_folder = "Drugbank_final_database"

# Create the destination folder if it doesn't exist
os.makedirs(destination_folder, exist_ok=True)

# Files you want to move
files_to_move = [
    "main_database_cleaned_and_encoded.csv",
    "drug_interactions_encoded.csv"
]

# Move files one by one
for file_name in files_to_move:
    src_path = os.path.join(source_folder, file_name)
    dst_path = os.path.join(destination_folder, file_name)

    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        print(f"✅ Moved '{file_name}' to '{destination_folder}'")
    else:
        print(f"❌ File not found: {src_path}")