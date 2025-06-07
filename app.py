import streamlit as st
import time
from datetime import datetime
from soc2_parser import extract_soc2_summary

st.set_page_config(page_title="SOC 2 Parser", layout="wide")
st.title("SOC 2 Parser")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False
        st.session_state.start_time = None
        st.session_state.end_time = None
        st.session_state.total_chunks = None
        st.session_state.time_taken = None
        st.session_state.summary = None

    if st.button("Start Analysis"):
        st.session_state.analysis_started = True
        st.session_state.start_time = datetime.now()
        st.session_state.end_time = None
        st.session_state.total_chunks = None
        st.session_state.time_taken = None
        st.session_state.summary = None
        st.experimental_rerun()

    if st.session_state.analysis_started:
        st.write(f"**Start Time:** {st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write("**Total Chunks Identified:** Detecting...")
        st.write("**End Time:** Pending...")
        st.write("**Time Taken:** Pending...")

        with st.spinner("Processing..."):
            summary = extract_soc2_summary(uploaded_file)

            st.session_state.end_time = datetime.now()
            st.session_state.time_taken = st.session_state.end_time - st.session_state.start_time
            st.session_state.total_chunks = summary.get("Total Chunks", "N/A")
            st.session_state.summary = summary

        st.write(f"**Total Chunks Identified:** {st.session_state.total_chunks}")
        st.write(f"**End Time:** {st.session_state.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        minutes, seconds = divmod(st.session_state.time_taken.total_seconds(), 60)
        st.write(f"**Time Taken:** {int(minutes)} minutes {int(seconds)} seconds")

        st.subheader("Summary Insights")
        st.json(st.session_state.summary)
