#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath
import requests
import unidecode

from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.types import Config, StreamSlice


logger = logging.getLogger("airbyte")


def sheet_column_label(col_index: int) -> str:
    """
    Convert a 0-based column index to a Google Sheets-style column letter (A, B, ..., Z, AA, AB, ...).
    """
    label = ""
    col_index += 1  # Convert to 1-based index
    while col_index > 0:
        col_index -= 1
        label = chr(65 + (col_index % 26)) + label
        col_index //= 26
    return label


class RangePartitionRouter(SinglePartitionRouter):
    """
    Create ranges to request rows data to google sheets api.
    """

    parameters: Mapping[str, Any]

    def __init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__(parameters)
        self.parameters = parameters
        self.sheet_row_count = parameters.get("row_count", 0)
        self.sheet_id = parameters.get("sheet_id")
        self.batch_size = parameters.get("batch_size", 1000000)

    def stream_slices(self) -> Iterable[StreamSlice]:
        start_range = 2  # skip 1 row, as expected column (fields) names there

        while start_range <= self.sheet_row_count:
            end_range = start_range + self.batch_size
            logger.info(f"Fetching range {self.sheet_id}!{start_range}:{end_range}")
            yield StreamSlice(partition={"start_range": start_range, "end_range": end_range}, cursor_slice={})
            start_range = end_range + 1


class RawSchemaParser:
    config: Config

    def _extract_data(
        self,
        body: Mapping[str, Any],
        extraction_path: Optional[List[Union[InterpolatedString, str]]] = None,
        default: Any = None,
    ) -> Any:
        """
        Extracts data from the body based on the provided extraction path.
        """

        if not extraction_path:
            return body

        path = [node.eval(self.config) if not isinstance(node, str) else node for node in extraction_path]

        return dpath.get(body, path, default=default)  # type: ignore # extracted

    def _set_data(
        self, value: Any, body: MutableMapping[str, Any], extraction_path: Optional[List[Union[InterpolatedString, str]]] = None
    ) -> Any:
        """
        Sets data in the body based on the provided extraction path.
        """
        if not extraction_path:
            body = value

        path = [node.eval(self.config) if not isinstance(node, str) else node for node in extraction_path]

        dpath.set(body, path, value=value)

    def parse_raw_schema_values(
        self,
        raw_schema_data: MutableMapping[Any, Any],
        schema_pointer: List[Union[InterpolatedString, str]],
        key_pointer: List[Union[InterpolatedString, str]],
        names_conversion: bool,
    ):
        """
        1. Parses sheet headers from the provided raw schema. This method assumes that data is contiguous
            i.e: every cell contains a value and the first cell which does not contain a value denotes the end
            of the headers.
        2. Makes name conversion if required.
        3. Deduplicates fields from the schema by appending cell positions to duplicate headers.
        Return a list of tuples with correct property index (by found in array), value and raw_schema
        """
        raw_schema_properties = self._extract_data(raw_schema_data, schema_pointer, default=[])
        parsed_schema_values = []
        # Gather all sanitisation flags from config
        config = getattr(self, "config", {})
        flags = {
            "remove_leading_trailing_underscores": config.get("remove_leading_trailing_underscores", False),
            "combine_number_word_pairs": config.get("combine_number_word_pairs", False),
            "remove_special_characters": config.get("remove_special_characters", False),
            "combine_letter_number_pairs": config.get("combine_letter_number_pairs", False),
            "allow_leading_numbers": config.get("allow_leading_numbers", False),
        }
        use_sanitzation = any(flags.values())

        for property_index, raw_schema_property in enumerate(raw_schema_properties):
            raw_schema_property_value = self._extract_data(raw_schema_property, key_pointer)
            if not raw_schema_property_value or raw_schema_property_value.isspace():
                break
            # Use sanitzation if any flag is set, else legacy
            if names_conversion and use_sanitzation:
                raw_schema_property_value = safe_sanitzation_conversion(raw_schema_property_value, **flags)
            elif names_conversion:
                raw_schema_property_value = safe_name_conversion(raw_schema_property_value)

            parsed_schema_values.append((property_index, raw_schema_property_value, raw_schema_property))

        # Deduplicate by appending cell position if duplicates exist
        header_counts = Counter(p[1] for p in parsed_schema_values)
        duplicates = {k for k, v in header_counts.items() if v > 1}
        for i in range(len(parsed_schema_values)):
            property_index, value, prop = parsed_schema_values[i]
            if value in duplicates:
                col_letter = sheet_column_label(property_index)
                new_value = f"{value}_{col_letter}1"
                parsed_schema_values[i] = (property_index, new_value, prop)

        return parsed_schema_values

    def parse(self, schema_type_identifier, records: Iterable[MutableMapping[Any, Any]]):
        """Removes duplicated fields and makes names conversion"""
        names_conversion = self.config.get("names_conversion", False)
        schema_pointer = schema_type_identifier.get("schema_pointer")
        key_pointer = schema_type_identifier["key_pointer"]
        parsed_properties = []
        for raw_schema_data in records:
            for _, parsed_value, raw_schema_property in self.parse_raw_schema_values(
                raw_schema_data, schema_pointer, key_pointer, names_conversion
            ):
                self._set_data(parsed_value, raw_schema_property, key_pointer)
                parsed_properties.append(raw_schema_property)
            self._set_data(parsed_properties, raw_schema_data, schema_pointer)
            yield raw_schema_data


