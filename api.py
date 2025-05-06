import streamlit as st
import json

from modules.html_cleaner import clean_html
from modules.html_to_json import extract_serp

st.title("HTML to JSON Processor")

uploaded_file = st.file_uploader("Upload an HTML file", type=["html"])

if uploaded_file is not None:
    # Step 1: Read uploaded file
    html_content = uploaded_file.read().decode("utf-8")
    
    # Step 2: Clean HTML
    cleaned_html = clean_html(html_content)
    st.subheader("Cleaned HTML")
    st.code(cleaned_html, language="html")
    
    # Step 3: Map to JSON
    mapped_json = extract_serp(cleaned_html)
    st.subheader("Mapped JSON")
    st.json(mapped_json)

    # Step 4: Offer JSON for download
    json_string = json.dumps(mapped_json, indent=2)
    st.download_button(
        label="Download JSON",
        data=json_string,
        file_name="output.json",
        mime="application/json"
    )
