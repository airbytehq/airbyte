from urllib.parse import urlparse

import scrapy
from scrapy.http import Response, HtmlResponse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from ..middleware.pdf import PdfDownloadMiddleware

STATUS_SEND_WAIT_TIME_IN_SECONDS = 5

ALLOWED_FILE_TYPE_MAP = {
    "html": "text/html",
    "pdf": "application/pdf",
}

NOT_ALLOWED_EXT = (
    "zip",
    "txt",
    "csv",
    "docx",
    "doc",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "exe",
    "jpg",
    "jpeg",
    "png",
    "gif",
    "wav",
    "mp3",
    "ogg",
)

# empty string means relative links
ALLOWED_SCHEMES = ("", "http", "https")


class WebBaseSpider(scrapy.Spider):
    name = "web_base_spider"

    custom_settings = {
        "USER_AGENT": UserAgent(
            platforms=["pc"],
            browsers=["safari", "chrome"],
        ).random,
        "FEEDS": {
            "storage/exports/%(data_resource_id)s.csv": {
                "format": "csv",
                "fields": ["content", "source"],
            },
            "storage/exports/raw_%(data_resource_id)s.csv": {
                "format": "csv",
            },
        },
    }

    def __init__(
        self,
        url: str,
        data_resource_id: str,
        allowed_extensions: list,
        *args,
        **kwargs,
    ):
        super(WebBaseSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.data_resource_id = data_resource_id
        self.allowed_extensions = allowed_extensions
        self.allowed_domains = [urlparse(url).netloc]
        self.custom_settings = {
            **(self.custom_settings or {}),
        }

    def get_clean_content(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        clean_content = " \n ".join(" ".join(x.split()) for x in soup.get_text(separator=" ", strip=True).splitlines() if x.strip())
        return clean_content

    def get_pdf_content(self, response):
        pdf_download_middleware = PdfDownloadMiddleware()
        return pdf_download_middleware.process_response(response)

    def is_valid_link(self, link):
        url_parsed = urlparse(link)

        if url_parsed.scheme not in ALLOWED_SCHEMES:
            return False

        ext = url_parsed.path.split(".")[-1]
        if ext.lower() in NOT_ALLOWED_EXT:
            return False

        return True

    def is_html_document(self, response: Response) -> bool:
        content_type = response.headers.get("Content-Type") or b""
        return content_type.decode("utf-8").startswith("text/html")

    def is_pdf_document(self, response: Response) -> bool:
        content_type = response.headers.get("Content-Type") or b""
        return content_type.decode("utf-8").startswith("application/pdf")

    def is_allowed_type(self, response: Response) -> bool:
        content_type = response.headers.get("Content-Type") or b""
        content_type = content_type.decode("utf-8")
        return any(content_type.startswith(ALLOWED_FILE_TYPE_MAP[ext]) for ext in self.allowed_extensions)

    def parse(self, response, **_):

        if self.is_html_document(response) and self.is_allowed_type(response):
            yield {
                "raw": response.text,
                "content": self.get_clean_content(response),
                "source": response.url,
            }

        if self.is_pdf_document(response) and self.is_allowed_type(response):
            yield {
                "raw": response.body,
                "content": self.get_pdf_content(response),
                "source": response.url,
            }

        if isinstance(response, HtmlResponse):
            for link in response.css("a::attr(href)").getall():
                if self.is_valid_link(link):
                    yield response.follow(link, self.parse)
