import streamlit as st
import fitz
import re
from docx import Document
import plotly.graph_objects as go

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config("Smart Resume Parser", layout="centered")
local_css("style.css")
st.title("AI Resume Screener")

ROLE_SKILLS = {
    "Data Scientist": ["Python", "Pandas", "Numpy", "Scikit-Learn", "Machine Learning", "SQL"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Redux"],
    "Backend Developer": ["Python", "Django", "Flask", "PostgreSQL", "APIs"],
    "Data Analyst": ["SQL", "Excel", "Python", "Tableau"],
    "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Docker"],
    "Other": []
}
SOFT_SKILLS = [
    "Time Management", "Effective Communication", "Collaboration", "Leadership",
    "Problem Solving", "Creativity", "Adaptability"
]
TECH_KEYWORDS = set(sum(ROLE_SKILLS.values(), []))

def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for p in doc:
            text += p.get_text()
    return text

def read_docx(file):
    return "\n".join([p.text for p in Document(file).paragraphs])

def preprocess_text(text):
    clean = re.sub(r"(\w)-\s*\n(\w)", r"\1\2", text)
    clean = re.sub(r"\s*\n\s*", " ", clean)
    return clean

def extract_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for l in lines[:7]:
        if re.match(r"^[A-Z][A-Z\s\-]{2,}$", l) and 2 <= len(l.split()) <= 4:
            return l.title()
        if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", l):
            return l.title()
    return lines[0].title() if lines else "-"

def extract_phone(text):
    phones = re.findall(r"(?:\+91[-\s]?)?\b\d{10}\b", text)
    nums = []
    for p in phones:
        if not p.startswith("+91"):
            p = "+91-" + p
        nums.append(p)
    return ", ".join(dict.fromkeys(nums)) if nums else "-"

def extract_email(text):
    clean = preprocess_text(text)
    emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", clean)
    return ", ".join(dict.fromkeys(emails)) if emails else "-"

def extract_linkedin(text):
    clean = preprocess_text(text)
    links = re.findall(
        r"(?:https?://)?(?:www\.)?(linkedin\.com/(?:in|pub)/[a-zA-Z0-9\-\_/%\.]+)", clean, re.I
    )
    links = [l.rstrip('.;,') for l in links]
    return ", ".join(dict.fromkeys(links)) if links else "-"

def extract_github(text):
    clean = preprocess_text(text)
    links = re.findall(
        r"(?:https?://)?(?:www\.)?(github\.com/[a-zA-Z0-9\-\_/%\.]+)", clean, re.I
    )
    links = [l.rstrip('.;,') for l in links]
    return ", ".join(dict.fromkeys(links)) if links else "-"

def clean_skill_string(s):
    words = re.split(r"[ ,/;()\|]", s)
    skills = []
    for w in words:
        wup = w.upper()
        if wup in [x.upper() for x in TECH_KEYWORDS]:
            if wup in ["JS", "JAVASCRIPT"]:
                if "JavaScript" not in skills:
                    skills.append("JavaScript")
            else:
                val = w.title()
                if val not in skills:
                    skills.append(val)
    return skills

def smart_skill_group(text, label, patterns):
    regex = rf"{label}\s*[:\-]?\s*(.*)"
    out = []
    for line in text.split('\n'):
        m = re.search(regex, line, re.I)
        if m:
            found = clean_skill_string(m.group(1))
            out.extend(found)
    for pt in patterns:
        if re.search(rf'\b{re.escape(pt)}\b', text, re.I) and pt.title() not in out:
            out.append(pt.title())
    return list(dict.fromkeys(out))

def extract_soft_skills(text):
    found = []
    t = text.lower()
    for s in SOFT_SKILLS:
        if s.lower() in t and s.title() not in found:
            found.append(s.title())
    return found

def normalize_tech_skills(skills):
    mapped = []
    for s in skills:
        stxt = s.strip().lower()
        if stxt in ["js", "javascript"]:
            if "JavaScript" not in mapped:
                mapped.append("JavaScript")
        else:
            sval = s.strip().title()
            if sval not in mapped:
                mapped.append(sval)
    return mapped

def skill_gap_analysis(tech_skills, job_role):
    required = set([s.title() for s in ROLE_SKILLS.get(job_role,[])])
    resume = set(s.title() for s in tech_skills)
    gap = [s for s in required if s not in resume]
    overlap = [s for s in required if s in resume]
    return list(required), sorted(gap), int(100*len(overlap)/(len(required) or 1)), overlap

def recommend_courses(missing_skills):
    lkup = {
        "Python": "https://www.coursera.org/specializations/python",
        "React": "https://react.dev/learn",
        "Django": "https://docs.djangoproject.com/en/4.1/intro/",
        "Scikit-Learn": "https://scikit-learn.org/stable/tutorial/index.html",
        "Html": "https://www.w3schools.com/html/",
        "Css": "https://www.w3schools.com/css/",
        "JavaScript": "https://www.javascript.com/",
        "Redux": "https://redux.js.org/introduction/getting-started"
    }
    out = []
    for s in missing_skills:
        url = lkup.get(s, None)
        if url:
            out.append(f"[{s} Course]({url})")
        else:
            out.append(f"Online course: {s}")
    return out

