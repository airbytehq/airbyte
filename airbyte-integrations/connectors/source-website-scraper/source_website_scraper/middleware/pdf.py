import requests
import uuid

from langchain_community.document_loaders.unstructured import UnstructuredFileIOLoader


class PdfDownloadMiddleware:

    def process_response(self, response):
        pdf_url = response.url
        pdf_response = requests.get(pdf_url, stream=True)
        pdf_path = f"storage/exports/{str(uuid.uuid4())}.pdf"
        with open(pdf_path, "wb") as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        with open(pdf_path, "rb") as f:
            loader = UnstructuredFileIOLoader(
                f,
                strategy="fast",
            )
            docs = loader.load()
            content = " ".join([doc.page_content for doc in docs])
            return content
