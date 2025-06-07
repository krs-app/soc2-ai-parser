import streamlit as st
from soc2_parser import extract_soc2_summary

st.set_page_config(page_title="SOC 2 Report Parser", layout="wide")
st.title("🔍 SOC 2 Report Parser (AI-powered)")

uploaded_file = st.file_uploader("Upload a SOC 2 PDF report", type="pdf")

if uploaded_file:
    with st.spinner("Processing the report..."):
        summary = extract_soc2_summary(uploaded_file)

    st.success("Report parsed successfully!")
    st.subheader("Extracted Summary:")

    for key, value in summary.items():
        st.markdown(f"**{key}**: {value}")
