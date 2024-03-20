import stanfordnlp

def get_lyric_mood(lyrics):
    # Load English language model
    nlp = stanfordnlp.Pipeline(lang='en', logging_level='ERROR')

    # Process lyrics
    doc = nlp(lyrics)

    # Analyze sentiment
    positive_count = 0
    negative_count = 0

    for sentence in doc.sentences:
        for token in sentence.tokens:
            if token.sentiment == 'Positive':
                positive_count += 1
            elif token.sentiment == 'Negative':
                negative_count += 1

    # Determine mood based on sentiment count
    if positive_count > negative_count:
        return 'positive'
    elif positive_count < negative_count:
        return 'negative'
    else:
        return 'neutral'

def main():
    # Example lyrics
    lyrics = """
    I'm walking on sunshine
    Oh-oh, and don't it feel good?
    Hey, alright now
    And don't it feel good?
    """

    # Analyze mood
    mood = get_lyric_mood(lyrics)
    print("The mood of the lyrics is:", mood)

if __name__ == "__main__":
    main()