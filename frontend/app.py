import re
import streamlit as st
import random
import sys
import os

# Ensure backend folder is importable
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from study_tools import explain_topic, summarize_text, generate_quiz, generate_flashcards

# -----------
# --------------------------
# Page config & styling
# --------------------------
st.set_page_config(page_title="AI Study Buddy", page_icon="🧠", layout="wide")

page_bg = """
<style>
[data-testid="stHeader"] {
    background: linear-gradient(90deg, #667eea, #764ba2);
}
h1 {
    color: #333333;
    text-align: center;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'>🧠 Welcome to AI Study Buddy</h1>", unsafe_allow_html=True)

st.markdown("""
<div style="
    display: flex;
    justify-content: center;
    align-items: center;
    height: 150px;  /* Adjust height as needed */
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 12px;
    color: white;
    text-align: center;
    font-size: 1.2rem;">
✨ Welcome to the AI Study Buddy!  
Type a topic or paste your notes below and let AI do the hard work. 📚
</div>
""", unsafe_allow_html=True)

# --------------------------
# Session state initialization
# --------------------------
defaults = {
    "explanation": "",
    "summary": "",
    "quiz": "",
    "quiz_parsed": None,
    "flashcards": "",
    "score": 0,
    "active_tab": "📘 Explain Topic"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def switch_to(tab_name: str):
    st.session_state.active_tab = tab_name
    st.rerun()

# --------------------------
# Helper: Parse quiz text
# --------------------------
# def parse_quiz(quiz_text):
#     questions = re.split(r'(?=Q\d+\.)', quiz_text)
#     parsed = []
#     for q in questions:
#         q = q.strip()
#         if not q:
#             continue
#         lines = q.splitlines()
#         question_line = lines[0].strip()
#         question_text = re.sub(r'^Q\d+\.\s*', '', question_line)
#         options = []
#         correct = None
#         for line in lines[1:]:
#             if re.match(r'^[A-D][\)\.]', line.strip()):
#                 options.append(line.strip()[2:].strip())
#             elif line.strip().lower().startswith("answer:"):
#                 correct = line.split(":")[-1].strip().upper()
#         parsed.append({
#             "question": question_text,
#             "options": options,
#             "correct": correct
#         })
#     return parsed

# --------------------------
# Navigation Tabs
# --------------------------
tabs = ["📘 Explain Topic", "📝 Summarize Notes", "❓ Generate Quiz", "📚 Generate Flashcards"]
selected_tab = st.radio("📍 Navigation", tabs, index=tabs.index(st.session_state.active_tab), horizontal=True)

# --------------------------
# TAB 1: Explain
# --------------------------
if selected_tab == "📘 Explain Topic":
    st.title("📘 Explain Topic")
    topic = st.text_input("Enter a topic to explain:", key="topic_input")

    if st.button("Explain", key="explain_btn"):
        if topic.strip():
            with st.spinner("Generating explanation..."):
                explanation = explain_topic(topic)
                st.session_state.explanation = explanation
                st.session_state.summary = ""
                st.session_state.quiz = ""
                st.session_state.quiz_parsed = None
                st.session_state.flashcards = ""
                st.session_state.score = 0
            st.success("✅ Explanation ready!")

    if st.session_state.explanation:
        st.subheader("📘 Simplified Explanation")
        st.write(st.session_state.explanation)
        st.download_button("💾 Download Explanation", st.session_state.explanation, "explanation.txt")

        if st.button("➡ Summarize this Explanation"):
            with st.spinner("Summarizing..."):
                st.session_state.summary = summarize_text(st.session_state.explanation)
            st.success("📝 Summary generated successfully!")
            switch_to("📝 Summarize Notes")

# --------------------------
# TAB 2: Summarize
# --------------------------
elif selected_tab == "📝 Summarize Notes":
    st.title("📝 Summarize Notes")
    notes = st.text_area("Paste or edit your notes:", value=st.session_state.summary or st.session_state.explanation)

    if st.button("Summarize", key="summarize_btn"):
        if notes.strip():
            with st.spinner("Summarizing..."):
                st.session_state.summary = summarize_text(notes)
            st.success("✅ Summary ready!")

    if st.session_state.summary:
        st.subheader("📝 Summary")
        st.write(st.session_state.summary)
        st.download_button("💾 Download Summary", st.session_state.summary, "summary.txt")

        if st.button("➡ Generate Quiz from this Summary"):
            with st.spinner("Creating quiz..."):
                quiz_text = generate_quiz(st.session_state.summary, 5)
                st.session_state.quiz = quiz_text
                st.session_state.quiz_parsed = parse_quiz(quiz_text)
                st.session_state.score = 0
            st.success("✅ Quiz generated successfully!")
            switch_to("❓ Generate Quiz")

# --------------------------
# TAB 3: Interactive Quiz
# --------------------------
elif selected_tab == "❓ Generate Quiz":
    st.title("❓ Interactive Quiz")

    quiz_notes = st.text_area(
        "Paste text to generate quiz questions:",
        value=st.session_state.summary or st.session_state.explanation
    )
    num_qs = st.slider("Number of questions:", 3, 10, 5, key="num_qs_slider")

    if st.button("Generate Quiz", key="quiz_btn"):
        if quiz_notes.strip():
            with st.spinner("Generating quiz..."):
                try:
                    quiz_text = generate_quiz(quiz_notes, num_qs)
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")
                    quiz_text = ""
                st.session_state.quiz = quiz_text
                st.session_state.selected_answers = {}
                st.session_state.show_results = False
            st.success("✅ Quiz generated successfully! Scroll below to attempt it.")
        else:
            st.warning("Please enter some text first.")

    # --- Improved Parser ---
    import re
    def parse_quiz_text(text):
        """Parse Gemini quiz output into clean Q/A/C structure."""
        questions_raw = re.split(r'(?=Question\s*\d+)', text, flags=re.I)
        parsed = []

        for q in questions_raw:
            q = q.strip()
            if not q:
                continue

            # Extract question text
            q_match = re.search(r'Question\s*\d+[\.:]?\s*(.*)', q, flags=re.I)
            question = q_match.group(1).strip() if q_match else q

            # Extract all option lines like "A) ..." "B) ..." etc.
            option_lines = re.findall(r'^[A-D][\)\.\:]?\s*.*', q, flags=re.M)
            cleaned_opts = []
            for opt in option_lines:
                # remove leading A) / B. / C:
                opt = re.sub(r'^[A-D][\)\.\:]?\s*', '', opt).strip()
                # skip any corrupted or partial question line
                if len(opt) < 3 or "question" in opt.lower():
                    continue
                # fix capitalization if missing
                if opt and opt[0].islower():
                    opt = opt[0].upper() + opt[1:]
                cleaned_opts.append(opt)

            # remove any "Correct Answer" text variants that might sneak in
            cleaned_opts = [
                o for o in cleaned_opts
                if not re.search(r'(orrect\s*answer|correct\s*ans|^answer)', o, re.I)
            ]

            # Extract correct answer letter (A/B/C/D)
            correct_match = re.search(r'correct\s*answer[:\-]?\s*([A-D])', q, flags=re.I)
            correct = correct_match.group(1).upper() if correct_match else None

            parsed.append({
                "question": question,
                "options": cleaned_opts,
                "correct": correct
            })

        return parsed

    # --- Display Quiz Form ---
    if st.session_state.quiz:

        quiz_data = parse_quiz_text(st.session_state.quiz)

        # ✅ Shuffle options for each question
        for q in quiz_data:
            if not q.get("options") or not q.get("correct"):
                continue
            # find index of correct option
            correct_idx = ord(q["correct"]) - ord("A")
            correct_opt = q["options"][correct_idx] if 0 <= correct_idx < len(q["options"]) else None

            # shuffle options
            random.shuffle(q["options"])

            # update correct letter after shuffle
            if correct_opt in q["options"]:
                new_idx = q["options"].index(correct_opt)
                q["correct"] = chr(ord("A") + new_idx)


        if quiz_data:
            st.subheader("📘 Attempt the Quiz")

            if "selected_answers" not in st.session_state:
                st.session_state.selected_answers = {}
            if "show_results" not in st.session_state:
                st.session_state.show_results = False

            with st.form("quiz_form", clear_on_submit=False):
                for i, q in enumerate(quiz_data):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    if q["options"]:
                        selected = st.radio(
                            "Choose your answer:",
                            q["options"],
                            index=None,
                            key=f"ans_{i}"
                        )
                        st.session_state.selected_answers[i] = selected
                    else:
                        st.warning("_⚠️ No valid options detected for this question._")
                    st.markdown("---")
                submitted = st.form_submit_button("✅ Submit Answers")

            # --- Evaluate answers on submit ---
            if submitted:
                score = 0
                results = []
                for i, q in enumerate(quiz_data):
                    user_ans = st.session_state.selected_answers.get(i)
                    correct_letter = q.get("correct")
                    correct_opt = None
                    if correct_letter and correct_letter in ["A", "B", "C", "D"]:
                        idx = ord(correct_letter) - ord("A")
                        if 0 <= idx < len(q["options"]):
                            correct_opt = q["options"][idx]
                    if user_ans == correct_opt:
                        score += 1
                        results.append(f"✅ **Q{i+1}: Correct!** ({user_ans})")
                    else:
                        results.append(
                            f"❌ **Q{i+1}: Wrong!**  Your: {user_ans or 'None'} | Correct: {correct_opt or 'N/A'}"
                        )

                st.session_state.show_results = True
                st.session_state.quiz_results = results
                st.session_state.quiz_score = score

        # --- Results Section ---
        if st.session_state.get("show_results", False):
            st.subheader("🏁 Quiz Results")
            for r in st.session_state.quiz_results:
                st.markdown(r)
            st.success(f"**Final Score:** {st.session_state.quiz_score} / {len(quiz_data)}")

            # Flashcards button
            if st.button("➡ Generate Flashcards from this Quiz", key="quiz_to_flashcards"):
                with st.spinner("Generating flashcards..."):
                    try:
                        flashcards_text = generate_flashcards(
                            st.session_state.summary or st.session_state.explanation, 5
                        )
                        st.session_state.flashcards = flashcards_text
                    except Exception as e:
                        st.error(f"Error generating flashcards: {e}")
                st.success("📚 Flashcards generated! Check the 'Generate Flashcards' tab.")
        else:
            st.info("👇 Generate a quiz above, answer all questions, then click **Submit Answers**.")

# --------------------------
# TAB 4: Flashcards
# --------------------------
elif selected_tab == "📚 Generate Flashcards":
    st.title("📚 Study Flashcards")
    flash_text = st.text_area("Paste study notes:", value=st.session_state.summary or st.session_state.explanation)
    num_cards = st.slider("Number of flashcards:", 3, 10, 5)
    if st.button("Generate Flashcards", key="flash_btn"):
        if flash_text.strip():
            with st.spinner("Generating flashcards..."):
                st.session_state.flashcards = generate_flashcards(flash_text, num_cards)
            st.success("✅ Flashcards ready!")

    if st.session_state.flashcards:
        st.write(st.session_state.flashcards)
        st.download_button("💾 Download Flashcards", st.session_state.flashcards, "flashcards.txt")

# --------------------------
# Footer
# --------------------------
st.markdown("""
<hr>
<div style="text-align:center; color:gray; font-size:0.9rem;">
  Made with ❤️ by <b>Aditya Dorwal</b><br>
  Powered by <b>Google Gemini API</b> | IBM Internship Project
</div>
""", unsafe_allow_html=True)
