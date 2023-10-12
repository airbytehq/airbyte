import io
import struct
import zipfile


class ZipFileHandler:
    """
    Handler class for extracting information from ZIP files stored in AWS S3.
    """

    # Class constants for signatures
    EOCD_SIGNATURE = b"\x50\x4b\x05\x06"
    ZIP64_LOCATOR_SIGNATURE = b"\x50\x4b\x06\x07"

    def __init__(self, s3_client, config):
        """
        Initialize the ZipFileHandler with an S3 client and configuration.
        """
        self.s3_client = s3_client
        self.config = config

    def _fetch_data_from_s3(self, filename, start, size=None):
        """
        Fetch a range of bytes from a file in S3.

        Parameters:
        - filename: The name of the file in S3.
        - start: The starting byte position.
        - size: The number of bytes to fetch (optional).

        Returns:
        - The fetched bytes.
        """
        end_range = f"{start + size - 1}" if size else ""
        range_str = f"bytes={start}-{end_range}"
        response = self.s3_client.get_object(Bucket=self.config.bucket, Key=filename, Range=range_str)
        return response["Body"].read()

    def _find_signature(self, filename, signature, initial_buffer_size=1024, max_buffer_size=16 * 1024 * 1024):
        """
        Find a given signature in the file by checking chunks of increasing size.
        If the signature is not found within the max_buffer_size, None is returned.

        Returns:
        - The chunk of data containing the signature or None if not found.
        """
        buffer_size = initial_buffer_size
        file_size = self.s3_client.head_object(Bucket=self.config.bucket, Key=filename)["ContentLength"]

        while buffer_size <= max_buffer_size:
            chunk = self._fetch_data_from_s3(filename, file_size - buffer_size)
            index = chunk.rfind(signature)
            if index != -1:
                return chunk[index:]
            buffer_size *= 2
        return None

    def _fetch_zip64_data(self, filename):
        """
        Fetch the ZIP64 End of Central Directory (EOCD) data from a ZIP file.
        """
        chunk = self._find_signature(filename, self.ZIP64_LOCATOR_SIGNATURE)
        zip64_eocd_offset = struct.unpack_from("<Q", chunk, 8)[0]
        return self._fetch_data_from_s3(filename, zip64_eocd_offset, 56)

    def _get_central_directory_start(self, filename):
        """
        Extract the central directory start position. Adjust for ZIP64 format if necessary.
        """
        eocd_data = self._find_signature(filename, self.EOCD_SIGNATURE)
        central_dir_start = struct.unpack_from("<L", eocd_data, 16)[0]

        # Check for ZIP64 format and adjust offsets if necessary
        if central_dir_start == 0xFFFFFFFF:
            zip64_data = self._fetch_zip64_data(filename)
            central_dir_start = struct.unpack_from("<Q", zip64_data, 48)[0]

        return central_dir_start

    def get_zip_files(self, filename):
        """
        Extract file information from a ZIP file stored in S3.

        Returns:
        - A list of ZipInfo objects for the files in the ZIP.
        """
        central_dir_start = self._get_central_directory_start(filename)
        central_dir_data = self._fetch_data_from_s3(filename, central_dir_start)

        with io.BytesIO(central_dir_data) as bytes_io:
            with zipfile.ZipFile(bytes_io, "r") as zf:
                return zf.infolist(), central_dir_start


class DecompressedStream(io.IOBase):
    """
    A custom stream class that handles decompression of data from a given file object.
    This class supports seeking, reading, and other basic file operations on compressed data.
    """

    def __init__(self, file_obj, file_start, file_len, compression_method):
        self._file = file_obj
        self.file_start = self._calculate_actual_start(file_start)
        self.file_len = file_len
        self.compression_method = compression_method
        self.seek(0)

    def _calculate_actual_start(self, file_start):
        """
        Calculate the actual start of the file content, skipping the ZIP headers.
        """
        self._file.seek(file_start + 26)
        file_head = self._file.read(4)
        name_len, extra_len = struct.unpack("<HH", file_head)

        return file_start + 30 + name_len + extra_len

    def _reset_decompressor(self):
        """
        Reset the decompressor object.
        """
        self.decompressor = zipfile._get_decompressor(self.compression_method)

    def _decompress_chunk(self, chunk):
        """
        Decompress a chunk of data based on the compression method.
        """
        if self.compression_method == zipfile.ZIP_STORED:
            return chunk
        return self.decompressor.decompress(chunk)

    def read(self, size=-1):
        if size == -1:
            size = self.file_len - self.position

        chunk = self._file.read(size)
        data = self._decompress_chunk(chunk)

        self.position += len(data)
        return data

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = offset
        elif whence == io.SEEK_CUR:
            self.position += offset
        elif whence == io.SEEK_END:
            self.position = self.file_len + offset
        else:
            raise ValueError("Invalid value for whence.")

        self._file.seek(self.file_start + self.position)
        self._reset_decompressor()
        return self.position

    def tell(self):
        return self.position

    def readable(self):
        return True

    def seekable(self):
        return True

    def close(self):
        self._file.close()


class ZipContentReader:
    """
    A custom reader class that provides buffered reading capabilities on a decompressed stream.
    This class supports reading lines, reading chunks, and iterating over the content.
    """

    def __init__(self, decompressed_stream, encoding=None, buffer_size=1024 * 1024):
        self.raw = decompressed_stream
        self.encoding = encoding
        self.buffer_size = buffer_size
        self.buffer = bytearray()
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def readline(self, limit=-1):
        """
        Read a single line from the file.
        """
        if limit != -1:
            raise NotImplementedError("limits other than -1 not implemented yet")

        line = ""
        while True:
            char = self.read(1)
            if not char:
                break

            line += char
            if char in ["\n", "\r"]:
                # Peek the next character without consuming it
                next_char = self.read(1)
                if char == "\r" and next_char == "\n":
                    line += next_char
                else:
                    self.buffer = next_char.encode(self.encoding) + self.buffer
                break
        return line

    def read(self, size=-1):
        """
        Read data from the file up to the specified size.
        """
        if size < 0:
            size = len(self.buffer)

        while len(self.buffer) < size:
            chunk = self.raw.read(self.buffer_size)
            if not chunk:
                break
            self.buffer += chunk

        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        self.position += len(data)

        return data.decode(self.encoding) if self.encoding else bytes(data)

    def seek(self, offset, whence=io.SEEK_SET):
        self.buffer = bytearray()
        self.position = self.raw.seek(offset, whence)
        return self.position

    def close(self):
        self.raw.close()
