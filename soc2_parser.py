# soc2_parser.py

import fitz  # PyMuPDF
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Extract text from uploaded PDF file
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    return text

# Prompt template for structured SOC 2 parsing
soc2_prompt = PromptTemplate(
    input_variables=["report"],
    template="""
You are a SOC 2 compliance analyst AI.
Given the SOC 2 audit report below, extract the following in a clean and well-formatted markdown:

1. **Auditor name and firm**
2. **Report scope and audit time period**
3. **Control exceptions and management responses** (present this in a table with Control ID, Description, Suggested Mitigation, Severity Score: High / Medium / Low)
4. **Highlights on control areas** like access control, encryption, backups
5. **Plain English summary** (bold the key gaps)
6. **Additional observations** (if any)

Use markdown for clean output. Prioritize clarity and use bullet points or tables where useful.

Report:
{report}
"""
)

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

chain = LLMChain(
    llm=llm,
    prompt=soc2_prompt,
    verbose=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

def extract_soc2_info(uploaded_file):
    raw_text = extract_text_from_pdf(uploaded_file)
    result = chain.run(report=raw_text)
    return result
