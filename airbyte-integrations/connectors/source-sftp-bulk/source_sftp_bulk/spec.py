from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from pydantic import Field


class SourceSFTPBulkSpec(AbstractFileBasedSpec):
    class Config:
        title = "Google Drive Source Spec"

    folder_url: str = Field(
        description="URL for the folder you want to sync. Using individual streams and glob patterns, it's possible to only sync a subset of all files located in the folder.",
        examples=["https://drive.google.com/drive/folders/1Xaz0vXXXX2enKnNYU5qSt9NS70gvMyYn"],
        order=0,
        pattern="^https://drive.google.com/.+",
        pattern_descriptor="https://drive.google.com/drive/folders/MY-FOLDER-ID",
    )

    username: str = Field(title="User Name", description="The server user", order=0)

    password: str = Field(title="Password", description="Password", airbyte_secret=True, order=1)
    private_key: str = Field(title="Private key", description="The Private key", multiline=True, order=2)
    host: str = Field(title="Host Address", description="The server host address", examples=["www.host.com", "192.0.2.1"], order=3)
    port: int = Field(title="Host Address", description="The server port", default=22, examples=["22"], order=4)

    @classmethod
    def documentation_url(cls) -> str:
        return "https://docs.airbyte.com/integrations/sources/sftp-bulk"
