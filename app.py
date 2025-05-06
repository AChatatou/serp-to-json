import streamlit as st
import json
import os

from modules.html_cleaner import clean_serp_html
from modules.html_to_json import extract_serp

# Streamlit app UI
st.title("HTML to JSON Converter")

# Upload HTML file
uploaded_file = st.file_uploader("Upload an HTML file", type="html")


if uploaded_file is not None:
    # Step 1: Read uploaded file
    html_content = uploaded_file.read().decode("utf-8")

    # Step 2: Clean HTML
    cleaned_html = clean_serp_html(html_content)
    st.subheader("Cleaned HTML")
    # st.code(cleaned_html, language="html")
    # Provide a download button for the cleaned HTML
    st.download_button(
        label="Download Clean HTML",
        data=cleaned_html,
        file_name="cleaned_html.html",
        mime="text/html"
    )
    
    # Step 3: Map to JSON
    # mapped_json = html_to_json(cleaned_html)
    mapped_json = extract_serp(html_content)
    st.subheader("Mapped JSON")
    st.json(mapped_json)

    # Step 4: Offer JSON for download
    json_output = json.dumps(mapped_json, indent=2)

    # Get the original file name without extension
    base_filename = os.path.splitext(uploaded_file.name)[0]

    # Set the JSON filename based on uploaded HTML file name
    json_filename = f"{base_filename}.json"

    # Provide a download button for the JSON
    st.download_button(
        label="Download JSON",
        data=json_output,
        file_name=json_filename,
        mime="application/json"
    )
