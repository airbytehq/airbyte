#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Tuple
import re
from datetime import datetime as dt

from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


class ParserError(Exception):
    """Replacement for pendulum's ParserError"""
    pass


@dataclass
class CustomFieldTransformation(RecordTransformation):
    """
    Remove all "empty" (e.g. '0000-00-00', '0000-00-00 00:00:00') 'date' and 'date-time' fields from record
    """

    config: Config
    parameters: InitVar[Optional[Mapping[str, Any]]] = None

    def __post_init__(self, parameters: Optional[Mapping[str, Any]] = None):
        # Handle the case when parameters is None
        parameters = parameters or {}
        self.name = parameters.get("name")
        
        # Skip schema loading if name is None
        if self.name is None:
            self._schema = {}
            self._date_and_date_time_fields = []
        else:
            self._schema = self._get_schema_root_properties()
            self._date_and_date_time_fields = self._get_fields_with_property_formats_from_schema(("date", "date-time"))

    def _get_schema_root_properties(self):
        # Only call this if self.name is not None
        if not self.name:
            return {}
            
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()
        return schema.get("properties", {})

    def _get_fields_with_property_formats_from_schema(self, property_formats: Tuple[str, ...]) -> List[str]:
        """
        Get all properties from schema within property_formats
        """
        return [k for k, v in self._schema.items() if v.get("format") in property_formats]

    def parse(self, text):
        """
        Direct replacement for pendulum.parse functionality.
        Handles various date formats including those with timezone information.
        """
        # Reject dates with zeros like '0000-00-00' or '0000-00-00 00:00:00'
        if re.match(r'^0+[-]0+[-]0+', text):
            raise ParserError("Zero date not allowed")
            
        # Comprehensive list of formats to try
        formats = [
            # Basic formats
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            
            # Date and time formats
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S.%f',
            
            # ISO formats
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            
            # With timezone
            '%Y-%m-%d %H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            
            # Using Z for UTC
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]
            
        # Try parsing with different formats
        for fmt in formats:
            try:
                # Handle 'Z' timezone indicator for UTC
                text_to_parse = text
                if fmt.endswith('Z') and not text.endswith('Z'):
                    continue
                if not fmt.endswith('Z') and text.endswith('Z'):
                    text_to_parse = text[:-1]  # Remove Z
                    fmt = fmt + 'Z' if 'Z' not in fmt else fmt
                    
                date_obj = dt.strptime(text_to_parse, fmt)
                # In pendulum, dates with zero components are rejected
                if date_obj.year == 0 or date_obj.month == 0 or date_obj.day == 0:
                    raise ParserError("Date with zero components")
                return date_obj
            except ValueError:
                continue
                
        # Try ISO format as a last resort
        try:
            # Replace Z with +00:00 for ISO format parsing
            iso_text = text.replace('Z', '+00:00')
            
            # For Python < 3.11 compatibility, remove microseconds if they have more than 6 digits
            microseconds_match = re.search(r'\.(\d{7,})(?=[+-Z]|$)', iso_text)
            if microseconds_match:
                fixed_micro = microseconds_match.group(1)[:6]
                iso_text = iso_text.replace(microseconds_match.group(0), f'.{fixed_micro}')
                
            date_obj = dt.fromisoformat(iso_text)
            if date_obj.year == 0 or date_obj.month == 0 or date_obj.day == 0:
                raise ParserError("Date with zero components")
            return date_obj
        except (ValueError, AttributeError):
            pass
            
        # If nothing worked, raise the error like pendulum would
        raise ParserError(f"Unable to parse: {text}")

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        # If we don't have any fields to check, just return the record as is
        if not self._date_and_date_time_fields:
            return record
            
        for item in record:
            if item in self._date_and_date_time_fields and record.get(item):
                try:
                    self.parse(record[item])
                except ParserError:
                    record[item] = None
        return record
    