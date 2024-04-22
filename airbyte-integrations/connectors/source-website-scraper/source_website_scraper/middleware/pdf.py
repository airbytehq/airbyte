import fitz


class PdfDownloadMiddleware:

    def process_response(self, response):
        pdf_document = fitz.open(stream=response.body, filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        return text
