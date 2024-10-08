import os

import numpy as np
from openai import OpenAI
import json
import pandas as pd
import re
from flask import Flask, request, jsonify
import httpx


# Set OpenAI API key

client = OpenAI(
    
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def convert_to_float_list(vector_str):
    try:
        return [float(x) for x in vector_str.strip('[]').split(',')]
    except:
        return 'error'
def parse_emotion_vector(output):
    if output is None:
        return None
    if not isinstance(output, str):
        return None
    if output == "['Happiness', ' Sadness', ' Fear', ' Disgust', ' Anger', ' Surprise', ' Anticipation', ' Trust', ' Distrust', ' Love', ' Saudade', ' Awe', ' Bittersweetness', ' Melancholy', ' Nostalgia']":
        return None
    if len(output) < 15:
        return None

    # Define the list of emotions in the correct order
    emotions = [
        "Happiness", "Sadness", "Fear", "Disgust", "Anger",
        "Surprise", "Anticipation", "Trust", "Distrust", "Love",
        "Saudade", "Awe", "Bittersweetness", "Melancholy", "Nostalgia"
    ]

    # Try to find labeled values using regex
    labeled_values = re.findall(r'(\w+):\s*([\d\.]+)', output)

    if labeled_values:
        # Create a dictionary to store emotion values
        emotion_dict = {emotion: 0 for emotion in emotions}

        # Update the dictionary with the parsed values
        for label, value in labeled_values:
            if label in emotion_dict:
                if value.endswith('.'):
                    value = value[:-1]
                emotion_dict[label] = float(value)


        # Extract the values in the correct order
        return [emotion_dict[emotion] for emotion in emotions]

    # If no labeled values, try to parse a list of values
    try:
        # Extract the list from the string using regex
        list_match = re.search(r'\[([^\]]+)\]', output)
        if list_match:
            list_string = list_match.group(1)
            # Split the list values, strip quotes and spaces, and convert them to floats
            values = []
            for value in list_string.split(','):
                try:
                    float_value = float(value.strip().strip("'").strip('"').strip('.'))
                    values.append(float_value)
                except ValueError:
                    return None
            if len(values) == 15 and sum(values) > 0:
                return values


    except Exception as e:
        raise ValueError(f"Error parsing emotion vector: {str(e)} + {output}")

    return None


def classify_poem(poems_directory, list_of_poems=[]):
    # Loop through each text file in the poems directory
    results_directory = "results"
    if not os.path.exists(results_directory):
        os.makedirs(results_directory)

    for filename in sorted(os.listdir(poems_directory)):
        if filename.endswith(".txt"):
            filepath = os.path.join(poems_directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                poem_content = file.read()
            id = filename.split(".")[0]

            if int(id) not in list_of_poems and list_of_poems != []:
                continue
            # Use OpenAI to analyze the poem's emotional content
            try:
                response = client2.chat.completions.create(
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


                result_filepath = os.path.join(results_directory, f"{id}-results.txt")
                with open(result_filepath, 'w', encoding='utf-8') as result_file:
                    result_file.write(emotion_vector_string)
                vector = os.path.join(results_directory, f"{id}-vector.txt")
                with open(vector, 'w', encoding='utf-8') as vector_file:
                    vector_file.write(str(emotion_vector))

                print(f"Processed {filename} and saved results to {result_filepath}")


            except Exception as e:
                print(f"Failed to process {filename}: {str(e)}")
                emotion_vector = "Error processing poem"


    return poems_final

def read_vector_results(results_directory):
    for filename in os.listdir(results_directory):
        if filename.endswith("-vector.txt"):
            id = int(filename.split("-")[0])
            with open(os.path.join(results_directory, filename), 'r', encoding='utf-8') as vector_file:
                vector = vector_file.read()
                poems_final.loc[poems_final['Id'] == id, 'raw_emotion_vector'] = vector
    return poems_final

def clean_poems_final(poems_final):
    poems_final_classified = pd.read_csv("results_old/poems_final_classified.csv")
    poems_final_classified['emotion_vector'] = poems_final_classified['emotion_vector'].apply(convert_to_float_list)
    poems_final_classified['emotion_vector'] = poems_final_classified['emotion_vector'].apply(
        lambda x: None if x == 'error' else x)
    poems_final_classified['emotion_vector'] = poems_final_classified['emotion_vector'].apply(
        lambda x: None if x is None or sum(x) == 0 else x)
    poems_final_classified.to_csv("poems_final_classified.csv", index=False)


def clean_poem_format(poem):
    # Replace sequences of carriage returns and newlines with a single newline
    poem = re.sub(r'[\r\n]+', '\n', poem)
    # Strip leading and trailing whitespace from each line
    poem = "\n".join(line.strip() for line in poem.split('\n'))
    # Replace multiple newlines with a single newline
    poem = re.sub(r'\n+', '\n', poem)
    # Strip leading and trailing whitespace
    poem = poem.strip()
    return poem
def convert_to_float_list(vector_str):
    try:
        vector_str = str(vector_str)
        list= []
        for e in vector_str.split(','):
            e = e.strip()
            e = e.strip('[]')
            e = e.replace("'", "")
            print(e)
            list.append(float(e))
        if len(list) == 15 and sum(list) > 0:
            return list
        return None

    except:
        return None


if __name__ == '__main__':


    poems_directory = "by_id"
    results_directory = "results"
    poems_final = pd.read_csv("poems_total.csv")
    poems_final = read_vector_results(results_directory)
    poems_final.to_csv("poems_total.csv", index=False)
    poems_not_classified = poems_final[poems_final['raw_emotion_vector'].isnull()]

    poems_not_classified.to_csv("poems_not_classified.csv", index=False)
    list_of_poems = poems_not_classified['Id'].tolist()
    classify_poem(poems_directory, list_of_poems)








