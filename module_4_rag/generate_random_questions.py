import csv
import random

topics = ["science", "history", "technology", "mathematics", "geography", "literature", "sports", "art", "music", "cinema"]

# Define a pattern for generating questions
question_patterns = [
    "What are the key principles of {}?",
    "Who are the most influential figures in {}?",
    "How has {} evolved over the years?",
    "What are some common misconceptions about {}?",
    "Can you explain the theory of {}?",
    "What role does {} play in modern society?",
    "How does {} affect our daily lives?",
    "What are the future prospects of {}?",
    "What are the major challenges in {} today?",
    "How can one get started with {}?"
]

# Generate a list of 50 random questions
questions = []
for _ in range(50):
    topic = random.choice(topics)
    pattern = random.choice(question_patterns)
    question = pattern.format(topic)
    questions.append([question])


def main():
    # Define the file path
    file_path = './random_questions.csv'

    # Write the questions to a CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question"])  # Writing header
        writer.writerows(questions)

if __name__ == "__main__":
    main()
