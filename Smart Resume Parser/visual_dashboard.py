import matplotlib.pyplot as plt
import streamlit as st

def show_skill_pie(parsed):
    ss = parsed.get("skills", [])
    if not ss: return
    fig, ax = plt.subplots()
    ax.pie([1]*len(ss), labels=ss, autopct='%1.0f%%')
    st.pyplot(fig)

def show_exp_timeline(parsed):
    exp = parsed.get("experience", "")
    if not exp: return
    st.write("Experience Timeline: (example)")
    st.text(exp)

def show_edu_heatmap(parsed):
    edu = parsed.get("education", "")
    if not edu: return
    st.write("Education Heatmap: (example)")
    st.text(edu)
