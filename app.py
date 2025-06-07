import streamlit as st
from soc2_parser import extract_soc2_info

st.set_page_config(page_title="SOC 2 Parser", layout="centered")

st.title("🔍 SOC 2 Report Parser (AI-Powered)-1")
st.write("Upload a SOC 2 PDF report and get structured insights using AI.")

uploaded_file = st.file_uploader("📄 Upload SOC 2 PDF", type="pdf")

if uploaded_file:
    with st.spinner("Reading and analyzing the document..."):
        results = extract_soc2_info(uploaded_file)

    st.success("✅ Extracted Insights:")
    for key, value in results.items():
        st.subheader(key)
        st.write(value)
