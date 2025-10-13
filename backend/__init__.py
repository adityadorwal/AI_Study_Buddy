
if __name__ == "__main__":
    print("🧠 AI Study Buddy — Backend Test\n")

    topic = input("Enter a topic to explain: ")
    print("\n📘 Explanation:\n", explain_topic(topic))

    text = input("\nPaste some text or short notes to summarize:\n")
    print("\n📝 Summary:\n", summarize_text(text))

    print("\n❓ Quiz:\n", generate_quiz(text))
    print("\n🎴 Flashcards:\n", generate_flashcards(text))
