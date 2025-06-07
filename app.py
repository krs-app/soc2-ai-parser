import streamlit as st
from soc2_parser import extract_soc2_info

st.set_page_config(page_title="SOC 2 Report AI Parser", layout="wide")

st.title("🔍 SOC 2 Report Parser using AI")
st.markdown("Upload a SOC 2 PDF report to extract key audit insights like auditor, scope, exceptions, encryption & backup practices.")

uploaded_file = st.file_uploader("📄 Upload SOC 2 PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing the report with AI..."):
        results = extract_soc2_info(uploaded_file)

    st.success("✅ Extracted Insights")

    for key, value in results.items():
        st.markdown(f"### {key}")
        st.markdown(value)
