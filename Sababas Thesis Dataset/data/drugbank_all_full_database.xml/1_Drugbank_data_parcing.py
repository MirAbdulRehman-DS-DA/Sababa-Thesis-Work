import xml.etree.ElementTree as ET
import csv
import os

def extract_drug_data(xml_file, output_folder):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Prepare data for main database CSV
    main_data = []
    
    # Prepare data for drug interactions CSV
    drug_interactions_data = []
    
    # Prepare data for drug categories CSV
    drug_categories_data = []
    
    # Prepare data for experimental properties CSV
    experimental_properties_data = []
    
    # Prepare data for pathways CSV
    pathway_data = []
    
    # Iterate over each drug element
    for drug in root.findall('.//{http://www.drugbank.ca}drug'):
        drug_info = {}
        
        # Extract basic drug information
        drug_info['type'] = drug.attrib.get('type')
        drug_info['created'] = drug.attrib.get('created')
        drug_info['primary_drugbank_id'] = drug.find('{http://www.drugbank.ca}drugbank-id[@primary="true"]').text if drug.find('{http://www.drugbank.ca}drugbank-id[@primary="true"]') is not None else None
        drug_info['name'] = drug.find('{http://www.drugbank.ca}name').text if drug.find('{http://www.drugbank.ca}name') is not None else None
        drug_info['description'] = drug.find('{http://www.drugbank.ca}description').text if drug.find('{http://www.drugbank.ca}description') is not None else None
        drug_info['cas_number'] = drug.find('{http://www.drugbank.ca}cas-number').text if drug.find('{http://www.drugbank.ca}cas-number') is not None else None
        drug_info['unii'] = drug.find('{http://www.drugbank.ca}unii').text if drug.find('{http://www.drugbank.ca}unii') is not None else None
        drug_info['state'] = drug.find('{http://www.drugbank.ca}state').text if drug.find('{http://www.drugbank.ca}state') is not None else None
        
        # Extract groups information
        groups = [group.text for group in drug.findall('.//{http://www.drugbank.ca}group')]
        drug_info['groups'] = ','.join(groups)
        
        # Extract other tags information
        tags_to_extract = [
            'synthesis-reference', 'indication', 'pharmacodynamics', 'mechanism-of-action', 'toxicity',
            'metabolism', 'absorption', 'half-life', 'protein-binding', 'route-of-elimination',
            'volume-of-distribution', 'clearance'
        ]
        
        for tag in tags_to_extract:
            element = drug.find(f'.//{{http://www.drugbank.ca}}{tag}')
            drug_info[tag] = element.text if element is not None else None
        
        # Extract classification information
        classification_tags_to_extract = [
            'description', 'direct-parent', 'kingdom', 'superclass', 'class', 'subclass'
        ]
        
        for tag in classification_tags_to_extract:
            classification_tag = f'classification_{tag}'
            element = drug.find(f'.//{{http://www.drugbank.ca}}{tag}')
            drug_info[classification_tag] = element.text if element is not None else None
        
        # Extract affected organisms information
        affected_organisms = [org.text for org in drug.findall('.//{http://www.drugbank.ca}affected-organism')]
        drug_info['affected_organisms'] = ','.join(affected_organisms)
        
        # Extract food interactions information
        food_interactions = [food.text for food in drug.findall('.//{http://www.drugbank.ca}food-interaction')]
        drug_info['food_interactions'] = ','.join(food_interactions)
        
        # Extract sequence information (updated)
        sequences_element = drug.find('.//{http://www.drugbank.ca}sequence')
        if sequences_element is not None:
            sequence_text = sequences_element.text.strip()
            sequence_format = sequences_element.attrib.get('format')
            sequence_value = f"{sequence_format}: {sequence_text}" if sequence_format else sequence_text
            drug_info['sequence'] = sequence_value
        else:
            drug_info['sequence'] = None
                
        # Extract molecular weight information (excluding targets)
        molecular_weights = [mw.text for mw in drug.findall('.//{http://www.drugbank.ca}molecular-weight')]
        
        if len(molecular_weights) == 1:
            drug_info['molecular_weight'] = molecular_weights[0]
        else:
            drug_info['molecular_weight'] = ''
        
        # Add extracted data to main database list
        main_data.append(drug_info)
        
        # Extract and add data to experimental properties list
        for prop in drug.findall('.//{http://www.drugbank.ca}property'):
            experimental_properties_data.append({
                'primary_drugbank_id': drug_info['primary_drugbank_id'],
                'kind': prop.find('{http://www.drugbank.ca}kind').text if prop.find('{http://www.drugbank.ca}kind') is not None else None,
                'value': prop.find('{http://www.drugbank.ca}value').text if prop.find('{http://www.drugbank.ca}value') is not None else None,
                'source': prop.find('{http://www.drugbank.ca}source').text if prop.find('{http://www.drugbank.ca}source') is not None else None
            })
        
        # Extract and add data to pathways list (excluding drugs)
        for pathway in drug.findall('.//{http://www.drugbank.ca}pathway'):
            pathway_data.append({
                'primary_drugbank_id': drug_info['primary_drugbank_id'],
                'pathway_smpdb_id': pathway.find('{http://www.drugbank.ca}smpdb-id').text if pathway.find('{http://www.drugbank.ca}smpdb-id') is not None else None,
                'pathway_name': pathway.find('{http://www.drugbank.ca}name').text if pathway.find('{http://www.drugbank.ca}name') is not None else None,
                'pathway_category': pathway.find('{http://www.drugbank.ca}category').text if pathway.find('{http://www.drugbank.ca}category') is not None else None,
                'pathway_enzymes': pathway.find('{http://www.drugbank.ca}enzymes').text if pathway.find('{http://www.drugbank.ca}enzymes') is not None else None
            })
        
        # Extract and add data to categories list (including primary_drugbank_id)
        for category in drug.findall('.//{http://www.drugbank.ca}category'):
            drug_categories_data.append({
                'primary_drugbank_id': drug_info['primary_drugbank_id'],
                'category': category.find('{http://www.drugbank.ca}category').text if category.find('{http://www.drugbank.ca}category') is not None else None,
                'mesh_id': category.find('{http://www.drugbank.ca}mesh-id').text if category.find('{http://www.drugbank.ca}mesh-id') is not None else None
            })
        
        # Extract and add data to drug interactions list
        for interaction in drug.findall('.//{http://www.drugbank.ca}drug-interaction'):
            drug_interactions_data.append({
                'primary_drugbank_id': drug_info['primary_drugbank_id'],
                'drugbank_id': interaction.find('{http://www.drugbank.ca}drugbank-id').text if interaction.find('{http://www.drugbank.ca}drugbank-id') is not None else None,
                'name': interaction.find('{http://www.drugbank.ca}name').text if interaction.find('{http://www.drugbank.ca}name') is not None else None,
                'description': interaction.find('{http://www.drugbank.ca}description').text if interaction.find('{http://www.drugbank.ca}description') is not None else None
            })
        
    # Write main database CSV file
    main_csv_file = os.path.join(output_folder, 'main_database.csv')
    with open(main_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=main_data[0].keys())
        writer.writeheader()
        writer.writerows(main_data)
    
    # Write experimental properties CSV file
    experimental_properties_csv_file = os.path.join(output_folder, 'experimental_properties.csv')
    with open(experimental_properties_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=experimental_properties_data[0].keys())
        writer.writeheader()
        writer.writerows(experimental_properties_data)
    
    # Write pathways CSV file
    pathways_csv_file = os.path.join(output_folder, 'pathways.csv')
    with open(pathways_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=pathway_data[0].keys())
        writer.writeheader()
        writer.writerows(pathway_data)
    
    # Write categories CSV file
    categories_csv_file = os.path.join(output_folder, 'drug_categories.csv')
    with open(categories_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=drug_categories_data[0].keys())
        writer.writeheader()
        writer.writerows(drug_categories_data)
    
    # Write drug interactions CSV file
    drug_interactions_csv_file = os.path.join(output_folder, 'drug_interactions.csv')
    with open(drug_interactions_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=drug_interactions_data[0].keys())
        writer.writeheader()
        writer.writerows(drug_interactions_data)

# Example usage
xml_file = 'full database.xml'
output_folder = 'drug_data'
extract_drug_data(xml_file, output_folder)
print(f'Data has been extracted to the folder: {output_folder}')