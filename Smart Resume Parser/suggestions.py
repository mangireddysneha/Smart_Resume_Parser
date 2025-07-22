import re

def check_missing_essentials(parsed, contact, fname):
    missing = []
    if not contact:
        missing.append("🚨 Contact info missing!")
    if not parsed.get("education"):
        missing.append("🚨 Education section missing!")
    if not parsed.get("experience"):
        missing.append("🚨 Work/Internship/Experience missing!")
    if not parsed.get("skills"):
        missing.append("🚨 Skills section missing!")
    SOFTS = ["communication", "leadership", "teamwork", "collaboration", "time management", "problem solving"]
    skills = ",".join(parsed.get("skills", [])).lower()
    if not any(w in skills for w in SOFTS):
        missing.append("❓ No soft skills found!")
    if any(w in fname.lower() for w in ["resume", "cv", "final", "doc"]):
        missing.append("❗ Unprofessional file name detected.")
    return missing

def skill_gap_analysis(skills, job_role):
    role_skills = {
        "Data Scientist": ["Python", "Pandas", "Numpy", "Scikit-Learn", "Machine Learning", "SQL"],
        "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Redux"],
        "Backend Developer": ["Python", "Django", "Flask", "PostgreSQL", "APIs"],
        "Data Analyst": ["SQL", "Excel", "Python", "Tableau"],
        "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Docker"],
        "Other": []
    }
    required = role_skills.get(job_role, [])
    skills_lower = [s.lower() for s in skills]
    overlap = [r for r in required if r.lower() in skills_lower]
    gap = [r for r in required if r.lower() not in skills_lower]
    percent = int(100 * len(overlap) / (len(required) or 1))
    return required, gap, percent

def recommend_courses(missing_skills):
    courses = []
    lkup = {
        "python": "https://www.coursera.org/specializations/python",
        "react": "https://react.dev/learn",
        "django": "https://docs.djangoproject.com/en/4.1/intro/",
        "scikit-learn": "https://scikit-learn.org/stable/tutorial/index.html",
        "html": "https://www.w3schools.com/html/",
        "css": "https://www.w3schools.com/css/",
        "javascript": "https://www.javascript.com/",
        "redux": "https://redux.js.org/introduction/getting-started"
    }
    for s in missing_skills:
        url = lkup.get(s.lower())
        if url:
            courses.append(f"[{s} Official Course]({url})")
        else:
            courses.append(f"Online course: {s}")
    return courses

def customized_tips(parsed):
    tips = [
        "Try to quantify your impact (e.g., 'Improved performance by 30%').",
        "Add GitHub links for projects.",
        "Mention frameworks/tools used (React, Docker, etc.)."
    ]
    return tips

def linkedin_portfolio_check(text):
    github = re.search(r"github\\.com/\\S+", text, re.I)
    linkedin = re.search(r"linkedin\\.com/in/\\S+", text, re.I)
    addlnk = None
    if not linkedin:
        addlnk = "Consider adding your LinkedIn profile for credibility."
    return (github.group(0) if github else None, linkedin.group(0) if linkedin else None, addlnk)

def quantify_impact_suggestion(text):
    if not re.search(r"\\d+%", text):
        return "Try to include numeric impact statements (e.g., improved X by 20%)."
    return None

def jd_matching(skills_in_resume, jd_text):
    resume_set = set([s.lower() for s in skills_in_resume])
    jd_skills = set(re.findall(r"\\b[A-Za-z][A-Za-z\\+\\#]{1,}\\b", jd_text))
    overlap = [s for s in jd_skills if s.lower() in resume_set]
    gap = [s for s in jd_skills if s.lower() not in resume_set]
    percent = int(100 * len(overlap) / (len(jd_skills) or 1))
    return percent, overlap, gap
