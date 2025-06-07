import fitz  # PyMuPDF
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"[ERROR] Failed to read PDF: {e}"

def extract_soc2_summary(file):
    raw_text = extract_text_from_pdf(file)
    if raw_text.startswith("[ERROR]"):
        return {"Error": raw_text}

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_text(raw_text)

    llm = ChatOpenAI(model="gpt-4", temperature=0)

    all_exceptions = []
    tags_set = set()
    system_bullets = []
    summary_info = {
        "Auditor": "",
        "Time Period": "",
        "Scope": "",
        "Status Counts": {"Passed": 0, "Passed with Exception": 0, "Excluded": 0}
    }

    chunk_errors = []

    for i, chunk in enumerate(chunks[:5]):  # Adjust number of chunks as needed

        # Skip low-signal text chunks (too small or mostly headers)
        if len(chunk.strip()) < 300 or chunk.lower().count("section") > 4:
            continue

        prompt = f"""
        You are a SOC 2 compliance analyst.

        Read the following SOC 2 report chunk and extract these fields:
        - Auditor name and firm
        - Audit time period
        - Scope of audit
        - Notable Exceptions: each with Control, Exception, Response
        - Risk or focus tags (e.g., Encryption, Access Control)
        - System description (3–5 bullet points)
        - Control status summary with: Passed, Passed with Exception, Excluded

        Return output in valid JSON only. Do not include any explanations or formatting.

        {{
            "Auditor": "...",
            "Time Period": "...",
            "Scope": "...",
            "Exceptions": [{{"Control": "...", "Exception": "...", "Response": "..."}}],
            "Tags": ["...", "..."],
            "System Description": ["...", "..."],
            "Status Counts": {{"Passed": X, "Passed with Exception": Y, "Excluded": Z}}
        }}

        Text:
        {chunk}
        """

        try:
            response = llm([HumanMessage(content=prompt)])
            chunk_text = response.content.strip()

            # Clean and pre-process output
            chunk_text = chunk_text.encode("utf-8", "ignore").decode().strip()
            if not chunk_text or len(chunk_text) < 5:
                chunk_errors.append(f"Chunk {i+1}: Empty or invalid response")
                continue

            # Remove triple backticks
            if chunk_text.startswith("```json") or chunk_text.startswith("```"):
                chunk_text = chunk_text.replace("```json", "").replace("```", "").strip()

            # Remove intro text before first {
            json_start = chunk_text.find("{")
            if json_start > 0:
                chunk_text = chunk_text[json_start:]

            chunk_result = json.loads(chunk_text)

            # Merge into master summary
            if not summary_info["Auditor"]:
                summary_info["Auditor"] = chunk_result.get("Auditor", "")
            if not summary_info["Time Period"]:
                summary_info["Time Period"] = chunk_result.get("Time Period", "")
            if not summary_info["Scope"]:
                summary_info["Scope"] = chunk_result.get("Scope", "")

            all_exceptions += chunk_result.get("Exceptions", [])
            tags_set.update(chunk_result.get("Tags", []))
            system_bullets += chunk_result.get("System Description", [])

            for k in summary_info["Status Counts"]:
                try:
                    summary_info["Status Counts"][k] += int(chunk_result.get("Status Counts", {}).get(k, 0))
                except:
                    continue

        except Exception as e:
            chunk_errors.append(f"Chunk {i+1}: {str(e)}")
            continue

    summary_info["Exceptions"] = all_exceptions
    summary_info["Tags"] = list(tags_set)
    summary_info["System Description"] = list(set(system_bullets))

    if chunk_errors:
        summary_info["Error"] = (
            f"{len(chunk_errors)} chunk(s) failed to parse:\n" + "\n".join(chunk_errors)
        )

    return summary_info
