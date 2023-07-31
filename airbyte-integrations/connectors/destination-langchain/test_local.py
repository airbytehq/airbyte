#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

# Run with OPENAI_API_KEY set in the environment

embeddings = OpenAIEmbeddings()
vector_store = Chroma(embedding_function=embeddings, persist_directory="/tmp/airbyte_local/my_chroma_db")

# print(vector_store.similarity_search("python", 1))

qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())

print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