@dataclass
class DpathSchemaMatchingExtractor(DpathExtractor, RawSchemaParser):
    """
    Current DpathExtractor has problems for this type of data in response:
    [
      {
        "values": [
          [
            "name1",
            "22"
          ],
          [
            "name2",
            "24"
          ],
          [
            "name3",
            "25"
          ]
        ]
      }
    ]

    This is because "values" field is a list of lists instead of objects that we could extract with "*".
    In order to do so we need the ordered properties from the schema that we can match with each list of values.
    Then, if we get a properties object like {0: 'name', 1: 'age'} we end up with:

    {"type":"RECORD","record":{"stream":"a_stream_name","data":{"name":"name1","age":"22"},"emitted_at":1734371904128}}
    {"type":"RECORD","record":{"stream":"a_stream_name","data":{"name":"name2","age":"24"},"emitted_at":1734371904134}}
    {"type":"RECORD","record":{"stream":"a_stream_name","data":{"name":"name3","age":"25"},"emitted_at":1734371904134}}
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.decoder = JsonDecoder(parameters={})
        self._values_to_match_key = parameters["values_to_match_key"]
        schema_type_identifier = parameters["schema_type_identifier"]
        names_conversion = self.config.get("names_conversion", False)
        properties_to_match = parameters.get("properties_to_match", {})
        self._indexed_properties_to_match = self.extract_properties_to_match(
            properties_to_match, schema_type_identifier, names_conversion=names_conversion
        )

    def extract_properties_to_match(self, properties_to_match, schema_type_identifier, names_conversion):
        schema_pointer = schema_type_identifier.get("schema_pointer")
        key_pointer = schema_type_identifier["key_pointer"]
        indexed_properties = {}
        for property_index, property_parsed_value, _ in self.parse_raw_schema_values(
            properties_to_match, schema_pointer, key_pointer, names_conversion
        ):
            indexed_properties[property_index] = property_parsed_value
        return indexed_properties

    @staticmethod
    def match_properties_with_values(unmatched_values: List[str], indexed_properties: Dict[int, str]):
        data = {}
        for relevant_index in sorted(indexed_properties.keys()):
            if relevant_index >= len(unmatched_values):
                break

            unmatch_value = unmatched_values[relevant_index]
            if unmatch_value.strip() != "":
                data[indexed_properties[relevant_index]] = unmatch_value
        yield data

    @staticmethod
    def is_row_empty(cell_values: List[str]) -> bool:
        for cell in cell_values:
            if cell.strip() != "":
                return False
        return True

    @staticmethod
    def row_contains_relevant_data(cell_values: List[str], relevant_indices: Iterable[int]) -> bool:
        for idx in relevant_indices:
            if len(cell_values) > idx and cell_values[idx].strip() != "":
                return True
        return False

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        raw_records_extracted = super().extract_records(response=response)
        for raw_record in raw_records_extracted:
            unmatched_values_collection = raw_record.get(self._values_to_match_key, [])
            for unmatched_values in unmatched_values_collection:
                if not DpathSchemaMatchingExtractor.is_row_empty(
                    unmatched_values
                ) and DpathSchemaMatchingExtractor.row_contains_relevant_data(unmatched_values, self._indexed_properties_to_match.keys()):
                    yield from DpathSchemaMatchingExtractor.match_properties_with_values(
                        unmatched_values, self._indexed_properties_to_match
                    )


@dataclass
class DpathSchemaExtractor(DpathExtractor, RawSchemaParser):
    """
    Makes names conversion and parses sheet headers from the provided row.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.schema_type_identifier = parameters["schema_type_identifier"]

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        extracted_records = super().extract_records(response=response)
        yield from self.parse(schema_type_identifier=self.schema_type_identifier, records=extracted_records)


