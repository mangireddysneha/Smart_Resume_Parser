import re

def ats_suggestions(text):
    ats = []
    if re.search(r"table", text, re.I):
        ats.append("Remove tables; ATS may not parse them.")
    if re.search(r"image|jpg|png|logo", text, re.I):
        ats.append("Avoid images in resume.")
    if not all(h in text.lower() for h in ["education", "experience", "skills"]):
        ats.append("Add standard section headers.")
    if len(text) > 7000:
        ats.append("Resume too long; consider shortening.")
    return ats
