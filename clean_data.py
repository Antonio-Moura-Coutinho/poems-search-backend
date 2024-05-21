import os
import pandas as pd
import numpy as np
import re
poems_final = pd.read_csv("poems_final.csv")

poems_english = pd.read_csv("poems_english.csv")



def clean_poem_format(poem):
    formatted_poem = re.sub(r'([.!?])\s*', r'\1\n', poem)
    if "Copyright" in poem and len(poem) < 300:
        formatted_poem = None
    return formatted_poem
poems_final['Poem'] = poems_final['Poem'].apply(clean_poem_format)
poems_final = poems_final.dropna()
poems_final.to_csv("poems_final.csv", index=False)
poems_english.to_csv("poems_english_old.csv", index=False)
poems_english['Poem'] = poems_english['Poem'].apply(clean_poem_format)
poems_english = poems_english.dropna()
poems_english.to_csv("poems_english.csv", index=False)
def old1():
    poems_english['Poet'] = poems_english['author'].apply(lambda x: x.upper())
    poems_authors = poems_english[['Poet']].drop_duplicates()
    poems_english['Title'] = poems_english['poem name']
    poems_english['Poem'] = poems_english['content']
    poems_english['Font'] = 'english_classic'
    poems_english = poems_english[['Title', 'Poem', 'Poet', 'Font']]
    poems_english.reset_index(drop=True, inplace=True)
    poems_english['Id'] = poems_english.reset_index(drop=True).index + 15000
    poems_english.to_csv("poems_english.csv", index=False)
def old2():
    poems_english['Title'] = poems_english['Title'].apply(lambda x: 'No title' if (x == '' or  x is np.nan) else x)
    for poem in poems_english.iterrows():
        poem_txt = poem[1]['Poem']
        poem_title = poem[1]['Title']
        poem_author = poem[1]['Poet']
        id = poem[1]['Id']
        if not os.path.exists(f"by_author/{poem_author}"):
            os.makedirs(f"by_author/{poem_author}")
        if not os.path.exists(f"by_id"):
            os.makedirs(f"by_id")
        print(poem_title)
        if poem_title.replace("/", "_") != poem_title:
            poem_title = poem_title.replace("/", "_")
        with open(f"by_author/{poem_author}/{poem_title}.txt", "w") as f:
            f.write(poem_txt)
        with open(f"by_id/{id}.txt", "w") as f:
            f.write(poem_txt)
    poems_authors.to_csv("poems_authors.csv", index=False)
    poems = pd.read_csv("original_datasets/poetry.csv")
    for row in poems.iterrows():
        try:
            title = row[1]['poem name']
            author = row[1]['author']
            text = row[1]['content']
            txt_name = author + "_" + title + ".txt"
            with open(f"data/{txt_name}", "w") as f:
                    f.write(text)
        except:
            print("error", row[1]['poem name'], row[1]['author'])


