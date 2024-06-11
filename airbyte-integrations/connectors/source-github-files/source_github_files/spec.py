from airbyte_cdk.sources.file_based.file_based_source import AbstractFileBasedSpec
from pydantic import BaseModel, Field


class SourceGithubFilesSpec(AbstractFileBasedSpec, BaseModel):
    class Config:
        title = "Google Drive Source Spec"

    folder_url: str = Field(
        description="URL for the folder you want to sync. Using individual streams and glob patterns, it's possible to only sync a subset of all files located in the folder.",
        examples=["https://drive.google.com/drive/folders/1Xaz0vXXXX2enKnNYU5qSt9NS70gvMyYn"],
        order=0,
        pattern="^https://drive.google.com/.+",
        pattern_descriptor="https://drive.google.com/drive/folders/MY-FOLDER-ID",
    )
