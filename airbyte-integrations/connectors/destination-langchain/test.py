from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import DocArrayHnswSearch
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vector_store = DocArrayHnswSearch.from_params(embeddings, "/tmp/airbyte_local/my_hnsw_index", 1536)

qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())

print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
