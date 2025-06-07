# app.py
import streamlit as st
from soc2_parser import extract_soc2_summary
import matplotlib.pyplot as plt
import time
from datetime import datetime

st.set_page_config(page_title="SOC 2 AI Parser", layout="wide")
st.title("🔍 SOC 2 Report Analyzer (AI-Powered)")

if "stop_processing" not in st.session_state:
    st.session_state.stop_processing = False
if "processed_chunks" not in st.session_state:
    st.session_state.processed_chunks = 0

uploaded_file = st.file_uploader("Upload SOC 2 PDF report", type="pdf")

if uploaded_file:
    if st.button("⏳ Start Analysis"):
        st.session_state.stop_processing = False
        st.session_state.processed_chunks = 0
        start_time = time.time()
        start_dt = datetime.now()
        st.markdown(f"**Start Time:** {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        with st.spinner("Reading and preparing document chunks..."):
            pre_result = extract_soc2_summary(uploaded_file, prepare_only=True)
            total_chunks = pre_result.get("Total Chunks", "?")
            st.session_state.total_chunks = total_chunks

        st.markdown(f"**Total Chunks Identified:** {total_chunks}")
        progress = st.empty()
        placeholder = st.empty()
        time_placeholder = st.empty()
        stop_btn = st.button("🛑 Stop")

        chunk_progress = st.empty()

        uploaded_file.seek(0)  # Reset the file pointer before reusing

        with st.spinner("Processing chunks with GPT-4..."):
            def on_chunk(index):
                st.session_state.processed_chunks += 1
                chunk_progress.markdown(f"📦 Processed {st.session_state.processed_chunks} / {total_chunks} chunks")

            result = extract_soc2_summary(uploaded_file, on_chunk=on_chunk)

        end_time = time.time()
        end_dt = datetime.now()
        elapsed = round(end_time - start_time)
        minutes, seconds = divmod(elapsed, 60)

        st.success("✅ Analysis Complete")
        st.markdown(f"**End Time:** {end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**Time Taken:** {minutes} min {seconds} sec")

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
