import fitz
from docx import Document
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_resume_text(uploaded_file):
    ext = uploaded_file.name.lower().split('.')[-1]
    if ext == "pdf":
        text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    else:
        doc = Document(uploaded_file)
        return "\n".join(para.text for para in doc.paragraphs)

def parse_resume_sections(text):
    def section(s): return re.search(f"{s}:?\\s*(.*)", text, re.I)
    return {
        "skills": re.findall(r"Skills\\s*[:\\-]?\\s*(.*)", text, re.I)[0].split(",") if re.findall(r"Skills\\s*[:\\-]?\\s*(.*)", text, re.I) else [],
        "education": section("Education").group(1) if section("Education") else "",
        "experience": section("Experience").group(1) if section("Experience") else ""
    }

def detect_contact_info(text):
    phone = re.search(r'\\b\\d{10}\\b', text)
    email = re.search(r'\\b[\\w\\.-]+@[\\w\\.-]+\\b', text)
    info = []
    if email: info.append(email.group(0))
    if phone: info.append(phone.group(0))
    return ", ".join(info) if info else None

def get_file_name_warning(name):
    if re.search(r'resume|cv|new|final', name, re.I):
        return "File name is not professional. Rename to 'Firstname_Lastname.pdf'."
    return None

def get_file_score(text):
    return len(text)
