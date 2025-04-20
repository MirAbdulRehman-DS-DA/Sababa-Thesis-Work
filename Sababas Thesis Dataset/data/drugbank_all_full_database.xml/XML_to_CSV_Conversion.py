import xml.etree.ElementTree as ET
import csv

def extract_drugbank_ids_and_names(xml_file, csv_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Prepare data for CSV
    data = []
    
    # Iterate over each drug element
    for drug in root.findall('.//{http://www.drugbank.ca}drug'):
        drugbank_ids = [id_elem.text for id_elem in drug.findall('{http://www.drugbank.ca}drugbank-id[@primary="true"]')]
        name = drug.find('{http://www.drugbank.ca}name').text
        
        for drugbank_id in drugbank_ids:
            data.append([drugbank_id, name])
    
    # Write data to CSV with UTF-8 encoding
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['DrugBank ID', 'Name'])
        writer.writerows(data)

# Example usage
xml_file = 'full database.xml'
csv_file = 'drugbank_ids_and_names.csv'
extract_drugbank_ids_and_names(xml_file, csv_file)
print(f'DrugBank IDs and names have been extracted to {csv_file}')