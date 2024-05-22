import pandas as pd
import numpy as np
from openai import OpenAI
import os
import re
os.environ['OPENAI_API_KEY'] = "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"
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
def convert_to_float_list(vector_str):
    try:
        return [float(x) for x in vector_str.strip('[]').split(',')]
    except:
        return 'error'
def get_emotion_vector(poem_content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",
                 "content": f"Analyze the emotional content of the poem and output an emotion vector. "
                            "The vector represents the intensity of each emotion on a scale from 0 to 1 for the "
                            "following 15 emotions, in order: [Happiness, Sadness, Fear, Disgust, Anger, Surprise, Anticipation, "
                            "Trust, Guilt, Love, Saudade, Envy, Bittersweetness, Loneliness, Nostalgia]. "
                            "These emotions represent a broad spectrum of human feelings. "
                            "Follow the structure provided and reply ONLY with the vector. "
                            "\n\n"
                            "Example Poem:\n"
                            "\"\"\"\n"
                            "a bullet has passed through\n\n"
                            "spent the time elsewhere\n\n"
                            "to need, tenderly, potential\n\n"
                            "does not need to be bought, cannot\n\n"
                            "in fact refute the cause, rather catches\n"
                            "\"\"\"\n"
                            "Example Emotion Vector: [0, 0.4, 0, 0, 0, 0, 0.3, 0.2, 0, 0, 0, 0, 0.3, 0.4, 0.5]"
                            "\n\n"
                            "Poem:\n"
                            "\"\"\"\n"
                            f"{poem_content}"
                            "\"\"\"\n"
                            "Emotion Vector: "
                 }
            ],
            max_tokens=300)

        emotion_vector_string = response.choices[0].message.content.strip()
        emotion_vector = emotion_vector_string.split("[")[1].split("]")[0].split(",")


    except Exception as e:
        print(f"Failed to process {poem_content}: {str(e)}")
        emotion_vector = "Error processing poem"
    return emotion_vector

def get_poem_interpretation(poem_content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",
                 "content": f"Analyze the and translate it if it is not in english "
                            "Explain the poem, and provide an interpretation of its meaning. "
                            "Use this emotions to describe [Happiness, Sadness, Fear, Disgust, Anger, Surprise, Anticipation, "
                            "Trust, Guilt, Love, Saudade, Envy, Bittersweetness, Loneliness, Nostalgia]. "
                            "These emotions represent a broad spectrum of human feelings. "
                            "Reply ONLY with the analysis. "
                 }
            ],
            max_tokens=800)

        intrepretation = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Failed to process {poem_content}: {str(e)}")
        intrepretation = "Error processing poem"
    return intrepretation
def get_poems_by_emotion(emotion_vector, poems):
    poems_aux = poems.copy()
    poems_aux = poems_aux[poems_aux['Font'] == 'english_classic']
    emotion_vector = str(emotion_vector).replace("'", "")
    emotion_vector = convert_to_float_list(emotion_vector)
    poems_aux['emotion_vector'] = poems_aux['emotion_vector'].apply(lambda x: convert_to_float_list(x))
    emotion_vector = np.array(emotion_vector)

    poems_aux['distance'] = poems_aux['emotion_vector'].apply(lambda x: cos_sim(emotion_vector, np.array(x)))
    poems_aux = poems_aux.sort_values('distance', ascending=False)
    return poems_aux.head(20)

def search_poems_by_emotion(string, poems):
    emotion_vector = get_emotion_vector(string)
    poems = get_poems_by_emotion(emotion_vector, poems)
    return poems
def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)









