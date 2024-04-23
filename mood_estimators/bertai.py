from transformers import pipeline

def get_lyrics_mood(text, printResults = False):
    # Load the text classification pipeline with a pre-trained model
    pipe = pipeline("text-classification", model='nickwong64/bert-base-uncased-poems-sentiment')

    # Example text
#     text = """
# When your day is long
# And the night, the night is yours alone
# When you're sure you've had enough
# Of this life, well hang on
# Don't let yourself go
# 'Cause everybody cries
# Everybody hurts sometimes
# Sometimes everything is wrong
# Now it's time to sing along
# When your day is night alone (hold on, hold on)
# If you feel like letting go (hold on)
# If you think you've had too much
# Of this life, well hang on
# 'Cause everybody hurts
# Take comfort in your friends
# Everybody hurts
# Don't throw your hand, oh no
# Don't throw your hand
# If you feel like you're alone
# No, no, no, you are not alone
# If you're on your own in this life
# The days and nights are long
# When you think you've had too much
# Of this life to hang on
# Well, everybody hurts sometimes
# Everybody cries
# Everybody hurts, sometimes
# And everybody hurts sometimes
# So hold on, hold on
# Hold on, hold on, hold on
# Hold on, hold on, hold on
# Everybody hurts
#     """

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
        return {"positive_percentage": round(positive_percentege / 100, 2), "negative_percentage": round(negative_percentege / 100, 2), "mixed_percentage": round(mixed_percentage / 100, 2), "no_impact_percentage": round(no_impact_percentage / 100, 2)}
    else:
        return None

if __name__ == "__main__":
    Text = """
    Are you alright?
I'm alright, I'm quite alright
And my money's right
8, yeah
Countin' them bands all way to the top, 'til they be fallin' over
Countin' them bands on my way to the top, 'til we fallin' over

I don't really care if you cry
On the real you should've never lied
Should've saw the way she looked me in my eyes
She said, "Baby, I am not afraid to, die"
Push me to the edge
All my friends are dead
Push me to the edge
All my friends are dead
Push me to the edge
All my friends are dead
Push me to the edge

Phantom that's all red
Inside all white
Like something you ride a sled down
I just want that head
My Brittany got mad
I'm barely her man now
Everybody got the same swag now
Watch the way that I tear it down
Stacking my bands all the way to the top
All the way 'til my bands fallin' over
Every time that you leave your spot
Your girlfriend call me like "Come on over"
I like the way that she treat me
Gon' leave you, won't leave me
I call it that Casanova
She say I'm insane yeah
I might blow my brain out
Xanny help the pain, yeah
Please, Xanny make it go away
I'm committed, not addicted but it keep control of me
All the pain, now I can't feel it, I swear that it's slowing me, yeah

I don't really care if you cry
On the real, you should've never lied
Saw the way she looked me in my eyes
She said, "I am not afraid to, die"
All my friends are dead
Push me to the edge
All my friends are dead
Push me to the edge
All my friends are dead, yeah
All my friends are dead, yeah

That is not your swag, I swear you fake hard
Now these niggas wanna take my cadence
Rain on 'em, thunderstorm, rain on 'em
Medicine, little nigga take some
Fast car, Nascar, race 'em
In the club, ain't got no ones, then we would beg them
Clothes from overseas
Got the racks and they all C-Notes
You is not a G, though
Looking at you stackin' all your money, it all green though
I was counting that and these all twenties, that's a G-roll

She say, "You're the worst, you're the worst"
I cannot die, because this my universe

I don't really care if you cry
On the real, you should've never lied
Should've saw the way she looked me in my eyes
She said, "Baby, I am not afraid to, die"
Push me to the edge
All my friends are dead
Push me to the edge
All my friends are dead
Push me to the edge
All my friends are dead
Push me to the edge

    """
    get_lyrics_mood(Text, True)