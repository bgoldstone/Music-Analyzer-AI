import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download NLTK resources (run once)
nltk.download('vader_lexicon')

# Sentiment Analyzer
sid = SentimentIntensityAnalyzer()

# Example song lyrics
lyrics = """
im so happy

im so sad

im ok

hello darkness my old friend

idk how i feel 

im so excited

"""

# Split lyrics into lines
lines = []
for line in lyrics.split('\n'):
    line = line.strip()
    if line:
        lines.append(line)

# Analyze sentiment of each line
mood_per_line = []
polarity_scores = []

for line in lines:
    sentiment_scores = sid.polarity_scores(line)
    polarity_scores.append(sentiment_scores['compound'])  # Collect compound scores for each line

    if sentiment_scores['compound'] >= 0.5:
        mood = 'Positive'
    elif sentiment_scores['compound'] <= -1.0:
        mood = 'Negative'
    else:
        mood = 'Neutral'
    mood_per_line.append((line, mood))

# Print sentiment analysis for each line
for line, mood in mood_per_line:
    print(f"Line: {line} | Mood: {mood}")

# Calculate the mean of all the scores
mean_score = sum(polarity_scores) / len(polarity_scores)
print(f"\nMean Polarity Score: {mean_score:.4f}")