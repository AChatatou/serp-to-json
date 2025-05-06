from bs4 import BeautifulSoup
import re
import os


def clean_serp_html(html_content):
    """
    Clean a search engine result page HTML, removing unnecessary elements
    while preserving important search result content.

    Args:
        html_content (str): Raw HTML content of a SERP

    Returns:
        str: Cleaned HTML containing only essential SERP information
    """
    # Create BeautifulSoup object for parsing
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script, style and other non-essential elements
    for element in soup.select('script, style, iframe, noscript, svg, img[width="1"], meta, link'):
        element.decompose()

    # Remove tracking pixels, hidden inputs, etc.
    for element in soup.find_all(['img', 'input']):
        # Remove tiny images (likely tracking pixels)
        if element.name == 'img' and element.has_attr('width') and element.has_attr('height'):
            try:
                if (int(element['width']) < 5 or int(element['height']) < 5):
                    element.decompose()
            except (ValueError, TypeError):
                pass

        # Remove hidden inputs
        if element.name == 'input' and element.get('type') == 'hidden':
            element.decompose()

    # Remove empty elements and unnecessary attributes
    for element in soup.find_all(True):
        # Keep only essential attributes for search results analysis
        allowed_attrs = ['href', 'src', 'alt', 'title', 'class', 'id']
        attrs = dict(element.attrs)
        for attr in attrs:
            if attr not in allowed_attrs:
                del element[attr]

        # Clean href attributes from tracking parameters
        if element.has_attr('href'):
            href = element['href']
            # Clean Google redirect URLs
            if href.startswith('/url?') or 'google' in href and 'url=' in href:
                match = re.search(r'[?&](?:q|url)=([^&]+)', href)
                if match:
                    element['href'] = match.group(1)

            # Remove tracking parameters
            if '?' in href:
                base_url = href.split('?')[0]
                params = href.split('?')[1].split('&')
                # Keep only non-tracking parameters (simplified approach)
                clean_params = [p for p in params if
                                not any(t in p.lower() for t in ['utm_', 'ref=', 'track', 'click'])]
                if clean_params:
                    element['href'] = base_url + '?' + '&'.join(clean_params)
                else:
                    element['href'] = base_url

    # Find and preserve search result containers
    # Common selectors for major search engines
    selectors = [
        'div.g', 'div.rc', 'li.b_algo', 'div.result', 'div.algo',  # Standard results
        'div.related-question', 'div.knowledge-panel',  # Knowledge panels
        'div.bkWMgd', 'div.ULSxyf', 'div#search',  # Google containers
        'ol#b_results', 'div#results', 'div#web'  # Bing/Yahoo/DDG containers
    ]

    # Try to identify and preserve the main content area
    main_content = None
    for selector in selectors:
        candidates = soup.select(selector)
        if candidates:
            if not main_content or len(str(candidates[0])) > len(str(main_content)):
                container = candidates[0].parent
                while container and container.name != 'body' and len(container.find_all('a')) < 5:
                    container = container.parent

                if container and container.name != 'body':
                    main_content = container
                    break

    # If we found a main content area, isolate it
    if main_content:
        # Preserve search box if present
        search_box = soup.select_one('form[action*="search"]') or soup.select_one('input[name="q"]')

        # Create new document with just the essential elements
        new_soup = BeautifulSoup('<html><head><title></title></head><body></body></html>', 'html.parser')

        # Copy the title
        if soup.title:
            new_soup.title.string = soup.title.string

        # Add search box if found
        if search_box:
            new_soup.body.append(search_box)

        # Add main content
        new_soup.body.append(main_content)

        # Replace original soup
        soup = new_soup
    else:
        # Fallback: remove known noisy sections
        for noise_section in soup.select('footer, header, nav, aside, [role="complementary"], [role="navigation"]'):
            noise_section.decompose()

    # Final cleanup - remove empty elements
    for element in soup.find_all():
        if not element.get_text(strip=True) and not element.find_all(['img', 'input']) and element.name not in ['br',
                                                                                                                'hr']:
            if not (element.name == 'a' and element.has_attr('href')):  # Keep links with hrefs
                element.decompose()

    # Generate clean HTML
    clean_html = soup.prettify()


    return clean_html


def clean_serp_html_file(input_file, output_file=None):
    """
    Clean a SERP HTML file and save the result

    Args:
        input_file (str): Path to the input HTML file
        output_file (str, optional): Path to save the cleaned HTML output
                                    (defaults to input_file_clean.html)

    Returns:
        str: Path to the output file
    """
    # Set default output file if not specified
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_clean{ext}"

    # Read the input file
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()

    # Clean the HTML
    clean_html = clean_serp_html(html_content)

    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(clean_html)

    return output_file


# Example usage
if __name__ == "__main__":
    # Example using the function on a file
    input_file = "sample_serp.html"
    output_file = clean_serp_html_file(input_file)
    print(f"Cleaned HTML saved to {output_file}")