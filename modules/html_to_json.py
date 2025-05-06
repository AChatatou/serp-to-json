import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

def extract_serp(html_content: str) -> Dict[str, Any]:
    """
    Extract structured data from a Search Engine Result Page HTML
    
    Args:
        html_content: HTML content of the SERP page
        
    Returns:
        Dictionary containing structured SERP data
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    main_search_results = soup.select_one('#rso')
    footer = soup.select_one('#botstuff')
    
    serp_data = {
        "search_metadata": extract_metadata(soup),
        "organic_results": extract_organic_results(main_search_results),
        "related_searches": extract_related_searches(soup),
        "related_questions": extract_related_questions(soup),
        "knowledge_graph": extract_knowledge_graph(soup),
        #"answer_box": extract_answer_box(soup),
        #"ads": extract_ads(soup),
        #"local_results": extract_local_results(soup),
        "top_stories": extract_top_stories(soup),
        "images": extract_images(soup),
        "videos": extract_videos(soup),
        #"pagination": extract_pagination(soup),
    }
    
    # Remove None or empty values
    serp_data = {k: v for k, v in serp_data.items() if v}
    
    return serp_data




def extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract search metadata including query and engine info"""
    metadata = {
        "status": "success",
        "engine": "google",  # Default to Google, adjust as needed
        "title": soup.title.string if soup.title else None,
        "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Can be filled with current timestamp
    }
    

    return metadata

