def resume_score(parsed, required_skills, resume_skills, grammar_score):
    score = 0
    if parsed.get("education"): score += 15
    if parsed.get("experience"): score += 20
    score += min(len(resume_skills), 6) * 5
    matched = len(set([s.lower() for s in resume_skills]).intersection([s.lower() for s in required_skills]))
    score += matched * 7
    score += grammar_score
    return min(score, 100)
