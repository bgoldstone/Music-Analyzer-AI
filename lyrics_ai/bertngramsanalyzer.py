from transformers import pipeline
import torch

# Load the text classification pipeline with a pre-trained model
pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# Example text
text = """
Can I call you Rose? (Can I call you Rose?)
'Cause you're sweet like a flower in bloom
(Can I call you Rose?)
Can I call you Rose? (Can I call you Rose?)
'Cause your fragrance takes over the room, darling
(Can I call you Rose?)
I wanna plant you in my heart, oh
So love can grow
Can I call you Rose? (Can I call you Rose?)
'Cause your thorns won't let love in too soon
(Can I call you Rose?)
Can I call you Rose? (Can I call you Rose?)
'Cause your roots have the power to consume me
(Can I call you Rose?)
I wanna plant you in my heart, oh-oh
So love can grow
I was meditating on love and you and roses
And the universe told me, "Put it in a love song"
Oh, Rose
(Put it in a love song, put it in a love, put it in a love song)
Oh, Rose
(Put it in a love song, put it in a love, put it in a love song)
(Put it in a love song, put it in a love, put it in a love song)
Won't you let me in your heart?
(Put it in a love song, put it in a love, put it in a love song)
Your heart
(Put it in a love song, put it in a love, put it in a love song)
Oh, your heart
(Put it in a love song, put it in a love, put it in a love song)
(Put it in a love song, put it in a love, put it in a love song)
"""

# Split text into lines
lines = []
for line in text.split('\n'):
    line = line.strip()
    if line:
        lines.append(line)


# Analyze sentiment and n-grams for each line
results_per_line = []
for line in lines:
    # Analyze sentiment
    sentiment_result = pipe(line)
    sentiment_score = sentiment_result[0]['score']
    sentiment_label = sentiment_result[0]['label']
    
    # Analyze n-grams
    ngrams = [line[i:i+3] for i in range(len(line) - 2)]
    
    # Append results for the current line to the list
    results_per_line.append((line, sentiment_score, sentiment_label, ngrams))

# Print results for each line
print("Results for each line:")
for line_result in results_per_line:
    line, score, label, ngrams = line_result
    print(f"Line: {line} | Sentiment Score: {score:.4f} | Sentiment Label: {label} | N-grams: {ngrams}")

# Calculate mean score
mean_score = sum(score for _, score, _, _ in results_per_line) / len(results_per_line)

# Determine overall sentiment
if mean_score >= 0.5:
    overall_sentiment = "Positive"
elif mean_score <= -0.5:
    overall_sentiment = "Negative"
else:
    overall_sentiment = "Neutral"

# Print mean score and overall sentiment
print(f"\nMean Score: {mean_score:.4f}")
print(f"Overall Sentiment: {overall_sentiment}")