from transformers import pipeline

def get_lyrics_mood(printResults = False):
    # Load the text classification pipeline with a pre-trained model
    pipe = pipeline("text-classification", model='nickwong64/bert-base-uncased-poems-sentiment')

    # Example text
    text = """
When your day is long
And the night, the night is yours alone
When you're sure you've had enough
Of this life, well hang on
Don't let yourself go
'Cause everybody cries
Everybody hurts sometimes
Sometimes everything is wrong
Now it's time to sing along
When your day is night alone (hold on, hold on)
If you feel like letting go (hold on)
If you think you've had too much
Of this life, well hang on
'Cause everybody hurts
Take comfort in your friends
Everybody hurts
Don't throw your hand, oh no
Don't throw your hand
If you feel like you're alone
No, no, no, you are not alone
If you're on your own in this life
The days and nights are long
When you think you've had too much
Of this life to hang on
Well, everybody hurts sometimes
Everybody cries
Everybody hurts, sometimes
And everybody hurts sometimes
So hold on, hold on
Hold on, hold on, hold on
Hold on, hold on, hold on
Everybody hurts
    """

    # Split text into lines
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)

    # Classify each line and collect results
    results_per_line = []
    positive_count = 0
    negative_count = 0
    no_impact_count = 0
    mixed_count = 0

    for line in lines:
        result = pipe(line)[0]
        score = result['score']
        label = result['label']

        if label == 'positive':
            positive_count += 1
        elif label == 'negative':
            negative_count += 1
        elif label == 'no_impact':
            no_impact_count += 1
        elif label == 'mixed':
            mixed_count += 1

        results_per_line.append((line, score, label))

    # Calculate percentage of NO_IMPACT labels
    total_labels = positive_count + negative_count + no_impact_count + mixed_count
    positive_percentege = (positive_count / total_labels) * 100
    negative_percentege = (negative_count / total_labels) * 100
    mixed_percentage = (mixed_count / total_labels) * 100
    no_impact_percentage = (no_impact_count / total_labels) * 100
                    
    if printResults:
        # Print results for each line
        print("Results for each line:")
        for line_result in results_per_line:
            line, score, label = line_result
            print(f"Line: {line} | Score: {score:.4f} | Label: {label}")

        # Print sentiment count
        print("\nSentiment counts:")
        print(f"Positive: {positive_count}")
        print(f"Negative: {negative_count}")
        print(f"Mixed: {mixed_count}")
        print(f"No Impact: {no_impact_count}")


        # Check if no_impact_percentage exceeds 75%
        if no_impact_percentage > 75:
            print("\nPrioritize Sound Dawg")
        elif positive_percentege > 75:
            print("\nThis may be positive")
        elif negative_percentege > 75:
            print("\nPrioritze Lyrics")
        elif mixed_percentage > 75:
            print("\nMixed Feelings dawg")

        print("{0}% positive, {1}% negative, {2}% mixed, {3}% no impact".format(positive_percentege, negative_percentege, mixed_percentage, no_impact_percentage))
        
    if (text.strip() != None) or (text.strip() != ""): 
        return(positive_percentege, negative_percentege, mixed_percentage, no_impact_percentage)
    else:
        return None

if __name__ == "__main__":
    get_lyrics_mood(True)