"""
AI Study Buddy — Backend Utilities
----------------------------------
Provides tools for:
1. Explaining topics clearly
2. Summarizing notes
3. Generating quizzes
4. Creating flashcards

Ready for GitHub and Streamlit integration.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# 🔐 Load environment variables
load_dotenv()

# ✅ Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ✅ Initialize model (latest stable)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# ------------------------------- #
# 🧠 Core AI Functions
# ------------------------------- #

def explain_topic(topic: str) -> str:
    """Explain a topic in simple terms with references."""
    prompt = f"""
    You are an AI study assistant.
    Explain the topic '{topic}' in a simple and structured way, easy for a beginner to grasp.
    Include analogies or examples if useful.
    If possible, suggest one relevant research paper and one YouTube video
    (include both title and channel name along with link).
    Keep the response focused — no unnecessary fluff.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error while generating explanation: {e}"


def summarize_text(text: str) -> str:
    """Summarize notes into bullet points."""
    prompt = f"""
    Summarize the following study notes into clear, concise bullet points.
    Preserve key concepts and make it easy to review.

    Notes:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error while summarizing: {e}"


def generate_quiz(text: str, num_questions: int = 5) -> str:
    """Generate MCQ quiz based on given study material."""
    prompt = f"""
    Create {num_questions} multiple-choice questions (MCQs) from the text below.
    Each question must have 4 options (A–D), with the correct answer marked.
    Randomize the order of options.

    Format strictly as:
    Question 1: <question>
    A) <option>
    B) <option>
    C) <option>
    D) <option>
    Correct Answer: <A/B/C/D>

    Study Material:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error while generating quiz: {e}"


def generate_flashcards(text: str, num_cards: int = 5) -> str:
    """Generate flashcards in Q/A format."""
    prompt = f"""
    Create {num_cards} short Q&A flashcards from the following study material.
    Format:
    Q: <question>
    A: <answer>

    Study Material:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error while generating flashcards: {e}"


if __name__ == "__main__":
    print("🧠 AI Study Buddy — Backend Test\n")

    topic = input("Enter a topic to explain: ")
    print("\n📘 Explanation:\n", explain_topic(topic))

    text = input("\nPaste some text or short notes to summarize:\n")
    print("\n📝 Summary:\n", summarize_text(text))

    print("\n❓ Quiz:\n", generate_quiz(text))
    print("\n🎴 Flashcards:\n", generate_flashcards(text))