def calculate_professional_ats_score(text, details, required_skills, overlap_count):
    score = 0
    text_lower = text.lower()
    if 'skills' in text_lower: score += 10
    if 'experience' in text_lower or 'project' in text_lower: score += 10
    if details["Email"] != "-" and details["Phone"] != "-": score += 10
    action_verbs = ['developed', 'managed', 'implemented', 'created', 'led', 'analyzed', 'built', 'designed', 'engineered']
    if any(verb in text_lower for verb in action_verbs): score += 10
    if re.search(r'\d+%', text) or re.search(r'\d+\s*(?:times|x)\b', text): score += 10
    if details["LinkedIn"] != "-" or details["GitHub"] != "-": score += 10
    total_required = len(required_skills)
    if total_required > 0:
        match_ratio = overlap_count / total_required
        score += int(match_ratio * 40)
    return max(0, min(100, score))

col1, col2 = st.columns((2,1))
with col1:
    uploaded_file = st.file_uploader("Upload resume (PDF/DOCX)", type=["pdf", "docx"])
with col2:
    job_role = st.selectbox(
        "Target Role for Skill Gap",
        ["-- Select a Target Role --"] + list(ROLE_SKILLS.keys())
    )

if uploaded_file:
    if job_role != "-- Select a Target Role --":
        if st.button("Analyze Resume"):
            ext = uploaded_file.name.lower().split('.')[-1]
            text = read_pdf(uploaded_file) if ext == "pdf" else read_docx(uploaded_file)

            details = dict()
            details["Name"] = extract_name(text)
            details["Phone"] = extract_phone(text)
            details["Email"] = extract_email(text)
            details["LinkedIn"] = extract_linkedin(text)
            details["GitHub"] = extract_github(text)

            prog_lang = smart_skill_group(text, "Programming Languages", ["Python", "Java"])
            frontend = smart_skill_group(text, "Frontend", ["HTML", "CSS", "JavaScript", "JS"])
            backend = smart_skill_group(text, "Backend", ["MySQL", "MongoDB", "APIs"])
            gui = smart_skill_group(text, "GUI", ["Python Tkinter"])
            softs = extract_soft_skills(text)

            tech_skills = normalize_tech_skills(prog_lang + frontend + backend + gui)
            soft_skills = [s.title() for s in softs]

            st.markdown("---")
            st.markdown("## Profile Overview")
            details_table_md = f"""
            | | |
            |---|---|
            | **Name** | {details['Name']} |
            | **Phone** | {details['Phone']} |
            | **Email** | {details['Email']} |
            | **LinkedIn** | {details['LinkedIn']} |
            | **GitHub** | {details['GitHub']} |
            """
            st.markdown(details_table_md)

            st.markdown("---")
            st.markdown("## Core Competencies")
            col1_skills, col2_skills = st.columns(2)
            with col1_skills:
                if tech_skills:
                    st.markdown("**Technical Skills:**")
                    for t in tech_skills:
                        st.markdown(f"- {t}")
            with col2_skills:
                if soft_skills:
                    st.markdown("**Soft Skills:**")
                    for s in soft_skills:
                        st.markdown(f"- {s}")
            st.markdown("<br>", unsafe_allow_html=True)

            req_skills, missing_skills, gap_pct, overlap = skill_gap_analysis(tech_skills, job_role)
            ats_score = calculate_professional_ats_score(text, details, req_skills, len(overlap))

            st.markdown("---")
            st.markdown("## ATS Fit Score")
            st.markdown(f"**Score for _{job_role}_: {ats_score}/100**")
            st.markdown("<br>", unsafe_allow_html=True)

            if req_skills:
                st.markdown("---")
                st.markdown("## Missing Competencies")
                st.markdown(f"**Missing for _{job_role}_:**\n" +
                    (", ".join(missing_skills) if missing_skills else '<span style="color:green"><b>None!</b></span>'),
                    unsafe_allow_html=True)
                if missing_skills:
                    st.write("**Suggested Online Courses:**")
                    for c in recommend_courses(missing_skills):
                        st.markdown("- " + c)
                st.markdown("<br>", unsafe_allow_html=True)

            if req_skills:
                st.markdown("---")
                st.markdown("## Role Fit Analysis")

                matched_count = len(overlap)
                missing_count = len(missing_skills)

                if matched_count + missing_count > 0:
                    labels = ['Skills Matched', 'Skills Missing']
                    values = [matched_count, missing_count]

                    fig = go.Figure(data=[go.Bar(
                        x=labels,
                        y=values,
                        text=[f'{v} Skills' for v in values],
                        textposition='auto',
                        marker_color=['#27ae60', '#c0392b']
                    )])

                    fig.update_layout(
                        yaxis_title='Number of Skills',
                        plot_bgcolor='rgba(0,0,0,0)',
                        bargap=0.3
                    )

                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select a target role to enable the 'Analyze Resume' button.")
