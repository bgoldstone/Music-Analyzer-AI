from transformers import pipeline

classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

sentences = ["I am not having a great day"]

# Classify emotions for the given sentence
predictions = classifier(sentences)

# Print the prediction in the desired format
print("[[")
for emotion in predictions[0]:
    print(emotion)
print("]]")