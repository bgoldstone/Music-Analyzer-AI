from transformers import pipeline
import torch

# Load the text classification pipeline with a pre-trained model
pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# Example text
text = """
The sun is shining, and the birds are singing.
I lost my keys again, what a frustrating day.
It feels so good to be surrounded by friends.
Stuck in traffic again, I'll never get home.
The smell of fresh-baked cookies fills the air.
I can't stop smiling since I heard the good news!
Raindrops pattering against the window, a cozy day inside.
Feeling overwhelmed with all the work piling up.
A warm hug from a loved one makes everything better.
Another rejection letter, back to the drawing board.
Waking up to a beautiful sunrise, ready to seize the day.
Feeling a bit under the weather, but pushing through.
Watching my favorite movie always lifts my spirits.
Getting a compliment from a stranger brightened my day.
Sipping hot cocoa by the fireplace, pure bliss.
A disagreement with a friend left me feeling uneasy.
"A surprise visit from an old friend made my day."
Struggling to find motivation to tackle my to-do list.
The anticipation of a new adventure fills me with excitement.
A heartfelt apology healed a rift in our relationship.
"""

# Split text into lines
lines = []
for line in text.split('\n'):
    line = line.strip()
    if line:
        lines.append(line)

# Classify each line and collect results
results_per_line = []
for line in lines:
    result = pipe(line)[0]
    score = result['score']
    label = result['label']
    results_per_line.append((line, score, label))

# Print results for each line
print("Results for each line:")
for line_result in results_per_line:
    line, score, label = line_result
    print(f"Line: {line} | Score: {score:.4f} | Label: {label}")

# Calculate mean score
mean_score = sum(score for _, score, _ in results_per_line) / len(results_per_line)

# Determine overall sentiment
overall_sentiment = "Positive" if mean_score >= 0.5 else "Negative"

# Print mean score and overall sentiment
print(f"\nMean Score: {mean_score:.4f}")
print(f"Overall Sentiment: {overall_sentiment}")
