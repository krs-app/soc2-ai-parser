import fitz  # PyMuPDF
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_soc2_summary(file):
    raw_text = extract_text_from_pdf(file)

    prompt = (
        "You're an expert compliance analyst. "
        "Given this SOC 2 report, extract the following:\n"
        "- Auditor Name and Firm\n"
        "- Time Period of the report\n"
        "- Scope of audit (systems, teams, functions)\n"
        "- Any noted exceptions and management responses\n"
        "- Key security practices (e.g., encryption, access control)\n\n"
        "Respond in this JSON format:\n"
        "{\n"
        "  'Auditor': '',\n"
        "  'Time Period': '',\n"
        "  'Scope': '',\n"
        "  'Exceptions': '',\n"
        "  'Security Controls': ''\n"
        "}\n\n"
        f"Document:\n{raw_text[:7000]}"  # limit to avoid token overload
    )

    llm = ChatOpenAI(model="gpt-4", temperature=0)
    response = llm([HumanMessage(content=prompt)])
    try:
        return eval(response.content)
    except Exception:
        return {"Error": "Failed to parse AI response. Please review raw text."}
