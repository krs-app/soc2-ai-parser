# soc2_parser.py
import fitz
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
import streamlit as st

def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "".join([page.get_text() for page in doc])
    except Exception as e:
        return f"[ERROR] {e}"

def extract_soc2_summary(file, prepare_only=False, on_chunk=None):
    text = extract_text_from_pdf(file)
    if text.startswith("[ERROR]"):
        return {"Error": text}

    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=500)
    chunks = splitter.split_text(text)

    if prepare_only:
        return {"Total Chunks": len(chunks)}

    llm = ChatOpenAI(model="gpt-4", temperature=0)
    summary = {
        "Auditor": "",
        "Time Period": "",
        "Scope": "",
        "Exceptions": [],
        "Tags": [],
        "System Description": [],
        "Status Counts": {"Passed": 0, "Passed with Exception": 0, "Excluded": 0},
        "Total Chunks": len(chunks),
        "Failed Chunks": 0
    }
    tags_set = set()
    chunk_errors = []

    def process_chunk(i_chunk):
        if on_chunk:
            on_chunk(i_chunk)
        chunk = chunks[i_chunk]
        prompt = f"""
        Extract as JSON:
        - Auditor
        - Time Period
        - Scope
        - Exceptions (Control, Exception, Response)
        - Tags
        - System Description
        - Status Counts: Passed, Passed with Exception, Excluded
        Return valid JSON only.
        Text:
        {chunk}
        """
        try:
            res = llm([HumanMessage(content=prompt)]).content.strip()
            res = res.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(res[res.find("{"):])
            return parsed
        except Exception as e:
            chunk_errors.append(f"Chunk {i_chunk+1}: {str(e)}")
            return None

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(process_chunk, range(len(chunks))))

    for result in results:
        if not result:
            summary["Failed Chunks"] += 1
            continue

        summary["Auditor"] = summary["Auditor"] or result.get("Auditor", "")
        summary["Time Period"] = summary["Time Period"] or result.get("Time Period", "")
        summary["Scope"] = summary["Scope"] or result.get("Scope", "")
        summary["Exceptions"] += result.get("Exceptions", [])
        tags_set.update(result.get("Tags", []))
        summary["System Description"] += result.get("System Description", [])

        for k in summary["Status Counts"]:
            summary["Status Counts"][k] += int(result.get("Status Counts", {}).get(k, 0))

    summary["Tags"] = list(tags_set)
    summary["System Description"] = list(set(summary["System Description"]))

    if chunk_errors:
        summary["Error"] = "\n".join(chunk_errors)

    return summary
