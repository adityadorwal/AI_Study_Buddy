# 🧠 AI Study Buddy  
### Your Personal AI Learning Assistant — Powered by Google Gemini & Streamlit  

[![Streamlit App](https://img.shields.io/badge/Live%20App-Open-success?logo=streamlit)](https://aistudybuddy-nwl9vb6xza4ekmz3znh8g8.streamlit.app/)
[![GitHub repo size](https://img.shields.io/github/repo-size/adityadorwal/AI_Study_Buddy?color=blue)](https://github.com/adityadorwal/AI_Study_Buddy)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📘 Overview  

**AI Study Buddy** is an intelligent learning assistant that helps students and learners understand, summarize, and revise topics faster.  
It leverages **Google Gemini’s Generative AI** to perform tasks like:
- 🧩 Explaining complex topics  
- ✂️ Summarizing long texts  
- 🧠 Generating quizzes  
- 🪪 Creating flashcards for revision  

Built using **Streamlit**, it features a clean, intuitive interface that works both locally and online.  

---

## 🚀 Live Demo  
👉 **Try it now:**  
🔗 [AI Study Buddy App](https://aistudybuddy-nwl9vb6xza4ekmz3znh8g8.streamlit.app/)

---

## 🏗️ Project Structure  

```

AI_Study_Buddy/
│
├── AI_Study_Buddy-main/
│   ├── README.md
│   ├── requirements.txt
│   ├── .gitignore
│   │
│   ├── backend/
│   │   ├── **init**.py
│   │   └── study_tools.py       # Core AI logic using Google Gemini
│   │
│   └── frontend/
│       └── app.py               # Streamlit app for UI & integration
│
└── Deployed via Streamlit Cloud

````

---

## 🧩 Features  

✅ **Explain Any Topic** – Input a topic, and get a clear, structured explanation.  
✅ **Summarize Text** – Paste any long text and get concise key points.  
✅ **Generate Quizzes** – Create comprehension-based MCQs or short questions.  
✅ **Flashcards** – Automatically create topic-based flashcards for revision.  
✅ **Responsive UI** – Built with Streamlit for simplicity and instant deployment.  

---

## 🧠 Tech Stack  

| Layer | Technology |
|-------|-------------|
| Frontend | Streamlit |
| Backend | Python |
| AI Model | Google Gemini (via `google-generativeai`) |
| Environment | Python-dotenv |
| Deployment | Streamlit Community Cloud |

---

## ⚙️ Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/adityadorwal/AI_Study_Buddy.git
cd AI_Study_Buddy/AI_Study_Buddy-main
````

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate      # On Windows
# or
source venv/bin/activate   # On Mac/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up Environment Variable

Create a `.env` file in the project root and add:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 5️⃣ Run the App

```bash
streamlit run frontend/app.py
```

---

## 🖼️ Screenshots

| Feature            | Screenshot                                                                                |
| ------------------ | ----------------------------------------------------------------------------------------- |
| Home Interface     | ![Home Screenshot](https://github.com/adityadorwal/AI_Study_Buddy/assets/home.png) |
| Explanation Output | ![Explanation](https://github.com/adityadorwal/AI_Study_Buddy/assets/summary.png)     |
| Quiz & Flashcards  | ![Quiz Flashcards](https://github.com/adityadorwal/AI_Study_Buddy/assets/quiz.png) |

*(You can add screenshots from your Streamlit app later by uploading to GitHub Issues → copy link → paste here.)*

---

## 🧩 Key Python Files

### `backend/study_tools.py`

* Contains core logic using `google.generativeai`.
* Functions:

  * `explain_topic()`
  * `summarize_text()`
  * `generate_quiz()`
  * `generate_flashcards()`

### `frontend/app.py`

* Streamlit app interface with tabs for each feature.
* Imports backend functions and displays responses interactively.

---

## 💡 Future Improvements

🔹 Add **voice input/output** support
🔹 Enable **offline mode** (local LLM integration)
🔹 Add **notes storage & PDF export**
🔹 Multi-language support

---

## 👨‍💻 Author

**Aditya Dorwal**
📧 [Email](18dorwaladitya@gmail.com) | 🌐 [GitHub](https://github.com/adityadorwal)

---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).
You are free to use, modify, and distribute it with proper attribution.
---
