from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random

# Set up headless Chrome
options = Options()
options.headless = True
options.add_argument("--disable-blink-features=AutomationControlled") 
options.add_argument("--incognito")  # Use incognito mode
driver = webdriver.Chrome(options=options)

# List of search queries
queries = [
    # Image & Video Carousels
    "sunset photography ideas",
    "how to tie a tie",
    "cat videos",
    "interior design living room ideas",
    "wedding dress styles 2025",
]


# Base Google search URL
base_url = "https://www.google.com/search?q="

# Set to store unique attributes
attributes_set = set()

# Final results 
xray_values = set()

for query in queries:
    search_url = base_url + query.replace(" ", "+")
    driver.get(search_url)
    
    # Random delay between requests (in seconds)
    delay = random.uniform(5, 8)
    time.sleep(delay)


    print(driver.page_source[:500]) 

    # Parse the HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Count all tags in the parsed HTML (For debugging)
    all_tags = soup.find_all(True)  # Finds all tags
    print(f"Total number of tags parsed: {len(all_tags)}")

    # Iterate through all tags in the parsed HTML
    for tag in all_tags:  # True means find all tags
        # Extract the tag's attributes (if any)
        for attribute in tag.attrs:
            # Add each attribute to the set (set ensures no duplicates)
            attributes_set.add(attribute)


    # Find all elements with xray-json-path attribute
    found = soup.find_all(attrs={"xray-json-path": True})


    values = [tag["xray-json-path"] for tag in found]

    print(values)

    # Store results
    xray_values.update(values)
# Close browser
driver.quit()

print(xray_values)


attributes_list = list(attributes_set)
# Print the number of unique attributes found
print(f"Found {len(attributes_list)} unique attributes")
# Write the attributes to a file (for example, in a plain text file)
with open("attributes.txt", "w") as file:
    for attribute in attributes_list:
        file.write(f"{attribute}\n")

# Writing the unique xray-json-path values to a text file
with open('xray_json_paths.txt', 'w') as file:
    for path in xray_values:
        file.write(path + '\n')
