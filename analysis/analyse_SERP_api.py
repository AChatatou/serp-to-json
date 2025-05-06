import os
import json
import re
from bs4 import BeautifulSoup

# Folder with preprocessed HTML files
html_folder = "/Users/adilc/Documents/Uni/S7_SS25/BSc/data"

# Dictionary: xray-json-path value → set of full HTML strings
xray_elements = {}
ids = []

# Process each HTML file in the folder
for filename in os.listdir(html_folder):
    if filename.endswith(".html"):
        file_path = os.path.join(html_folder, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            html = file.read()
            soup = BeautifulSoup(html, "html.parser")

            # Find tags with the xray-json-path attribute
            tags = soup.find_all(attrs={"xray-json-path": True})
            for tag in tags:
                xray_value = tag["xray-json-path"]
                full_html = str(tag)

                if xray_value not in xray_elements:
                    xray_elements[xray_value] = set()
                xray_elements[xray_value].add(full_html)

            # Collect all tags that have an id attribute
            for tag in soup.find_all():
                if tag.has_attr("id"):
                    ids.append({
                        "tag": tag.name,
                        "id": tag["id"]
                    })

# Convert sets to lists for JSON serialization
xray_json_ready = {key: list(value) for key, value in xray_elements.items()}

# Write to a JSON file
with open("xray_elements.json", "w", encoding="utf-8") as json_file:
    json.dump(xray_json_ready, json_file, indent=2, ensure_ascii=False)

print(f"Saved full xray-tagged HTML elements to 'xray_elements.json'")

# Normalize keys by removing numeric indices like [0], [1] → []
normalized_keys = set()
for key in xray_elements.keys():
    normalized_key = re.sub(r"\[\d+\]", "[]", key)
    normalized_keys.add(normalized_key)

# Save normalized xray-json-path values to a text file
with open("xray_keys.txt", "w", encoding="utf-8") as txt_file:
    for key in sorted(normalized_keys):
        txt_file.write(f"{key}\n")

print("Saved normalized xray-json-path keys to 'xray_keys.txt'")

# Convert list of dicts to a set of tuples to remove duplicates
unique_ids = {(item['tag'], item['id']) for item in ids}

with open("ids.txt", "w", encoding="utf-8") as id_file:
    for tag, id_value in sorted(unique_ids):
        id_file.write(f"{tag}: {id_value}\n")

print("saved ids")