TOKEN_PATTERN = re.compile(r"[A-Z]+[a-z]*|[a-z]+|\d+|(?P<NoToken>[^a-zA-Z\d]+)")
DEFAULT_SEPARATOR = "_"


def name_conversion(text: str) -> str:
    """
    convert name using a set of rules, for example: '1MyName' -> '_1_my_name'
    """
    text = unidecode.unidecode(text)

    tokens = []
    for m in TOKEN_PATTERN.finditer(text):
        if m.group("NoToken") is None:
            tokens.append(m.group(0))
        else:
            tokens.append("")

    if len(tokens) >= 3:
        tokens = tokens[:1] + [t for t in tokens[1:-1] if t] + tokens[-1:]

    if tokens and tokens[0].isdigit():
        tokens.insert(0, "")

    text = DEFAULT_SEPARATOR.join(tokens)
    text = text.lower()
    return text


def safe_name_conversion(text: str) -> str:
    if not text:
        return text
    new = name_conversion(text)
    if not new:
        raise Exception(f"initial string '{text}' converted to empty")
    return new


def _sanitization(
    text: str,
    remove_leading_trailing_underscores: bool = False,
    combine_number_word_pairs: bool = False,
    remove_special_characters: bool = False,
    combine_letter_number_pairs: bool = False,
    allow_leading_numbers: bool = False,
) -> str:
    """
    Converts a string into a normalized, SQL-compliant name using a set of configurable options.

    Args:
        text: The input string to convert.
        remove_leading_trailing_underscores: If True, removes underscores at the start/end of the result.
        combine_number_word_pairs: If True, combines adjacent number and word tokens (e.g., "50 th" -> "50th").
        remove_special_characters: If True, removes all special characters from the input.
        combine_letter_number_pairs: If True, combines adjacent letter and number tokens (e.g., "Q 3" -> "Q3").
        allow_leading_numbers: If False, prepends an underscore if the result starts with a number.

    Returns:
        The normalized, SQL-compliant string.

    Steps:
    1. Transliterates the input text to ASCII using unidecode.
    2. Optionally removes special characters if remove_special_characters is True.
    3. Splits the text into tokens using a regex pattern that separates words, numbers, and non-alphanumeric characters.
    4. Optionally combines adjacent letter+number or number+word tokens based on flags.
    5. Removes empty tokens in the middle, but keeps leading/trailing empty tokens for underscore placement.
    6. Optionally strips leading/trailing underscores if remove_leading_trailing_underscores is True.
    7. Optionally prepends an underscore if the result starts with a number and allow_leading_numbers is False.
    8. Returns the final string in lowercase.
    """
    text = unidecode.unidecode(text)

    if remove_special_characters:
        text = re.sub(r"[^\w\s]", "", text)

    tokens = []
    for m in TOKEN_PATTERN.finditer(text):
        if m.group("NoToken") is None:
            tokens.append(m.group(0))
        else:
            tokens.append("")

    # Combine tokens as per flags
    combined_tokens = []
    i = 0
    while i < len(tokens):
        if (
            combine_letter_number_pairs
            and i + 1 < len(tokens)
            and tokens[i]
            and tokens[i].isalpha()
            and tokens[i + 1]
            and tokens[i + 1].isdigit()
        ):
            combined = tokens[i] + tokens[i + 1]
            combined_tokens.append(combined)
            i += 2
        elif (
            combine_number_word_pairs
            and i + 1 < len(tokens)
            and tokens[i]
            and tokens[i].isdigit()
            and tokens[i + 1]
            and tokens[i + 1].isalpha()
        ):
            combined = tokens[i] + tokens[i + 1]
            combined_tokens.append(combined)
            i += 2
        else:
            combined_tokens.append(tokens[i])
            i += 1

    # Find indices of first and last non-empty tokens
    first_non_empty = next((i for i, t in enumerate(combined_tokens) if t), len(combined_tokens))
    last_non_empty = next((i for i, t in reversed(list(enumerate(combined_tokens))) if t), -1)

    # Process tokens: keep leading/trailing empty tokens, remove empty tokens in middle
    if first_non_empty < len(combined_tokens):
        leading = combined_tokens[:first_non_empty]
        middle = [t for t in combined_tokens[first_non_empty : last_non_empty + 1] if t]
        trailing = combined_tokens[last_non_empty + 1 :]
        processed_tokens = leading + middle + trailing
    else:
        processed_tokens = combined_tokens  # All tokens are empty

    # Join tokens with underscores
    result = DEFAULT_SEPARATOR.join(processed_tokens)

    # Apply remove_leading_trailing_underscores on the final string
    if remove_leading_trailing_underscores:
        result = result.strip(DEFAULT_SEPARATOR)

    # Handle leading numbers after underscore removal
    if not allow_leading_numbers and result and result[0].isdigit():
        result = DEFAULT_SEPARATOR + result

    final_result = result.lower()
    return final_result


