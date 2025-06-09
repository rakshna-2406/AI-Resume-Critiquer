import streamlit as st
import fitz
import io
from fpdf import FPDF
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from resume_parser import check_grammar, check_skills, get_resume_score

#  Styling for drag-and-drop uploader
st.markdown("""
<style>
    .stFileUploader > div {
        background-color: #fff9c4 !important;
        border: 2px dashed #fbc02d !important;
        color: #795548 !important;
        border-radius: 10px;
        padding: 20px;
        font-weight: bold;
        text-align: center;
    }
    .stFileUploader label {
        color: #795548 !important;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

#  Login setup
def login():
    st.title("🔐 Login to AI Resume Review")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "test123":
            st.session_state.logged_in = True
            st.success("Login successful! 🎉")
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")

#  PDF extraction
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def suggest_job_title(skills):
    skills_lower = [s.lower() for s in skills]
    if "machine learning" in skills_lower or "deep learning" in skills_lower:
        return "AI/ML Intern"
    elif "web development" in skills_lower:
        return "Frontend Developer"
    elif "java" in skills_lower:
        return "Java Developer"
    else:
        return "IT Intern"

def suggest_linkedin_headline(skills):
    return f"Final Year IT Student | {' | '.join(skills[:3]).title()}"

def resume_recommendations(grammar_issues, missing_skills):
    suggestions = []
    if grammar_issues:
        suggestions.append("• Improve grammar and spelling consistency.")
    if missing_skills:
        suggestions.append("• Add more relevant technical skills based on your career goal.")
    if not suggestions:
        suggestions.append("• Your resume is well optimized! Just ensure clarity and formatting.")
    return suggestions

def safe_text(txt):
    return txt.encode("latin-1", errors="ignore").decode("latin-1")

#  Session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    st.title("📄 AI Resume Review Tool")
    st.write("Upload your resume to check grammar, extract skills, and get a feedback report.")

    uploaded_file = st.file_uploader("📎 Upload Resume File", type=["pdf", "txt"])

    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = uploaded_file.read().decode("utf-8", errors="ignore")

        st.subheader("📝 Extracted Resume Text")
        st.text_area("Resume Text", resume_text, height=200)

        if st.button("🔍 Analyze Resume"):
            grammars = check_grammar(resume_text)
            matched, missing, all_skills = check_skills(resume_text)
            total_score, grammar_score, skill_score = get_resume_score(grammars, matched, all_skills)

            st.markdown(f"### ✅ Score: **{total_score}/10**")
            st.markdown(f"- Grammar: **{grammar_score}/5**")
            st.markdown(f"- Skills: **{skill_score}/5**")

            st.subheader("✍️ Grammar Suggestions")
            if grammars:
                for g in grammars:
                    st.warning(g)
            else:
                st.success("No grammar issues found!")

            st.subheader("💡 Skills Identified")
            st.info(", ".join(matched) if matched else "None found.")

            st.subheader("🚫 Missing Skills")
            st.error(", ".join(missing) if missing else "All essential skills present!")

            job_title = suggest_job_title(matched)
            headline = suggest_linkedin_headline(matched)

            st.subheader("🎯 AI Suggestions")
            st.success(f"Suggested Job Title: **{job_title}**")
            st.info(f"LinkedIn Headline: **{headline}**")

            st.subheader("📌 Resume Recommendations")
            for rec in resume_recommendations(grammars, missing):
                st.info(rec)

            st.subheader("☁️ Resume Word Cloud")
            wordcloud = WordCloud(width=800, height=300, background_color="white").generate(resume_text)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)

            def generate_pdf():
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, safe_text(f"Resume Score: {total_score}/10"))
                pdf.multi_cell(0, 10, safe_text(f"Grammar Score: {grammar_score}/5"))
                pdf.multi_cell(0, 10, safe_text(f"Skill Score: {skill_score}/5"))
                pdf.multi_cell(0, 10, safe_text(f"Suggested Job Title: {job_title}"))
                pdf.multi_cell(0, 10, safe_text(f"LinkedIn Headline: {headline}"))
                pdf.multi_cell(0, 10, safe_text("Grammar Suggestions:"))
                for g in grammars:
                    pdf.multi_cell(0, 10, safe_text(g))
                pdf.multi_cell(0, 10, safe_text("Skills Found: " + ", ".join(matched)))
                pdf.multi_cell(0, 10, safe_text("Missing Skills: " + ", ".join(missing)))
                pdf.multi_cell(0, 10, safe_text("Recommendations:"))
                for rec in resume_recommendations(grammars, missing):
                    pdf.multi_cell(0, 10, safe_text(rec))
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                return io.BytesIO(pdf_bytes)

            buffer = generate_pdf()
            st.download_button("📥 Download PDF Report", data=buffer, file_name="resume_feedback.pdf", mime="application/pdf")

    else:
        st.info("Upload your resume above to begin analysis.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
