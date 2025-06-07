import fitz  # PyMuPDF
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_soc2_info(uploaded_file):
    raw_text = extract_text_from_pdf(uploaded_file)

    template = """
You are an expert auditor AI. Extract the following from the SOC 2 audit report text below:

1. Auditor name and firm
2. Report scope and audit time period
3. Any control exceptions and management responses
4. Highlights on control areas like access control, encryption, backups
5. Summary in plain English

Only include actual content from the report. Return each point clearly labeled.

Report text:
{report}
"""

    prompt = PromptTemplate(
        input_variables=["report"],
        template=template,
    )

    llm = ChatOpenAI(temperature=0, model="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

    chain = LLMChain(llm=llm, prompt=prompt)

    result = chain.run(report=raw_text)
    
    # Convert result into sections
    lines = result.split("\n")
    output = {}
    current_key = ""
    for line in lines:
        if any(x in line.lower() for x in ["auditor", "scope", "exception", "highlight", "summary"]):
            current_key = line.strip()
            output[current_key] = ""
        elif current_key:
            output[current_key] += line.strip() + " "
    
    return output
