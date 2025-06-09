import spacy
from textblob import TextBlob

nlp = spacy.load("en_core_web_sm")

def check_grammar(text):
    blob = TextBlob(text)
    suggestions = []
    for sentence in blob.sentences:
        if str(sentence) != str(sentence.correct()):
            suggestions.append(f"❌ {sentence} → ✅ {sentence.correct()}")
    return suggestions

def check_skills(text):
    with open("skill_list.txt") as f:
        skills = [line.strip().lower() for line in f]
    matched = [skill for skill in skills if skill in text.lower()]
    missing = [skill for skill in skills if skill not in text.lower()]
    return matched, missing, skills

def get_resume_score(grammars, matched, total_skills):
    grammar_score = max(0, 5 - len(grammars))  # out of 5
    skill_score = (len(matched) / len(total_skills)) * 5  # out of 5
    return round(grammar_score + skill_score, 1), grammar_score, round(skill_score, 1)