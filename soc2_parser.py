# soc2_parser.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import PyPDF2

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

template = """
You are an expert SOC 2 analyst. Given a SOC 2 report, extract the following insights in cleanly formatted markdown:

1. **Auditor name and firm**
2. **Report scope and audit time period**
3. **Any control exceptions and management responses**
4. **Highlights on control areas like access control, encryption, backups**
5. **Summary in plain English for leadership team**

Respond using HTML-compatible markdown (like <ul><li> etc), use <strong> for bold parts inside sections, and format control exceptions using bullet points for readability.

Report:
"""

prompt = PromptTemplate.from_template(template)
chain = LLMChain(llm=llm, prompt=prompt)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_soc2_info(file):
    try:
        raw_text = extract_text_from_pdf(file)
        result = chain.run(report=raw_text)

        return {
            "SOC 2 Summary Report": result
        }
    except Exception as e:
        print(f"Extraction error: {e}")
        return None
