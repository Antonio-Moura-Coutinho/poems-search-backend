import os
import pandas as pd
import numpy as np
import re

def process_poems(poems_final, poems_data, author, content, title, font='poems_data'):
    poems_data['Poet'] = poems_data[author].apply(lambda x: x.upper())
    poems_data['Poem'] = poems_data[content]
    poems_data['Title'] = poems_data[title]
    poems_data['Font'] = font
    poems_data = poems_data[['Title', 'Poem', 'Poet', 'Font']]
    poems_data.reset_index(drop=True, inplace=True)
    last_id = poems_final['Id'].max() if not poems_final.empty else 0
    poems_data['Id'] = poems_data.reset_index(drop=True).index + last_id + 5000
    poems_data.to_csv("poems_data.csv", index=False)
    poems_total = pd.concat([poems_final, poems_data])
    poems_total.to_csv("poems_total.csv", index=False)
    return poems_total
# process_poems(poems_final, 汉_poems, '作者', '内容', '题目', '汉')
# process_poems(poems_total, poems_portuguese, 'Poet', 'Poem', 'Title', 'portuguese')
def clean_poem_format(poem):
    formatted_poem = re.sub(r'([.!?])\s*', r'\1\n', poem)
    if "1999" in poem and len(poem) < 400:
        formatted_poem = None
    return formatted_poem
def insert_newlines_at_punctuation(poem, max_words_per_line):
    # Split the poem into lines
    lines = poem.split('\n')
    formatted_lines = []

    for line in lines:
        words = line.split()
        if len(words) <= max_words_per_line:
            formatted_lines.append(line)
        else:
            new_line = []
            word_count = 0
            for word in words:
                new_line.append(word)
                word_count += 1
                if word_count >= max_words_per_line and re.match(r'[.!?,;:]', word[-1]):
                    formatted_lines.append(' '.join(new_line))
                    new_line = []
                    word_count = 0
            if new_line:
                formatted_lines.append(' '.join(new_line))

    # Join the formatted lines back into a single string
    formatted_poem = '\n'.join(formatted_lines)
    return formatted_poem


def old2(poems):
    poems['Title'] = poems['Title'].apply(lambda x: 'No title' if (x == '' or  x is np.nan) else x)
    for poem in poems.iterrows():
        poem_txt = poem[1]['Poem']
        poem_txt = str(poem_txt)
        if poem_txt is None:
            continue
        poem_title = poem[1]['Title']
        poem_author = poem[1]['Poet']
        id = int(poem[1]['Id'])
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


if __name__ == '__main__':
    poems_final = pd.read_csv("poems_final.csv")

    poems_english = pd.read_csv("poems_english.csv")

    poems_portuguese = pd.read_csv("poems_portuguese.csv")
    poems_portuguese['Id'] = None
    poems_portuguese.to_csv("poems_portuguese.csv", index=False)

    poems_total = pd.read_csv("poems_total.csv")
    poems_total['Poem'] = poems_total['Poem'].replace({np.nan: 'APAGAR'})
    poems_total['Poem'] = poems_total['Poem'].apply(lambda x: insert_newlines_at_punctuation(x, 10))
    poems_final.to_csv("poems_final.csv", index=False)

    汉_poems = pd.read_csv("original_datasets/汉.csv")
    poems_total.dropna(subset=['Id'], inplace=True)
    poems_total['Id'] = poems_total['Id'].astype(int)
    poems_total.to_csv("poems_total.csv", index=False)

    poems_authors = poems_total['Poet'].drop_duplicates().reset_index(drop=True)
    poems_authors.to_csv("poems_authors.csv", index=False)


