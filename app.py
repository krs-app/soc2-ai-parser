# app.py
import streamlit as st
from soc2_parser import extract_soc2_summary
import matplotlib.pyplot as plt
from datetime import datetime
import time

st.set_page_config(page_title="SOC 2 AI Parser", layout="wide")
st.title("🔍 SOC 2 Report Analyzer (AI-Powered)")

if "result" not in st.session_state:
    st.session_state.result = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = None
if "meta_displayed" not in st.session_state:
    st.session_state.meta_displayed = False

uploaded_file = st.file_uploader("Upload SOC 2 PDF report", type="pdf")

if uploaded_file:
    if st.session_state.result:
        st.session_state.result = None
        st.session_state.start_time = None
        st.session_state.end_time = None
        st.session_state.elapsed = None
        st.session_state.meta_displayed = False
        st.experimental_rerun()

    if st.button("⏳ Start Analysis"):
        st.session_state.start_time = datetime.now()
        start_unix = time.time()

        # Placeholder display immediately after clicking button
        st.subheader("📌 Processing Details")
        st.markdown(f"**Start Time:** {st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**Total Chunks Identified:** _Loading..._")
        st.markdown(f"**End Time:** _Pending..._")
        st.markdown(f"**Time Taken:** _Pending..._")

        with st.spinner("Analyzing the document with GPT..."):
            result = extract_soc2_summary(uploaded_file)

        st.session_state.result = result
        st.session_state.end_time = datetime.now()
        st.session_state.elapsed = round(time.time() - start_unix)
        st.session_state.meta_displayed = True
        st.experimental_rerun()

if st.session_state.result:
    result = st.session_state.result

    if not st.session_state.meta_displayed:
        st.subheader("📌 Processing Details")
        st.markdown(f"**Start Time:** {st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.start_time else '_'}")
        st.markdown(f"**Total Chunks Identified:** {result.get('Total Chunks', '?')}")
        st.markdown(f"**End Time:** {st.session_state.end_time.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.end_time else '_'}")

        if st.session_state.elapsed is not None:
            minutes, seconds = divmod(st.session_state.elapsed, 60)
            st.markdown(f"**Time Taken:** {minutes} min {seconds} sec")
        else:
            st.markdown("**Time Taken:** _")

    st.subheader("📊 Summary Insights")

    if "Error" in result:
        st.error("⚠️ Some chunks could not be parsed.")
        st.code(result["Error"])

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Auditor:** {result.get('Auditor', '')}")
        st.markdown(f"**Time Period:** {result.get('Time Period', '')}")
        st.markdown(f"**Scope:** {result.get('Scope', '')}")

        st.markdown("**Tags Identified:**")
        tags = result.get("Tags", [])
        if tags:
            st.markdown(", ".join(tags))
        else:
            st.markdown("_No tags identified._")

        st.markdown("**System Description:**")
        desc = result.get("System Description", [])
        if isinstance(desc, list):
            for item in desc:
                if isinstance(item, str) and item.strip():
                    st.markdown(f"- {item.strip()}")
        elif isinstance(desc, str):
            st.markdown(f"- {desc.strip()}")
        else:
            st.markdown("_No system description found._")

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
