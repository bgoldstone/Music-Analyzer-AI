import nltk

from nltk.sentiment import SentimentIntensityAnalyzer

# Download NLTK resources (run once)
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer
sid = SentimentIntensityAnalyzer()

# Example song lyrics
lyrics = "Put your loving hand out, baby \
I'm beggin' \
Beggin', beggin' you \
Put your loving hand out baby \
Beggin', beggin' you \
Put your loving hand out darlin'"

# Analyze sentiment of lyrics
sentiment_scores = sid.polarity_scores(lyrics)

# Determine mood based on sentiment score
if sentiment_scores["compound"] >= 0.05:
    mood = "Positive"
elif sentiment_scores["compound"] <= -0.05:
    mood = "Negative"
else:
    mood = "Neutral"

print("Mood of the song:", mood)
