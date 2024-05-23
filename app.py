import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import process, fuzz
import pandas as pd
import re
import numpy as np
import seach_functions
import ast

app = Flask(__name__)
CORS(app)



def clean_poem_format(poem):
    poem = re.sub(r'[\r\n]+', '\n', poem)
    poem = "\n".join(line.strip() for line in poem.split('\n'))
    poem = re.sub(r'\n+', '\n', poem)
    poem = poem.strip()
    return poem

poems = pd.read_csv("poems_final.csv")
poems = poems.replace({np.nan: None})
poems = poems.dropna()

@app.route('/classify_poem', methods=['POST'])
def classify_poem():
    data = request.json
    query = data.get('query', '').lower()
    matched_poems = seach_functions.search_poems_by_emotion(query, poems)

    if not matched_poems.empty:
        results = [{
            "poem": poem,
            "emotion_vector": vector,
            "title": title,
            "poet": poet
        } for poem, vector, title, poet in zip(matched_poems['Poem'], matched_poems['emotion_vector'], matched_poems['Title'],
                                matched_poems['Poet'])]
    else:
        results = [{"poem": "No matching poems found.", "emotion_vector": []}]
    return jsonify(results)

@app.route('/find_by_author', methods=['POST'])
def find_by_author():
    data = request.json
    query = data.get('query', '').upper()
    poets = poems['Poet'].unique()

    if query in poets:
        poems_by_author = poems[poems['Poet'].str.upper() == query.upper()].dropna()
        results = [{
            "poem": poem,
            "emotion_vector": eval(vector),
            "title": title,
            "poet": poet
        } for poem, vector, title, poet in zip(poems_by_author['Poem'], poems_by_author['emotion_vector'], poems_by_author['Title'],
                                poems_by_author['Poet'])]
    else:
        closest_match = process.extractOne(query, poets, scorer=fuzz.token_sort_ratio)
        if closest_match and closest_match[1] > 40:
            closest_author = closest_match[0]
            poems_by_author = poems[poems['Poet'] == closest_author].dropna()
            results = [{
                "poem": poem,
                "emotion_vector": eval(vector),
                "title": title,
                "poet": poet
            } for poem, vector, title, poet in zip(poems_by_author['Poem'], poems_by_author['emotion_vector'], poems_by_author['Title'],
                                    poems_by_author['Poet'])]

        else:
            results = [{"poem": "No poems found by this author.", "emotion_vector": []}]

    return jsonify(results)

@app.route('/find_by_title', methods=['POST'])
def find_by_title():
    data = request.json
    query = data.get('query', '').upper()
    poems['Title'] = poems['Title'].apply(lambda x: x.upper())
    titles = poems['Title'].unique().tolist()

    if query in titles:
        poems_by_title = poems[poems['Title'] == query.upper()].dropna()
        results = [{
            "poem": poem,
            "emotion_vector": eval(vector),
            "title": title,
            "poet": poet
        } for poem, vector, title, poet in zip(poems_by_title['Poem'], poems_by_title['emotion_vector'], poems_by_title['Title'],
                                    poems_by_title['Poet'])]
    else:
        closest_match = process.extractOne(query, poems['Title'], scorer=fuzz.token_sort_ratio)
        if closest_match and closest_match[1] > 60:
            closest_title = closest_match[0]
            poems_by_title = poems[poems['Title'] == closest_title].dropna()
            results = [{
                "poem": poem,
                "emotion_vector": eval(vector),
                "title": title,
                "poet": poet
            } for poem, vector, title, poet in zip(poems_by_title['Poem'], poems_by_title['emotion_vector'], poems_by_title['Title'],
                                    poems_by_title['Poet'])]
        else:
            results = [{"poem": "No poems found with this title.", "emotion_vector": []}]

    return jsonify(results)
@app.route('/find_by_BM25', methods=['POST'])
def find_by_BM25():
    data = request.json
    query = data.get('query', '')
    matched_poems = seach_functions.search_poems_by_query(query, poems)

    if not matched_poems.empty:
        results = [{
            "poem": poem,
            "emotion_vector": eval(vector),
            "title": title,
            "poet": poet
        } for poem, vector, title, poet in zip(matched_poems['Poem'], matched_poems['emotion_vector'], matched_poems['Title'],
                                matched_poems['Poet'])]
    else:
        return jsonify({"poems": ["No matching poems found."], "emotion_vector": []})

    return jsonify(results)

@app.route('/get_poem_interpretation', methods=['POST'])
def get_poem_interpretation():
    data = request.json
    poem = data.get('poem', '')
    interpretation = seach_functions.get_poem_interpretation(poem)
    return jsonify({"interpretation": interpretation})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


