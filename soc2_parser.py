import fitz  # PyMuPDF
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_soc2_summary(file):
    raw_text = extract_text_from_pdf(file)

    prompt = f"""
You are a SOC 2 compliance analyst. Analyze the following SOC 2 report text and extract the following structured fields:

1. Auditor name and audit firm  
2. Audit time period  
3. Scope of audit (systems, teams, services, etc.)  
4. List of any exceptions with control name, exception, and management response  
5. Number of controls that were Passed, Passed with Exception, or Excluded (return counts only)  
6. List 3–4 Risk/Focus Tags based on areas mentioned in the report (like Encryption, Access Control, Data Residency, etc.)  
7. Provide a short 3–5 bullet summary of the system description (how it handles infra, data, access, logging)

Return result as a Python dictionary like:
{{
  "Auditor": "",
  "Time Period": "",
  "Scope": "",
  "Status Counts": {{
      "Passed": int,
      "Passed with Exception": int,
      "Excluded": int
  }},
  "Exceptions": [
    {{
      "Control": "",
      "Exception": "",
      "Response": ""
    }},
    ...
  ],
  "Tags": ["", "", ""],
  "System Description": ["", "", ""]
}}

Document:
{raw_text[:7000]}
    """

    llm = ChatOpenAI(model="gpt-4", temperature=0)
    response = llm([HumanMessage(content=prompt)])

    try:
        return eval(response.content)  # ⚠️ If LLM returns exact dict, this works
    except Exception:
        return {"Error": "Could not parse AI response. Please try with a different document."}
