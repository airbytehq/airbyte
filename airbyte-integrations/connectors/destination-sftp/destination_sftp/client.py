#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import errno
import io
import json
import logging
import os
from typing import Any, BinaryIO, Dict, List, Optional, TextIO

import paramiko


class SftpClient:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        destination_path: str,
        port: int = 22,
        file_format: str = "json",
        file_name_pattern: str = "airbyte_{format}_{stream}",
        ssh_algorithms: Optional[Dict[str, Any]] = None,
    ):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.destination_path = destination_path
        self.file_format = file_format.lower()
        self.file_name_pattern = file_name_pattern
        self.ssh_algorithms = ssh_algorithms
        self._files = {}  # We'll store file paths rather than file handles
        self._headers: Dict[str, List[str]] = {}  # For CSV format
        self._transport = None
        self._sftp = None
        self.logger = logging.getLogger("airbyte")

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _connect(self):
        """Establish SFTP connection using direct paramiko transport"""
        try:
            self.logger.info(f"Connecting to SFTP server at {self.host}:{self.port}")
            self._transport = paramiko.Transport((self.host, self.port))
            self._transport.use_compression(True)

            # Handle SSH algorithms if specified
            if self.ssh_algorithms:
                if "server_host_key" in self.ssh_algorithms:
                    self._transport.get_security_options().key_types = tuple(self.ssh_algorithms["server_host_key"])

            self._transport.connect(username=self.username, password=self.password, hostkey=None)

            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self.logger.info("SFTP connection established successfully")

            # Verify destination path exists
            try:
                self._sftp.stat(self.destination_path)
                self.logger.info(f"Destination path verified: {self.destination_path}")
            except FileNotFoundError:
                self.logger.error(f"Destination path not found: {self.destination_path}")
                raise IOError(f"Destination path not found: {self.destination_path}")
            except Exception as e:
                self.logger.error(f"Error accessing destination path: {str(e)}")
                raise IOError(f"Error accessing destination path: {str(e)}")

        except paramiko.AuthenticationException as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise IOError(f"Authentication failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to connect to SFTP server: {str(e)}")
            raise IOError(f"Failed to connect to SFTP server: {str(e)}")

    def close(self):
        """Close SFTP connection"""
        if self._sftp:
            self._sftp.close()

        if self._transport:
            self._transport.close()

    def _get_file_extension(self) -> str:
        """Get appropriate file extension based on format"""
        if self.file_format == "csv":
            return "csv"
        else:  # Default to JSON
            return "jsonl"

    def _get_path(self, stream: str) -> str:
        """Generate file path based on pattern"""
        import datetime

        extension = self._get_file_extension()
        current_date = datetime.datetime.now().strftime("%Y%m%d")

        # Replace variables in pattern
        file_name = self.file_name_pattern.format(format=self.file_format, stream=stream, date=current_date)

        # Add extension if not present
        if not file_name.endswith(f".{extension}"):
            file_name = f"{file_name}.{extension}"

        # For restricted SFTP, avoid subdirectories by using basename only
        if "/" in file_name:
            file_name = os.path.basename(file_name)

        # Join with destination path
        return f"{self.destination_path}/{file_name}"

    def write(self, stream: str, record: Dict) -> None:
        """Write a record to the appropriate file"""
        if not self._sftp:
            self._connect()

        path = self._get_path(stream)
        self.logger.info(f"Writing to file: {path}")

        # For CSV format, we need to check if we need to write headers first
        if self.file_format == "csv":
            # Update headers with any new fields
            if stream not in self._headers:
                self._headers[stream] = list(record.keys())
            else:
                for key in record.keys():
                    if key not in self._headers[stream]:
                        self._headers[stream].append(key)

            # Check if the file exists
            try:
                self._sftp.stat(path)
                # File exists, append without headers
                file_exists = True
            except FileNotFoundError:
                # File doesn't exist, we'll need to write headers
                file_exists = False
            except Exception as e:
                self.logger.error(f"Error checking file existence: {str(e)}")
                raise IOError(f"Error checking file existence: {str(e)}")

            try:
                # Create a CSV row in memory
                values = []
                for header in self._headers[stream]:
                    value = record.get(header, "")
                    if isinstance(value, str):
                        if "," in value or '"' in value:
                            quoted_value = value.replace('"', '""')
                            value = f'"{quoted_value}"'
                    values.append(str(value))

                row = ",".join(values) + "\n"

                # If file doesn't exist or is empty, write headers first
                if not file_exists:
                    header_row = ",".join(self._headers[stream]) + "\n"
                    with self._sftp.open(path, "w") as f:  # Simple write mode
                        f.write(header_row)
                        f.write(row)
                else:
                    # Append to existing file
                    with self._sftp.open(path, "a") as f:  # Simple append mode
                        f.write(row)
            except Exception as e:
                self.logger.error(f"Error writing CSV data: {str(e)}")
                raise IOError(f"Error writing CSV data: {str(e)}")
        else:
            # JSON format is simpler
            try:
                json_line = json.dumps(record) + "\n"

                try:
                    # Check if file exists
                    self._sftp.stat(path)
                    # Append to existing file
                    with self._sftp.open(path, "a") as f:  # Simple append mode
                        f.write(json_line)
                except FileNotFoundError:
                    # Create new file
                    with self._sftp.open(path, "w") as f:  # Simple write mode
                        f.write(json_line)
                except Exception as e:
                    self.logger.error(f"Error accessing file: {str(e)}")
                    raise IOError(f"Error accessing file: {str(e)}")
            except Exception as e:
                self.logger.error(f"Error writing JSON data: {str(e)}")
                raise IOError(f"Error writing JSON data: {str(e)}")

    def read_data(self, stream: str) -> List[Dict]:
        """Read data from a file"""
        if not self._sftp:
            self._connect()

        path = self._get_path(stream)
        data = []

        try:
            try:
                # First check if file exists
                self._sftp.stat(path)
            except FileNotFoundError:
                self.logger.warning(f"File not found for stream {stream}: {path}")
                return []

            # Read file if it exists
            with self._sftp.open(path, "r") as file:
                content = file.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8")

                if self.file_format == "csv":
                    # Parse CSV
                    reader = csv.DictReader(content.splitlines())
                    for row in reader:
                        data.append(dict(row))
                else:
                    # Parse JSON
                    for line in content.splitlines():
                        if line.strip():
                            data.append(json.loads(line))
            return data
        except Exception as e:
            self.logger.error(f"Error reading data from {path}: {str(e)}")
            raise IOError(f"Error reading data from {path}: {str(e)}")

    def delete(self, stream: str) -> None:
        """Delete a file"""
        if not self._sftp:
            self._connect()

        path = self._get_path(stream)

        try:
            self._sftp.remove(path)
            self.logger.info(f"Deleted file: {path}")
        except FileNotFoundError:
            self.logger.warning(f"File not found when trying to delete: {path}")
        except IOError as err:
            # Ignore the case where the file doesn't exist
            if err.errno != errno.ENOENT:
                raise
        except Exception as e:
            self.logger.error(f"Error deleting file {path}: {str(e)}")
            raise IOError(f"Error deleting file {path}: {str(e)}")
