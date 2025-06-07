import streamlit as st
import time
from datetime import datetime
from soc2_parser import split_text_into_chunks, process_chunks

st.set_page_config(page_title="SOC 2 Parser", layout="wide")

st.title("SOC 2 Parser")

uploaded_file = st.file_uploader("Upload a TXT, PDF, or DOCX file", type=["txt", "pdf", "docx"])

if uploaded_file:
    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False
        st.session_state.start_time = None
        st.session_state.end_time = None
        st.session_state.total_chunks = None
        st.session_state.time_taken = None

    if st.button("Start Analysis"):
        st.session_state.analysis_started = True
        st.session_state.start_time = datetime.now()
        st.session_state.end_time = None
        st.session_state.total_chunks = None
        st.session_state.time_taken = None

        st.experimental_rerun()

    if st.session_state.analysis_started:
        with st.spinner("Processing..."):
            start_time = st.session_state.start_time
            st.write(f"**Start Time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write("**Total Chunks Identified:** Detecting...")
            st.write("**End Time:** Pending...")
            st.write("**Time Taken:** Pending...")

            file_contents = uploaded_file.read()
            chunks = split_text_into_chunks(file_contents)
            total_chunks = len(chunks)
            st.session_state.total_chunks = total_chunks

            # Update Total Chunks
            st.write(f"**Total Chunks Identified:** {total_chunks}")

            results = process_chunks(chunks)

            # End time and total time
            end_time = datetime.now()
            st.session_state.end_time = end_time
            time_taken = end_time - start_time
            st.session_state.time_taken = time_taken

            st.write(f"**End Time:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            minutes, seconds = divmod(time_taken.total_seconds(), 60)
            st.write(f"**Time Taken:** {int(minutes)} minutes {int(seconds)} seconds")

            st.subheader("Summary Insights")
            for i, res in enumerate(results):
                st.markdown(f"**Chunk {i+1}**")
                st.write(res)
