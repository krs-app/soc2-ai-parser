import streamlit as st
import matplotlib.pyplot as plt
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

        # ---------- CONTROL STATUS CHART ----------
        st.divider()
        st.subheader("✅ Control Result Summary")
        status_counts = result.get("Status Counts", {})
        
        # Safe parse for chart values
        def safe_int(val):
            try:
                return int(val)
            except:
                return 0
        
        passed = safe_int(status_counts.get("Passed"))
        exceptions = safe_int(status_counts.get("Passed with Exception"))
        excluded = safe_int(status_counts.get("Excluded"))
        
        if passed + exceptions + excluded == 0:
            st.warning("No control summary data available.")
        else:
            fig, ax = plt.subplots(figsize=(5, 5))  # Smaller figure size
        
            wedges, texts, autotexts = ax.pie(
                [passed, exceptions, excluded],
                labels=["Passed", "Passed with Exception", "Excluded"],
                autopct=lambda pct: f"{pct:.1f}% ({int(round(pct/100 * (passed + exceptions + excluded)))})",
                startangle=140,
                wedgeprops={'width': 0.4},
                textprops=dict(color="black", fontsize=10)
            )
            ax.axis("equal")
        
            # Move legend outside
            ax.legend(wedges, ["Passed", "Passed with Exception", "Excluded"],
                      title="Status",
                      loc="center left",
                      bbox_to_anchor=(1, 0.5),
                      fontsize=9)
        
            st.pyplot(fig)

            st.markdown(
                f"""
                <style>
                .badge-container {{ display: flex; gap: 1rem; margin-top: 1rem; }}
                .badge {{ padding: 0.5rem 1rem; border-radius: 10px; color: white; font-weight: bold; }}
                .pass {{ background-color: #4CAF50; }}
                .warn {{ background-color: #FFA500; }}
                .fail {{ background-color: #FF4444; }}
                </style>
                <div class="badge-container">
                    <div class="badge pass">✔️ Passed: {status_counts.get('Passed', 0)}</div>
                    <div class="badge warn">⚠️ With Exceptions: {status_counts.get('Passed with Exception', 0)}</div>
                    <div class="badge fail">❌ Excluded: {status_counts.get('Excluded', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------- EXCEPTIONS ----------
        st.divider()
        st.subheader("⚠️ Notable Exceptions")
        exceptions = result.get("Exceptions", [])
        if exceptions:
            with st.expander("View detailed exceptions and management responses"):
                for ex in exceptions:
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
