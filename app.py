import streamlit as st
from soc2_parser import extract_soc2_summary
import matplotlib.pyplot as plt

st.set_page_config(page_title="SOC 2 AI Parser", layout="wide")
st.title("🔍 SOC 2 Report Analyzer (AI-Powered)")

uploaded_file = st.file_uploader("Upload SOC 2 PDF report", type="pdf")

if uploaded_file:
    with st.spinner("Analyzing the document with GPT..."):
        result = extract_soc2_summary(uploaded_file)

    if "Error" in result:
        st.error("⚠️ Some chunks could not be parsed.")
        st.code(result["Error"])

    st.subheader("📊 Summary Insights")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Auditor:** {result.get('Auditor', '')}")
        st.markdown(f"**Time Period:** {result.get('Time Period', '')}")
        st.markdown(f"**Scope:** {result.get('Scope', '')}")

        st.markdown("**Tags Identified:**")
        st.markdown(", ".join(result.get("Tags", [])))

        st.markdown("**System Description:**")
        for item in result.get("System Description", []):
            st.markdown(f"- {item}")

        st.markdown("**Exceptions Found:**")
        for ex in result.get("Exceptions", []):
            with st.expander(f"🔸 {ex['Control']}"):
                st.markdown(f"**Exception:** {ex['Exception']}")
                st.markdown(f"**Response:** {ex['Response']}")

    with col2:
        st.markdown("**Control Status Summary:**")
        status_counts = result.get("Status Counts", {})
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())

        fig, ax = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontsize": 8},
            wedgeprops={'width': 0.5}
        )
        ax.axis("equal")
        st.pyplot(fig)

    st.caption(
        f"📄 Processed {result.get('Total Chunks', '?')} chunks"
        + (f", {result.get('Failed Chunks', 0)} failed to parse." if result.get("Failed Chunks", 0) > 0 else ".")
    )
