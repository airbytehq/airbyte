from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class JsonFormat(BaseModel):
    'This connector utilises <a href="https://pandas.pydata.org/docs/reference/api/pandas.io.json.read_json.html" target="_blank">Pandas</a> for JSON parsing.'

    class Config:
        title = "json"

    filetype: str = Field(Config.title, const=True)

    orient: str = Field(
        default='columns',
        description="Indication of expected JSON string format. Compatible JSON strings can be produced by to_json() with a corresponding orient value. Allowed values are {'split','records','index', 'columns','values', 'table'}",
    )

    convert_dates: Union[bool, List[str]] = Field(
        default=True,
        description="A list of columns to parse for dates; If True, then try to parse date-like columns, default is True."
    )

    keep_default_dates: bool = Field(
        default=True,
        description="""If parsing dates (convert_dates is not False), then try to parse the default datelike columns. A column label is datelike if one of these conditions is verified:
            * it ends with '_at',
            * it ends with '_time',
            * it begins with 'timestamp',
            * it is 'modified', 
            * it is 'date'
        """
    )

    lines: bool = Field(
        default=True,
        description="Read the file as a json object per line."
    )

    chunk_size: int = Field(
        default=100,
        description="If lines is True, returns a JsonReader iterator to read batches of `chunk_size` lines instead of the whole file at once."
    )

    compression: str = Field(
        default='infer',
        description="For on-the-fly decompression of on-disk data. If ‘infer’, then use gzip, bz2, zip or xz if path_or_buf is a string ending in ‘.gz’, ‘.bz2’, ‘.zip’, or ‘xz’, respectively, and no decompression otherwise. If using ‘zip’, the ZIP file must contain only one data file to be read in. Set to None for no decompression."
    )

    encoding: str = Field(
        default='utf8',
        description="The encoding to use to decode py3 bytes."
    )

    nrows: Optional[int] = Field(
        default=None,
        description="The number of lines from the line-delimited jsonfile that has to be read. This can only be passed if lines=True. If this is None, all the rows will be returned."
    )