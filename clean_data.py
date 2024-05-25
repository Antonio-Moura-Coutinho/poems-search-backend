import os
import pandas as pd
import numpy as np
import re
from collections import Counter

from classify_with_open import convert_to_float_list

def create_word_counts_df(poems_total):
    # Concatenate all poems into a single string
    all_poems = ' '.join(poems_total['Poem'])

    # Tokenize the string into individual words
    words = all_poems.split()
    words = [word.lower() for word in words]

    # Count the frequency of each word
    word_counts = Counter(words)

    # Create a DataFrame from the word-count pairs
    word_counts_df = pd.DataFrame.from_dict(word_counts, orient='index').reset_index()
    word_counts_df.columns = ['word', 'count']
    return word_counts_df
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
def clean_poem_format(poem, max_line_length=70):
    formatted_poem = re.sub(r'([.!?:;\。])\s*', r'\1\n', poem)
    formatted_poem = re.sub(r',\s*([A-Z])', r',\n\1', formatted_poem)
    formatted_poem = re.sub(r'([a-z])([A-Z])', r'\1\n\2', formatted_poem)

    lines = formatted_poem.split('\n')
    formatted_poem = ''
    for line in lines:
        while len(line) > max_line_length:
            # Find the position to insert the line break
            break_pos = line.rfind(' ', 0, max_line_length)
            if break_pos == -1:
                break_pos = max_line_length
            formatted_poem += line[:break_pos] + '\n'
            line = line[break_pos:].strip()
        formatted_poem += line + '\n'

    return formatted_poem

    print(formatted_poem)


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
                if word_count >= max_words_per_line and re.match(r'[A-Z]', word):
                    formatted_lines.append(' '.join(new_line))
                    word_count = 0
                    new_line = []
                new_line.append(word)
                word_count += 1
                if word_count >= max_words_per_line and re.match(r'[.!?,;:]', word):
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

    list = [1760,1761,2924,3606,9235,9236,9237,9238,10280,11106,11996,12023,15378,15379,15400,15404,15412,15414,15420,15429,15507,15530,15532,15541]

    poems_ch_eng = pd.read_csv("poems_ch_eng.csv")
    poems_ch_eng = poems_ch_eng[poems_ch_eng['Title'] != 'Manau']
    delete = poems_ch_eng[poems_ch_eng['Id'].isin(list)]

    poems_ch_eng = poems_ch_eng[~poems_ch_eng['Id'].isin(list)]
    poems_ch_eng.to_csv("poems_ch_eng.csv", index=False)
    poems_less_words = poems_ch_eng[poems_ch_eng['Poem'].apply(lambda x: len(x.split()) < 20)]




