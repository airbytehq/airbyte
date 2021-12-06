from .base_service import *

class JournalEntry(RestBaseService):
    def __init__(self, config: Config, path: str = "/record/v1/journalEntry"):
        super().__init__(path=path, config=config)