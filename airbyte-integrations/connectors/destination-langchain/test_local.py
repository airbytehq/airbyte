#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import DocArrayHnswSearch

# Run with OPENAI_API_KEY set in the environment

embeddings = OpenAIEmbeddings()
vector_store = DocArrayHnswSearch.from_params(embeddings, "/tmp/airbyte_local/special_path", 1536)

# print(vector_store.similarity_search("python", 1))

qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())

print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
