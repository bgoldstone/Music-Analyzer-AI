from transformers import pipeline

def get_lyrics_mood():
    # Load the text classification pipeline with a pre-trained model
    pipe = pipeline("text-classification", model='nickwong64/bert-base-uncased-poems-sentiment')

    # Example text
    text = """
    It might seem crazy what I'm 'bout to say
    Sunshine, she's here, you can take a break
    I'm a hot air balloon that could go to space
    With the air like I don't care, baby, by the way
    Clap along if you feel like a room without a roof
    (Because I'm happy)
    Clap along if you feel like happiness is the truth
    (Because I'm happy)
    Clap along if you know what happiness is to you
    (Because I'm happy)
    Clap along if you feel like that's what you wanna do
    Here come bad news talking this and that (yeah)
    Well, give me all you got and don't hold it back (yeah)
    Well, I should probably warn you I'll be just fine (yeah)
    No offense to you, don't wanna waste your time
    Here's why
    Clap along if you feel like a room without a roof
    (Because I'm happy)
    Clap along if you feel like happiness is the truth
    (Because I'm happy)
    Clap along if you know what happiness is to you
    (Because I'm happy)
    Clap along if you feel like that's what you wanna do
    Bring me down, can't nothing (happy)
    Bring me down, my level's too high (happy)
    Bring me down, can't nothing (happy)
    Bring me down, I said (I tell you)
    Bring me down, can't nothing (happy, happy, happy)
    Bring me down, my level's too high (happy, happy, happy)
    Bring me down, can't nothing (happy, happy)
    Bring me down, I said (happy, happy)
    Clap along if you feel like a room without a roof
    (Because I'm happy)
    Clap along if you feel like happiness is the truth
    (Because I'm happy)
    Clap along if you know that happiness is to you
    (Because I'm happy)
    Clap along if you feel like that's what you wanna do
    Clap along if you feel like a room without a roof
    (Because I'm happy)
    Clap along if you feel like happiness is the truth
    (Because I'm happy)
    Clap along if you know that happiness is to you
    (Because I'm happy)
    Clap along if you feel like that's what you wanna do
    Bring me down, can't nothing (happy, happy, happy)
    Bring me down, my level's too (happy, happy, happy)
    Bring me down, can't nothing (happy, happy, happy)
    Bring me down, I said (happy, happy, happy)
    Clap along if you feel like a room without a roof
    (Because I'm happy)
    Clap along if you feel like happiness is the truth
    (Because I'm happy)
    Clap along if you know what happiness is to you
    (Because I'm happy)
    Clap along if you feel like that's what you wanna do
    Clap along if you feel like a room without a roof
    (Because I'm happy)
    Clap along if you feel like happiness is the truth
    (Because I'm happy)
    Clap along if you know what happiness is to you
    (Because I'm happy)
    Clap along if you feel like that's what you wanna do
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

    printResults = True                    
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

    print(positive_percentege, negative_percentege, mixed_percentage, no_impact_percentage)
    # {'one':1, 'two':2, 'three':3}
    return(positive_percentege, negative_percentege, mixed_percentage, no_impact_percentage)

if __name__ == "__main__":
    get_lyrics_mood()