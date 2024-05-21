

import torch
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from transformers import BitsAndBytesConfig
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.core.indices import SummaryIndex



llm = HuggingFaceLLM(
    model_name="mistralai/Mistral-7B-Instruct-v0.1",
    tokenizer_name="mistralai/Mistral-7B-Instruct-v0.1",
    query_wrapper_prompt=PromptTemplate("<s>[INST] {query_str} [/INST] </s>\n"),
    context_window=3900,
    max_new_tokens=256,
    #model_kwargs={"quantization_config": quantization_config},
    # tokenizer_kwargs={},
    generate_kwargs={"temperature": 0.2, "top_k": 5, "top_p": 0.95},
    device_map="auto",
)



Settings.llm = llm
Settings.embed_model = "local:BAAI/bge-small-en-v1.5"
documents = SimpleDirectoryReader("../data").load_data()
vector_index = VectorStoreIndex.from_documents(documents)
query_engine = vector_index.as_query_engine(response_mode="compact")

response = query_engine.query("Analyze the emotional content of the following text and output an emotion vector. "
                              "The vector should represent the intensity of each emotion on a scale from 0 to 1 for the "
                              "following emotions: Happiness, Sadness, Fear, Disgust, Anger, Surprise, Anticipation, "
                              "Trust, Distrust, Love, Saudade, Awe, Bittersweetness, Melancholy, Nostalgia. "
                              "The format of the vector should be: [Happiness, Sadness, Fear, Disgust, Anger,"
                              "Surprise, Anticipation, Trust, Distrust, Love, Saudade, Awe, Bittersweetness, "
                              "Melancholy, Nostalgia]. For example, if a text is moderately happy, slightly sad, "
                              "and not displaying any other emotions, the vector might look like "
                              "[0.5, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0].")
print(response)
display_response(response)