def safe_sanitzation_conversion(text: str, **kwargs) -> str:
    """
    Converts text to a safe name using _sanitization with the provided keyword arguments.
    Raises an exception if the result is empty or "_". Unlike safe_name_conversion,
    this function also rejects "_" as a valid result, since _sanitization
    may return "_" for certain inputs (e.g., "*").
    """
    new = _sanitization(text, **kwargs)
    if not new or new == "_":
        raise Exception(f"initial string '{text}' converted to empty")
    return new


def exception_description_by_status_code(code: int, spreadsheet_id) -> str:
    if code in [
        requests.status_codes.codes.INTERNAL_SERVER_ERROR,
        requests.status_codes.codes.BAD_GATEWAY,
        requests.status_codes.codes.SERVICE_UNAVAILABLE,
    ]:
        return (
            "There was an issue with the Google Sheets API. "
            "This is usually a temporary issue from Google's side. "
            "Please try again. If this issue persists, contact support."
        )
    if code == requests.status_codes.codes.FORBIDDEN:
        return (
            f"The authenticated Google Sheets user does not have permissions to view the spreadsheet with id {spreadsheet_id}. "
            "Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. "
            "If the issue persists, contact support."
        )
    if code == requests.status_codes.codes.NOT_FOUND:
        return (
            f"The requested Google Sheets spreadsheet with id {spreadsheet_id} does not exist. "
            f"Please ensure the Spreadsheet Link you have set is valid and the spreadsheet exists. If the issue persists, contact support."
        )

    if code == requests.status_codes.codes.TOO_MANY_REQUESTS:
        return "Rate limit has been reached. Please try later or request a higher quota for your account."

    return ""
