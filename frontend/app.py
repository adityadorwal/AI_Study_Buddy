import re
import streamlit as st
import random
import sys
import os

# ── Import backend ───────────────────────────────────────────────────────────
# Robust path resolution: works whether run from project root or frontend/
_backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

from study_tools import explain_topic, summarize_text, generate_quiz, generate_flashcards


# ── Page config & styling ────────────────────────────────────────────────────

st.set_page_config(page_title="AI Study Buddy", page_icon="🧠", layout="wide")

st.markdown("""
<style>
[data-testid="stHeader"] {
    background: linear-gradient(90deg, #667eea, #764ba2);
}
h1 {
    color: #333333;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🧠 Welcome to AI Study Buddy</h1>", unsafe_allow_html=True)

st.markdown("""
<div style="
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 12px;
    color: white;
    text-align: center;
    font-size: 1.2rem;
    margin-bottom: 20px;">
✨ Welcome to the AI Study Buddy!<br>
Type a topic or paste your notes below and let AI do the hard work. 📚
</div>
""", unsafe_allow_html=True)


# ── Session state initialization ─────────────────────────────────────────────

defaults = {
    "explanation": "",
    "summary": "",
    "quiz": "",
    "quiz_parsed": None,        # parsed once and stored — NOT re-parsed on every render
    "quiz_shuffled": None,      # shuffled once and stored — NOT reshuffled on every render
    "flashcards": "",
    "score": 0,
    "active_tab": "📘 Explain Topic",
    "selected_answers": {},
    "show_results": False,
    "quiz_results": [],
    "quiz_score": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def switch_to(tab_name: str):
    st.session_state.active_tab = tab_name
    st.rerun()


# ── Quiz parser (module-level — defined once, not inside a tab block) ────────

def parse_quiz_text(text: str) -> list:
    """
    Parse Gemini quiz output into a clean list of dicts:
    [{ question, options: [str, str, str, str], correct: 'A'|'B'|'C'|'D' }, ...]
    """
    questions_raw = re.split(r'(?=Question\s*\d+)', text, flags=re.I)
    parsed = []

    for q in questions_raw:
        q = q.strip()
        if not q:
            continue

        # Extract question text
        q_match = re.search(r'Question\s*\d+[\.\:]?\s*(.*)', q, flags=re.I)
        question = q_match.group(1).strip() if q_match else q

        # Extract all option lines like "A) ..." "B) ..." etc.
        option_lines = re.findall(r'^[A-D][\)\.\:]?\s*.*', q, flags=re.M)
        cleaned_opts = []
        for opt in option_lines:
            opt_text = re.sub(r'^[A-D][\)\.\:]?\s*', '', opt).strip()
            if len(opt_text) < 3 or "question" in opt_text.lower():
                continue
            if opt_text and opt_text[0].islower():
                opt_text = opt_text[0].upper() + opt_text[1:]
            cleaned_opts.append(opt_text)

        # Remove any "Correct Answer" lines that slipped into options
        cleaned_opts = [
            o for o in cleaned_opts
            if not re.search(r'(orrect\s*answer|correct\s*ans|^answer)', o, re.I)
        ]

        # Extract correct answer letter (A/B/C/D)
        correct_match = re.search(r'correct\s*answer[\:\-]?\s*([A-D])', q, flags=re.I)
        correct = correct_match.group(1).upper() if correct_match else None

        if question and cleaned_opts and correct:
            parsed.append({
                "question": question,
                "options": cleaned_opts,
                "correct": correct,
            })

    return parsed


def shuffle_quiz(parsed: list) -> list:
    """
    Shuffle each question's options and update the correct-answer letter accordingly.
    Returns a new list — original parsed data is not mutated.
    Called ONCE when quiz is generated, result stored in session_state.quiz_shuffled.
    """
    shuffled = []
    for q in parsed:
        if not q.get("options") or not q.get("correct"):
            shuffled.append(q)
            continue

        opts = q["options"][:]
        correct_idx = ord(q["correct"]) - ord("A")
        correct_opt = opts[correct_idx] if 0 <= correct_idx < len(opts) else None

        random.shuffle(opts)

        if correct_opt and correct_opt in opts:
            new_correct = chr(ord("A") + opts.index(correct_opt))
        else:
            new_correct = None

        shuffled.append({
            "question": q["question"],
            "options": opts,
            "correct": new_correct,
        })
    return shuffled


# ── Navigation ───────────────────────────────────────────────────────────────

tabs = ["📘 Explain Topic", "📝 Summarize Notes", "❓ Generate Quiz", "📚 Generate Flashcards"]
selected_tab = st.radio(
    "📍 Navigation", tabs,
    index=tabs.index(st.session_state.active_tab),
    horizontal=True
)


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Explain Topic
# ════════════════════════════════════════════════════════════════════════════
if selected_tab == "📘 Explain Topic":
    st.title("📘 Explain Topic")
    topic = st.text_input("Enter a topic to explain:", key="topic_input")

    if st.button("Explain", key="explain_btn"):
        if topic.strip():
            with st.spinner("Generating explanation..."):
                explanation = explain_topic(topic)
                st.session_state.explanation = explanation
                # Clear downstream results when a new topic is explained
                st.session_state.summary = ""
                st.session_state.quiz = ""
                st.session_state.quiz_parsed = None
                st.session_state.quiz_shuffled = None
                st.session_state.flashcards = ""
                st.session_state.score = 0
                st.session_state.show_results = False
            st.success("✅ Explanation ready!")
        else:
            st.warning("Please enter a topic first.")

    if st.session_state.explanation:
        st.subheader("📘 Simplified Explanation")
        st.write(st.session_state.explanation)
        st.download_button("💾 Download Explanation", st.session_state.explanation, "explanation.txt")

        if st.button("➡ Summarize this Explanation"):
            with st.spinner("Summarizing..."):
                st.session_state.summary = summarize_text(st.session_state.explanation)
            st.success("📝 Summary generated successfully!")
            switch_to("📝 Summarize Notes")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Summarize Notes
# ════════════════════════════════════════════════════════════════════════════
elif selected_tab == "📝 Summarize Notes":
    st.title("📝 Summarize Notes")
    notes = st.text_area(
        "Paste or edit your notes:",
        value=st.session_state.summary or st.session_state.explanation
    )

    if st.button("Summarize", key="summarize_btn"):
        if notes.strip():
            with st.spinner("Summarizing..."):
                st.session_state.summary = summarize_text(notes)
            st.success("✅ Summary ready!")
        else:
            st.warning("Please paste some notes first.")

    if st.session_state.summary:
        st.subheader("📝 Summary")
        st.write(st.session_state.summary)
        st.download_button("💾 Download Summary", st.session_state.summary, "summary.txt")

        if st.button("➡ Generate Quiz from this Summary"):
            with st.spinner("Creating quiz..."):
                quiz_text = generate_quiz(st.session_state.summary, 5)
                st.session_state.quiz = quiz_text
                parsed = parse_quiz_text(quiz_text)
                st.session_state.quiz_parsed = parsed
                st.session_state.quiz_shuffled = shuffle_quiz(parsed)   # shuffle ONCE
                st.session_state.selected_answers = {}
                st.session_state.show_results = False
                st.session_state.score = 0
            st.success("✅ Quiz generated successfully!")
            switch_to("❓ Generate Quiz")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Interactive Quiz
# ════════════════════════════════════════════════════════════════════════════
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
                    st.session_state.quiz = quiz_text
                    parsed = parse_quiz_text(quiz_text)
                    st.session_state.quiz_parsed = parsed
                    st.session_state.quiz_shuffled = shuffle_quiz(parsed)   # shuffle ONCE
                    st.session_state.selected_answers = {}
                    st.session_state.show_results = False
                    st.session_state.quiz_score = 0
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")
            st.success("✅ Quiz generated! Scroll below to attempt it.")
        else:
            st.warning("Please enter some text first.")

    # ── Display quiz form ─────────────────────────────────────────────────
    quiz_data = st.session_state.get("quiz_shuffled") or []

    if quiz_data:
        st.subheader("📘 Attempt the Quiz")

        with st.form("quiz_form", clear_on_submit=False):
            for i, q in enumerate(quiz_data):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                if q.get("options"):
                    st.radio(
                        "Choose your answer:",
                        q["options"],
                        index=None,
                        key=f"ans_{i}"
                    )
                else:
                    st.warning("_⚠️ No valid options detected for this question._")
                st.markdown("---")
            submitted = st.form_submit_button("✅ Submit Answers")

        # ── Evaluate on submit ────────────────────────────────────────────
        if submitted:
            score = 0
            results = []
            for i, q in enumerate(quiz_data):
                user_ans = st.session_state.get(f"ans_{i}")
                correct_letter = q.get("correct")
                correct_opt = None
                if correct_letter and correct_letter in ["A", "B", "C", "D"]:
                    idx = ord(correct_letter) - ord("A")
                    if 0 <= idx < len(q["options"]):
                        correct_opt = q["options"][idx]

                if user_ans and user_ans == correct_opt:
                    score += 1
                    results.append(f"✅ **Q{i+1}: Correct!** ({user_ans})")
                else:
                    results.append(
                        f"❌ **Q{i+1}: Wrong!**  Your: {user_ans or 'None'} | Correct: {correct_opt or 'N/A'}"
                    )

            st.session_state.show_results = True
            st.session_state.quiz_results = results
            st.session_state.quiz_score = score

    elif st.session_state.quiz:
        st.warning("⚠️ Could not parse quiz questions. Try generating again with different text.")
    else:
        st.info("👇 Generate a quiz above, answer all questions, then click **Submit Answers**.")

    # ── Results ───────────────────────────────────────────────────────────
    if st.session_state.get("show_results") and quiz_data:
        st.subheader("🏁 Quiz Results")
        for r in st.session_state.quiz_results:
            st.markdown(r)
        st.success(f"**Final Score:** {st.session_state.quiz_score} / {len(quiz_data)}")

        if st.button("➡ Generate Flashcards from this Quiz", key="quiz_to_flashcards"):
            with st.spinner("Generating flashcards..."):
                try:
                    flashcards_text = generate_flashcards(
                        st.session_state.summary or st.session_state.explanation, 5
                    )
                    st.session_state.flashcards = flashcards_text
                    st.success("📚 Flashcards generated! Switch to the 'Generate Flashcards' tab.")
                except Exception as e:
                    st.error(f"Error generating flashcards: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Flashcards
# ════════════════════════════════════════════════════════════════════════════
elif selected_tab == "📚 Generate Flashcards":
    st.title("📚 Study Flashcards")
    flash_text = st.text_area(
        "Paste study notes:",
        value=st.session_state.summary or st.session_state.explanation
    )
    num_cards = st.slider("Number of flashcards:", 3, 10, 5)

    if st.button("Generate Flashcards", key="flash_btn"):
        if flash_text.strip():
            with st.spinner("Generating flashcards..."):
                st.session_state.flashcards = generate_flashcards(flash_text, num_cards)
            st.success("✅ Flashcards ready!")
        else:
            st.warning("Please paste some notes first.")

    if st.session_state.flashcards:
        st.subheader("🎴 Your Flashcards")
        # Render each card in a styled box
        cards_raw = st.session_state.flashcards.strip().split("\n")
        for line in cards_raw:
            line = line.strip()
            if line.startswith("Q:"):
                st.markdown(f"**{line}**")
            elif line.startswith("A:"):
                st.markdown(f"> {line}")
            elif line:
                st.markdown(line)
        st.download_button("💾 Download Flashcards", st.session_state.flashcards, "flashcards.txt")


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="text-align:center; color:gray; font-size:0.9rem;">
  Made with ❤️ by <b>Aditya Dorwal</b><br>
  Powered by <b>Google Gemini API</b> | IBM Internship Project
</div>
""", unsafe_allow_html=True)