def extract_organic_results(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract main organic search results"""
    organic_results = []
    results = soup.select('div.vt6azd.Ww4FFb')
    position = 0
    print(f"found {len(results)} results")

    for result in (results):
        snippet_tag = result.select_one('div.VwiC3b, div.tZESfb')
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
        highlighted_words = [em.get_text(strip=True) for em in snippet_tag.select('em')] if snippet_tag else []

        date_tag = snippet_tag.select_one('.YrbPuc span') if snippet_tag else None
        date = date_tag.get_text(strip=True) if date_tag else None

        source = result.select_one('span.VuuXrf, span.pKWwCd, div.GkAmnd, div.ZaCDgb')
        #link = result.select_one('a.rTyHce, a.cz3goc, a.jgWGIe, a.OcpZAb, a.zReHs')
        link = result.select_one('a')
        displayed_link = result.select_one('cite.qLRx3b.tjvcx, span.nC62wb.VndCse.z8gr9e')
        title = result.select_one('h3, div.F0FGWb, div.ynAwRc, div.MBeuO, div.v7jaNc')

        sitelinks_inline = [
            {
                "title": tag.get_text(strip=True),
                "link": tag['href']
            }
            for tag in result.select('a.dM1Yyd') if tag.has_attr('href')
        ]

        # Expanded sitelinks (desktop style)
        sitelinks_expanded = []
        for item in result.select('div.usJj9c'):
            a_tag = item.select_one('h3 > a')
            snippet_inner = item.select_one('div.zz3gNc')
            if a_tag and a_tag.has_attr('href'):
                sitelinks_expanded.append({
                    "title": a_tag.get_text(strip=True),
                    "link": a_tag['href'],
                    "snippet": snippet_inner.get_text(strip=True) if snippet_inner else ""
                })

        # Expanded sitelinks (mobile style) 
        for a_tag in result.select('a.ynAwRc'):
            if a_tag.has_attr('href'):
                sitelinks_expanded.append({
                    "title": a_tag.get_text(strip=True),
                    "link": a_tag['href'],
                    #"snippet": None
                })

        source_text = source.get_text(strip=True) if source else ""
        title_text = title.get_text(strip=True) if title else ""
        link_href = link['href'] if link and link.has_attr('href') else ""
        displayed_link_text = displayed_link.get_text(strip=True) if displayed_link else ""

        if source_text and title_text and link_href:
            position += 1
            organic_results.append({
                "position": position,
                "source": source_text,
                "title": title_text,
                "date": date,
                "link": link_href,
                "displayed_link": displayed_link_text,
                "redirect_link": (
                    "https://www.google.com" + link['ping']
                    if link and link.has_attr('ping')
                    else ""
                ),
                "snippet": snippet,
                "snippet_highlighted_words": highlighted_words,
                "sitelinks_inline": sitelinks_inline,
                "sitelinks_expanded": sitelinks_expanded
            })

    return organic_results

def extract_sitelinks(element: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract sitelinks from a result block"""
    sitelinks = []
    
    # Sitelinks container selector (may need adjustment)
    sitelinks_elements = element.select('.sitelinks-list a, .mCBkyc a')
    
    for link in sitelinks_elements:
        sitelink = {}

    
    return sitelinks


def extract_related_searches(soup: BeautifulSoup) -> List[List[Dict[str, Any]]]:
    """Extract related search queries (People also search for)."""
    
    people_also_search_list = []

    pasf_blocks = soup.select('div.oIk2Cb, div.AuVD')
    for block in pasf_blocks:
        items = block.select('a')
        for item in items:
            name = item.get_text(strip=True, separator=" ")
            if not name:
                for sibling in item.next_siblings:
                    if isinstance(sibling, str):
                        continue  # skip text nodes
                    # Check if sibling is a tag and contains a span at any depth
                    span = sibling.find('span')
                    if span:
                        name = span.get_text(strip=True, separator=" ")
                        break  # stop after finding the first matching sibling

            people_also_search_list.append({
                "name": name,
                "link": item['href']
            })


    return people_also_search_list


def extract_related_questions(soup: BeautifulSoup) -> List[str]:
    """Extract related questions (People Also ask)"""
    related_questions = []

    paa_blocks = soup.select('div[jsname="yEVEwb"]')
    for block in paa_blocks:
        span = block.find('span')
        if span:
            related_questions.append(span.get_text(strip=True))
   
    return related_questions



def extract_knowledge_graph(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract knowledge graph information if present"""
    knowledge_graph = {}
    
    # Main knowledge graph container
    kg_element = soup.select_one('.kp-wholepage, .knowledge-panel')
    if not kg_element:
        return None
    
    # Extract title
    title = kg_element.select_one('h2, .garHBe')
    if title:
        knowledge_graph["title"] = title.text.strip()
    
    # Extract type/category
    category = kg_element.select_one('.wwUB2c, .QIclbb')
    if category:
        knowledge_graph["type"] = category.text.strip()
    
    # Extract description
    description = kg_element.select_one('.kno-rdesc span')
    if description:
        knowledge_graph["description"] = description.text.strip()
    
    # Extract attributes (key-value pairs)
    attributes = {}
    attribute_rows = kg_element.select('.rVusze, .Z1hOCe')
    
    for row in attribute_rows:
        key_element = row.select_one('.w8qArf, .QIclbb')
        value_element = row.select_one('.LrzXr, .kno-fv')
        
        if key_element and value_element:
            key = key_element.text.strip().rstrip(':')
            value = value_element.text.strip()
            attributes[key] = value
    
    if attributes:
        knowledge_graph["attributes"] = attributes
    
    return knowledge_graph

def extract_answer_box(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract featured snippet/answer box"""
    answer_box = {}
    
    # Featured snippet container
    snippet_element = soup.select_one('.xpdopen, .c2xzTb, .g.mnr-c.g-blk')
    if not snippet_element:
        return None
    
    # Extract title
    title = snippet_element.select_one('h3, .LC20lb')
    if title:
        answer_box["title"] = title.text.strip()
    
    # Extract answer text
    answer = snippet_element.select_one('.hgKElc, .X5LH0c, .LGOjhe')
    if answer:
        answer_box["snippet"] = answer.text.strip()
    
    # Extract source
    source = snippet_element.select_one('cite, .iUh30')
    if source:
        answer_box["source"] = source.text.strip()
    
    # Extract link
    link = snippet_element.select_one('a')
    if link and link.has_attr('href'):
        href = link['href']
        if href.startswith('/url?'):
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            if 'q' in query_params:
                answer_box["link"] = query_params['q'][0]
        else:
            answer_box["link"] = href
    
    return answer_box

def extract_ads(soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
    """Extract advertisement results"""
    ads = {"top": [], "bottom": []}
    
    # Top ads
    top_ads_container = soup.select_one('#tads')
    if top_ads_container:
        ad_elements = top_ads_container.select('.uEierd')
        for i, element in enumerate(ad_elements):
            ad = {"position": i + 1}
            
            title_el = element.select_one('h3')
            if title_el:
                ad["title"] = title_el.text.strip()
            
            link_el = element.select_one('a')
            if link_el and link_el.has_attr('href'):
                ad["link"] = link_el['href']
            
            displayed_link = element.select_one('.qzEoUe')
            if displayed_link:
                ad["displayed_link"] = displayed_link.text.strip()
            
            snippet = element.select_one('.MUxGbd')
            if snippet:
                ad["snippet"] = snippet.text.strip()
            
            ads["top"].append(ad)
    
    # Bottom ads
    bottom_ads_container = soup.select_one('#bottomads')
    if bottom_ads_container:
        ad_elements = bottom_ads_container.select('.uEierd')
        for i, element in enumerate(ad_elements):
            ad = {"position": i + 1}
            
            title_el = element.select_one('h3')
            if title_el:
                ad["title"] = title_el.text.strip()
            
            link_el = element.select_one('a')
            if link_el and link_el.has_attr('href'):
                ad["link"] = link_el['href']
            
            displayed_link = element.select_one('.qzEoUe')
            if displayed_link:
                ad["displayed_link"] = displayed_link.text.strip()
            
            snippet = element.select_one('.MUxGbd')
            if snippet:
                ad["snippet"] = snippet.text.strip()
            
            ads["bottom"].append(ad)
    
    # Remove empty lists
    if not ads["top"]:
        del ads["top"]
    if not ads["bottom"]:
        del ads["bottom"]
    
    return ads if ads else None

def extract_local_results(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract local map results"""
    local_results = []
    
    # Local results container
    local_pack = soup.select_one('#lu_map, .AEprdc, .MkUM6e')
    if not local_pack:
        return None
    
    # Extract places
    place_elements = local_pack.select('.VkpGBb, .cXedhc')
    
    for i, element in enumerate(place_elements):
        place = {"position": i + 1}
        
        # Extract name
        name = element.select_one('.dbg0pd, .OSrXXb')
        if name:
            place["title"] = name.text.strip()
        
        # Extract address
        address = element.select_one('.rllt__details [role="img"], .rllt__details .BTPx6e')
        if address:
            place["address"] = address.text.strip()
        
        # Extract rating
        rating_element = element.select_one('span.BTtC6e')
        if rating_element:
            rating_text = rating_element.text.strip()
            rating_match = re.search(r'([\d.]+)', rating_text)
            if rating_match:
                place["rating"] = float(rating_match.group(1))
                
            # Extract review count
            reviews_match = re.search(r'\(([\d,]+)\)', rating_text)
            if reviews_match:
                place["reviews"] = reviews_match.group(1).replace(',', '')
        
        # Extract link
        link = element.select_one('a.yYlJEf, a.cXedhc')
        if link and link.has_attr('href'):
            place["link"] = link['href']
        
        if place.get("title"):
            local_results.append(place)
    
    return local_results


def extract_top_stories(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract news/top stories results"""
    stories = []
    
    # News container
    news_container = soup.select_one('#rso > div:has(.mCBkyc)')
    if not news_container:
        return None
    
    # Extract news items
    news_elements = news_container.select('.WlydOe')
    
    for i, element in enumerate(news_elements):
        story = {"position": i + 1}
        
        # Extract title
        title = element.select_one('div.mCBkyc')
        if title:
            story["title"] = title.text.strip()
        
        # Extract source
        source = element.select_one('.CEMjEf')
        if source:
            story["source"] = source.text.strip()
        
        # Extract published time
        time_element = element.select_one('span.OSrXXb')
        if time_element:
            story["time"] = time_element.text.strip()
        
        # Extract link
        link = element.select_one('a')
        if link and link.has_attr('href'):
            href = link['href']
            if href.startswith('/url?'):
                parsed_url = urlparse(href)
                query_params = parse_qs(parsed_url.query)
                if 'q' in query_params:
                    story["link"] = query_params['q'][0]
            else:
                story["link"] = href
        
        # Extract thumbnail
        thumbnail = element.select_one('img')
        if thumbnail and thumbnail.has_attr('src'):
            story["thumbnail"] = thumbnail['src']
        
        if story.get("title") or story.get("link"):
            stories.append(story)
    
    return stories

def extract_images(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract image results"""
    images = []

    image_blocks = soup.select('#iur, .bCOlv.yMbVTb')
    for block in image_blocks:
        for image_block in block.select('.w43QB.EXH1Ce, .DyfMyc'):
            link_tag = image_block.select_one('a')
            img_tag = image_block.select_one('img')

            link = link_tag.get('href') if link_tag else None
            image_description = img_tag.get('alt', "") if img_tag else ""
            image_src = img_tag.get('src') or img_tag.get('data-src') if img_tag else None

            images.append({
                "image_text": image_description,
                "link": link,
                "source": image_src
            })

    return images


def extract_videos(soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
    """Extract video results"""
    video_list = []
    short_video_list = []

    # Inline videos
    videos = soup.select('.sHEJob')
    for video in videos:
        link_tag = video.select_one('a')
        link = link_tag.get('href') if link_tag else None

        first_div, second_div = None, None
        try:
            next_div = link_tag.find_next('div')
            divs = next_div.find_all('div', recursive=False)
            if len(divs) >= 2:
                first_div, second_div = divs[0], divs[1]
        except Exception:
            pass

        title = first_div.get_text(strip=True) if first_div else ""
        

        videos_metadata = second_div.get_text(strip=True, separator=";") if second_div else ""

        if len(videos_metadata) >=4:
            metadata = videos_metadata.split(";")
            source = metadata[0] + " . " +  metadata[2]
            date = metadata[-1]


        video_list.append({
            "title": title,
            "link": link,
            "source": source  ,
            "date": date if date else None
        })

    """
    # Short videos
    short_videos = soup.select('div.oj7Mub.eVNxY, .T19leb')
    for short_video in short_videos:
        link_tag = short_video.select_one('a')
        title_tag = short_video.select_one('.bXckjb')
        source_tag = short_video.select_one('.RLbKnXb.YAG2qc.DMUiif')

        link = link_tag['href'] if link_tag else None
        title = title_tag.get_text(strip=True) if title_tag else ""
        source = source_tag.get_text(strip=True, separator=" ") if source_tag else ""

        short_video_list.append({
            "title": title,
            "link": link,
            "source": source
        })
    """
    """
    return {
        "inline_videos": video_list,
        "short_videos": short_video_list
    }
    """
    return video_list


def extract_pagination(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract pagination information"""
    pagination = {}

    
    return pagination

# Example usage
def parse_serp_from_file(html_file_path):
    """Parse SERP from an HTML file and return structured JSON"""
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    serp_data = extract_serp(html_content)
    return json.dumps(serp_data, indent=2, ensure_ascii=False)

# Uncomment to use with a file
# if __name__ == "__main__":
#     result = parse_serp_from_file("path/to/serp.html")
#     print(result)