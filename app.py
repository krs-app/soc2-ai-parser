import streamlit as st
from soc2_parser import extract_soc2_summary

st.set_page_config(page_title="SOC 2 Report Parser", layout="wide")
st.title("🔍 SOC 2 Report Parser (AI-powered)")

uploaded_file = st.file_uploader("Upload a SOC 2 PDF report", type="pdf")

if uploaded_file:
    with st.spinner("Processing the report..."):
        result = extract_soc2_summary(uploaded_file)

    if "Error" in result:
        st.error(result["Error"])
    else:
        st.success("Report parsed successfully!")

        # ---------- CORE FIELDS ----------
        st.subheader("📝 Extracted Summary")
        st.markdown(f"**Auditor:** {result.get('Auditor', 'N/A')}")
        st.markdown(f"**Time Period:** {result.get('Time Period', 'N/A')}")
        st.markdown(f"**Scope:** {result.get('Scope', 'N/A')}")

        # ---------- CONTROL STATUS VISUAL BAR ----------
        st.divider()
        st.subheader("✅ Control Result Summary")
        status_counts = result.get("Status Counts", {})

        # Safe int conversion
        def safe_int(val):
            try:
                return int(val)
            except:
                return 0

        passed = safe_int(status_counts.get("Passed"))
        exceptions = safe_int(status_counts.get("Passed with Exception"))
        excluded = safe_int(status_counts.get("Excluded"))

        st.markdown(
            f"""
            <style>
            .status-bar {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin: 10px 0;
            }}
            .status-pill {{
                padding: 8px 14px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                font-size: 15px;
            }}
            .green-pill {{ background-color: #4CAF50; }}
            .orange-pill {{ background-color: #FFA500; }}
            .red-pill {{ background-color: #FF4444; }}
            </style>

            <div class="status-bar">
                <div class="status-pill green-pill">✔️ Passed: {passed}</div>
                <div class="status-pill orange-pill">⚠️ With Exceptions: {exceptions}</div>
                <div class="status-pill red-pill">❌ Excluded: {excluded}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------- EXCEPTIONS ----------
        st.divider()
        st.subheader("⚠️ Notable Exceptions")
        exceptions_list = result.get("Exceptions", [])
        if exceptions_list:
            with st.expander("View detailed exceptions and management responses"):
                for ex in exceptions_list:
                    st.markdown(f"""
- **Control:** {ex.get('Control', 'N/A')}  
  🔸 **Exception:** {ex.get('Exception', 'N/A')}  
  🗣️ **Response:** {ex.get('Response', 'N/A')}
""")
        else:
            st.markdown("*No notable exceptions reported.*")

        # ---------- TAGS ----------
        st.divider()
        st.subheader("🔍 Risk & Focus Tags")
        tags = result.get("Tags", [])
        if tags:
            tag_html = ""
            for tag in tags:
                tag_html += f"<span style='background-color:#ffb703; color:black; padding:6px 10px; border-radius:8px; margin-right:6px;'>{tag}</span>"
            st.markdown(tag_html, unsafe_allow_html=True)
        else:
            st.markdown("*No tags extracted.*")

        # ---------- SYSTEM DESCRIPTION ----------
        st.divider()
        st.subheader("🧾 System Description Summary")
        sys_desc = result.get("System Description", [])
        if sys_desc:
            for bullet in sys_desc:
                st.markdown(f"- {bullet}")
        else:
            st.markdown("*No system summary available.*")
