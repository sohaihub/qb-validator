import streamlit as st
import pandas as pd
import google.generativeai as genai

# 🔐 Embed Gemini API Key directly (not recommended for production)
genai.configure(api_key="AIzaSyBj1BzzNCg6FOUeic8DTtU3uYNVMaDErQw")
model = genai.GenerativeModel("gemini-1.5-flash")

def validate_question(question, topic, level):
    prompt = f"""
You are an expert educator. Analyze the following question.

Topic: "{topic}"
Level: {level}
Question: "{question}"

Respond in the format:
- Relevant: Yes/No
- Suggestion: <Alternative question if not relevant>
- Explanation: <Why it's relevant or not>
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_batch(questions, topic, level):
    results = []
    for q in questions:
        result = validate_question(q, topic, level)
        parsed = {"Question": q, "Relevant": "", "Suggestion": "", "Explanation": ""}

        for line in result.split("\n"):
            if "Relevant:" in line:
                parsed["Relevant"] = line.split(":", 1)[-1].strip()
            elif "Suggestion:" in line:
                parsed["Suggestion"] = line.split(":", 1)[-1].strip()
            elif "Explanation:" in line:
                parsed["Explanation"] = line.split(":", 1)[-1].strip()

        results.append(parsed)
    return pd.DataFrame(results)

# 🖼️ Streamlit UI
st.set_page_config("Advanced QB Validator", layout="wide")
st.title("🧠 AI-Powered Question Bank Validator")

with st.sidebar:
    st.header("⚙️ Settings")
    topic = st.text_input("Topic", placeholder="e.g., Photosynthesis")
    level = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
    uploaded_file = st.file_uploader("Upload CSV (.csv with one column of questions)", type="csv")

tab1, tab2 = st.tabs(["📄 Manual Input", "📊 Uploaded Questions"])

# Manual input
with tab1:
    manual_questions = st.text_area("Enter one question per line")

# Uploaded questions
questions_list = []
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    questions_list = df.iloc[:, 0].dropna().tolist()
elif manual_questions:
    questions_list = manual_questions.strip().splitlines()

if st.button("🚀 Validate Questions"):
    if not topic or not level:
        st.error("Please specify both topic and difficulty level.")
    elif not questions_list:
        st.warning("Provide at least one question.")
    else:
        st.info(f"Validating {len(questions_list)} questions. Please wait...")
        result_df = analyze_batch(questions_list, topic, level)
        st.success("Validation complete ✅")
        st.dataframe(result_df, use_container_width=True)

        # Download button
        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "validated_questions.csv", "text/csv")
