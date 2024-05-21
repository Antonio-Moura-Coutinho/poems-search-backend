# This is a sample Python script.



# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import os
import openai
import pandas as pd
import numpy as np
import pandas as pd
import chardet
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.indices import SummaryIndex
os.environ['OPENAI_API_KEY'] = "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"
openai.api_key = os.environ['OPENAI_API_KEY']

documents = SimpleDirectoryReader("../by_id").load_data()
index = VectorStoreIndex.from_documents(documents)
summary_index = SummaryIndex.from_documents(documents)
llm = OpenAI(model="gpt-3.5-turbo", temperature=0)

for doc in documents:
    # Convert the document to a string
    doc_string = str(doc)
    vector_index = VectorStoreIndex.from_documents(doc)
    query_engine = vector_index.as_query_engine(response_mode="compact")


    # Perform the query for the document
    response = query_engine.query("Analyze the emotional content of the following text and output an emotion vector. "
                              "The vector should represent the intensity of each emotion on a scale from 0 to 1 for the "
                              "following emotions: Happiness, Sadness, Fear, Disgust, Anger, Surprise, Anticipation, "
                              "Trust, Distrust, Love, Saudade, Awe, Bittersweetness, Melancholy, Nostalgia. "
                              "The format of the vector should be: [Happiness, Sadness, Fear, Disgust, Anger,"
                              "Surprise, Anticipation, Trust, Distrust, Love, Saudade, Awe, Bittersweetness, "
                              "Melancholy, Nostalgia]. For example, if a text is moderately happy, slightly sad, "
                              "and not displaying any other emotions, the vector might look like "
                              "[0.5, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0].")

    doc_name = doc.name
    response
    with open(f"results/{doc_name}.txt", "w") as f:
        f.write(response)


