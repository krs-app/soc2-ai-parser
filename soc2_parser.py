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

    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    chunks = splitter.split_text(raw_text)
    total_chunks = len(chunks)

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

    for i, chunk in enumerate(chunks):
        prompt = f"""
        You are a SOC 2 compliance analyst.

        If the input chunk has no relevant content (e.g. table of contents, glossary, definitions), return this exact JSON:
        {{
            "Exceptions": [],
            "Tags": [],
            "System Description": [],
            "Status Counts": {{"Passed": 0, "Passed with Exception": 0, "Excluded": 0}},
            "Auditor": "",
            "Time Period": "",
            "Scope": ""
        }}

        Otherwise, extract:
        - Auditor name and firm
        - Audit time period
        - Scope of audit
        - Notable Exceptions: each with Control, Exception, Response
        - Risk or focus tags (e.g., Encryption, Access Control)
        - System description (3–5 bullet points)
        - Control status summary with: Passed, Passed with Exception, Excluded

        Return output in valid JSON only. Do not include any explanation or formatting.

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

            # Retry once if empty
            if not chunk_text or len(chunk_text) < 30:
                response = llm([HumanMessage(content=prompt)])
                chunk_text = response.content.strip()

            chunk_text = chunk_text.encode("utf-8", "ignore").decode().strip()

            if not chunk_text or len(chunk_text) < 5:
                chunk_errors.append(f"Chunk {i+1}: Empty or invalid response")
                continue

            if chunk_text.startswith("```json") or chunk_text.startswith("```"):
                chunk_text = chunk_text.replace("```json", "").replace("```", "").strip()

            json_start = chunk_text.find("{")
            if json_start > 0:
                chunk_text = chunk_text[json_start:]

            chunk_result = json.loads(chunk_text)

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
            chunk_errors.append(
                f"Chunk {i+1}: {str(e)}\n--- Raw GPT Output ---\n{response.content[:500]}\n--- Cleaned Text ---\n{chunk_text[:500]}"
            )
            continue

    summary_info["Exceptions"] = all_exceptions
    summary_info["Tags"] = list(tags_set)
    summary_info["System Description"] = list(set(system_bullets))
    summary_info["Total Chunks"] = total_chunks
    summary_info["Failed Chunks"] = len(chunk_errors)

    if chunk_errors:
        summary_info["Error"] = (
            f"{len(chunk_errors)} chunk(s) failed to parse:\n" + "\n\n".join(chunk_errors)
        )

    return summary_info
