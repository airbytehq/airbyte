#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import pinecone
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone

# Run with OPENAI_API_KEY, PINECONE_KEY and PINECONE_ENV set in the environment

embeddings = OpenAIEmbeddings()
pinecone.init(api_key=os.environ["PINECONE_KEY"], environment=os.environ["PINECONE_ENV"])
index = pinecone.Index("testdata")
vector_store = Pinecone(index, embeddings.embed_query, "text")


# Playing with a Github issue search use case

# prompt_template = """You are a question-answering bot operating on Github issues. Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. In the end, state the issue number you based your answer on.

# {context}

# Question: {question}
# Helpful Answer:"""
# prompt = PromptTemplate(
#     template=prompt_template, input_variables=["context", "question"]
# )
# document_prompt = PromptTemplate(input_variables=["page_content", "number"], template="{page_content}, issue number: {number}")
# qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever(), chain_type_kwargs={"prompt": prompt, "document_prompt": document_prompt})

qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())

print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
