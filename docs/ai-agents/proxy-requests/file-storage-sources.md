# File Storage Source Proxy Requests

File storage source proxy requests enable your AI agents to retrieve files and objects from cloud storage platforms on-demand. This is ideal for accessing documents, images, data files, and other binary content dynamically.

## Overview

File storage proxy requests allow you to:
- **Access files on-demand** from S3, GCS, Azure Blob Storage
- **Retrieve specific objects** by key or path
- **Stream large files** without downloading full datasets
- **Query file metadata** (size, modified date, content type)

## Supported File Storage Sources

### Amazon S3
**Use Case:** Access documents, images, data files, and logs stored in S3 buckets

**Authentication:** IAM credentials or Access Keys

**Available Operations:**
- `list_objects` - List objects in a bucket
- `get_object` - Retrieve file content
- `get_object_metadata` - Get file metadata without downloading content
- `head_object` - Check if object exists

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "Company Documents S3",
  "sourceDefinitionId": "69589781-7828-43c5-9f63-8925b1c1ccc2",
  "configuration": {
    "bucket": "my-company-documents",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1",
    "path_prefix": "documents/"
  }
}
```

**Proxy Request Examples:**

#### List Objects in Bucket
```bash
curl -X POST https://api.airbyte.com/v1/proxy/sources/{sourceId}/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list_objects",
    "parameters": {
      "prefix": "documents/invoices/",
      "max_keys": 100
    }
  }'
```

#### Get Specific File
```bash
curl -X POST https://api.airbyte.com/v1/proxy/sources/{sourceId}/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_object",
    "parameters": {
      "key": "documents/invoices/2024/invoice_12345.pdf"
    }
  }'
```

**Response:**
```json
{
  "key": "documents/invoices/2024/invoice_12345.pdf",
  "content": "base64_encoded_file_content",
  "content_type": "application/pdf",
  "size": 245678,
  "last_modified": "2024-01-15T10:30:00Z",
  "metadata": {
    "invoice_id": "12345",
    "customer_id": "cust_789"
  }
}
```

---

### Google Cloud Storage (GCS)
**Use Case:** Access files stored in Google Cloud Storage buckets

**Authentication:** Service Account or OAuth 2.0

**Available Operations:**
- `list_objects` - List objects in a bucket
- `get_object` - Retrieve file content
- `get_object_metadata` - Get file metadata

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "GCS Data Lake",
  "sourceDefinitionId": "c4cfaaf5-2e11-4d28-89e3-14ed7d1f8c5f",
  "configuration": {
    "bucket": "my-data-lake",
    "service_account_json": "{\"type\":\"service_account\",\"project_id\":\"...\"}",
    "path_prefix": "raw-data/"
  }
}
```

**Proxy Request Example:**
```python
def list_gcs_files(source_id, prefix, max_results=100):
    """List files in GCS bucket."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "list_objects",
            "parameters": {
                "prefix": prefix,
                "max_keys": max_results
            }
        }
    )
    return response.json()
```

---

### Azure Blob Storage
**Use Case:** Access files in Azure storage accounts

**Authentication:** Connection String or SAS Token

**Available Operations:**
- `list_blobs` - List blobs in a container
- `get_blob` - Retrieve blob content
- `get_blob_properties` - Get blob metadata

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "Azure Documents",
  "sourceDefinitionId": "b32a7b6f-5e8d-4c3e-9f2a-1b8c9d4e3f2a",
  "configuration": {
    "storage_account": "mycompanystorage",
    "container": "documents",
    "sas_token": "sv=2020-08-04&ss=b&srt=sco&sp=rl...",
    "path_prefix": "uploads/"
  }
}
```

**Proxy Request Example:**
```javascript
async function getAzureBlob(sourceId, blobPath) {
  const response = await fetch(
    `https://api.airbyte.com/v1/proxy/sources/${sourceId}/query`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        operation: 'get_blob',
        parameters: {
          blob_name: blobPath
        }
      })
    }
  );
  return await response.json();
}
```

---

## Common Use Cases

### Use Case 1: Document Retrieval for AI Agents

Retrieve customer documents for AI processing:

```python
def get_customer_invoice(source_id, customer_id, invoice_id):
    """Retrieve customer invoice PDF from S3."""
    file_key = f"invoices/{customer_id}/{invoice_id}.pdf"

    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "get_object",
            "parameters": {"key": file_key}
        }
    )

    if response.status_code == 200:
        data = response.json()
        # Decode base64 content
        import base64
        pdf_content = base64.b64decode(data["content"])
        return pdf_content
    else:
        raise Exception(f"Failed to retrieve invoice: {response.text}")
```

### Use Case 2: Image Processing

Access images for AI vision models:

```python
import base64
from PIL import Image
from io import BytesIO

def get_product_image(source_id, product_id):
    """Get product image from S3 for AI analysis."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "get_object",
            "parameters": {
                "key": f"products/{product_id}/main.jpg"
            }
        }
    )

    data = response.json()
    image_bytes = base64.b64decode(data["content"])

    # Open image with PIL
    image = Image.open(BytesIO(image_bytes))
    return image
```

### Use Case 3: Data File Access

Retrieve CSV or JSON data files:

```python
import csv
import base64
from io import StringIO

def get_customer_data_csv(source_id, date):
    """Get daily customer data export CSV."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "get_object",
            "parameters": {
                "key": f"exports/customers_{date}.csv"
            }
        }
    )

    data = response.json()
    csv_content = base64.b64decode(data["content"]).decode('utf-8')

    # Parse CSV
    reader = csv.DictReader(StringIO(csv_content))
    return list(reader)
```

### Use Case 4: Log File Analysis

Access log files for AI-powered analysis:

```python
import gzip
import base64

def get_application_logs(source_id, date, hour):
    """Retrieve and decompress application logs."""
    log_key = f"logs/{date}/app-{hour}.log.gz"

    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "get_object",
            "parameters": {"key": log_key}
        }
    )

    data = response.json()
    compressed_content = base64.b64decode(data["content"])

    # Decompress gzip
    decompressed = gzip.decompress(compressed_content).decode('utf-8')
    return decompressed.split('\n')
```

---

## Listing and Filtering Files

### List Files with Prefix

```python
def list_files_by_prefix(source_id, prefix, max_keys=1000):
    """List all files matching a prefix."""
    all_files = []
    continuation_token = None

    while True:
        params = {
            "prefix": prefix,
            "max_keys": min(max_keys - len(all_files), 100)
        }

        if continuation_token:
            params["continuation_token"] = continuation_token

        response = requests.post(
            f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={
                "operation": "list_objects",
                "parameters": params
            }
        ).json()

        all_files.extend(response["objects"])

        continuation_token = response.get("next_continuation_token")
        if not continuation_token or len(all_files) >= max_keys:
            break

    return all_files
```

### Filter Files by Extension

```python
def list_files_by_extension(source_id, prefix, extension):
    """List files with specific extension."""
    all_files = list_files_by_prefix(source_id, prefix)

    return [
        f for f in all_files
        if f["key"].endswith(f".{extension}")
    ]

# Example: Get all PDFs in invoices folder
pdf_files = list_files_by_extension("src_123", "invoices/", "pdf")
```

### Filter Files by Date

```python
from datetime import datetime, timedelta

def list_recent_files(source_id, prefix, days=7):
    """List files modified in the last N days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    all_files = list_files_by_prefix(source_id, prefix)

    return [
        f for f in all_files
        if datetime.fromisoformat(f["last_modified"].replace("Z", "+00:00")) > cutoff_date
    ]
```

---

## File Metadata Operations

### Get File Metadata Without Downloading

Retrieve file information without downloading content:

```python
def get_file_info(source_id, file_key):
    """Get file metadata without downloading."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "get_object_metadata",
            "parameters": {"key": file_key}
        }
    )

    return response.json()

# Example response
{
    "key": "documents/report.pdf",
    "size": 1048576,
    "last_modified": "2024-01-15T10:30:00Z",
    "content_type": "application/pdf",
    "etag": "\"abc123def456\"",
    "metadata": {
        "author": "John Doe",
        "department": "Finance"
    }
}
```

### Check if File Exists

```python
def file_exists(source_id, file_key):
    """Check if a file exists in storage."""
    try:
        response = requests.post(
            f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={
                "operation": "head_object",
                "parameters": {"key": file_key}
            }
        )
        return response.status_code == 200
    except:
        return False
```

---

## Binary Content Handling

### Working with Base64 Encoded Content

All binary content is returned as base64-encoded strings:

```python
import base64

def decode_file_content(response_data):
    """Decode base64 file content."""
    encoded_content = response_data["content"]
    decoded_bytes = base64.b64decode(encoded_content)
    return decoded_bytes

# For text files
text_content = decoded_bytes.decode('utf-8')

# For binary files
with open('output.pdf', 'wb') as f:
    f.write(decoded_bytes)
```

### Handling Large Files

For large files, consider streaming:

```python
def stream_large_file(source_id, file_key, chunk_size_mb=10):
    """Stream large file in chunks."""
    # First, get file size
    metadata = get_file_info(source_id, file_key)
    file_size = metadata["size"]

    # Calculate byte ranges
    chunk_size = chunk_size_mb * 1024 * 1024
    chunks = []

    for start in range(0, file_size, chunk_size):
        end = min(start + chunk_size - 1, file_size - 1)

        response = requests.post(
            f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={
                "operation": "get_object",
                "parameters": {
                    "key": file_key,
                    "range": f"bytes={start}-{end}"
                }
            }
        )

        chunk_data = response.json()
        chunks.append(base64.b64decode(chunk_data["content"]))

    return b''.join(chunks)
```

---

## Performance Optimization

### Caching File Metadata

Cache file listings to reduce API calls:

```python
from datetime import datetime, timedelta

class FileStorageCache:
    def __init__(self, ttl_minutes=5):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get_file_list(self, source_id, prefix):
        """Get cached file list or fetch fresh."""
        cache_key = f"{source_id}:{prefix}"

        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.ttl:
                return cached_data

        # Fetch fresh data
        files = list_files_by_prefix(source_id, prefix)
        self.cache[cache_key] = (files, datetime.now())
        return files

cache = FileStorageCache(ttl_minutes=5)
files = cache.get_file_list("src_123", "documents/")
```

### Conditional Requests

Use ETags for conditional downloads:

```python
def get_file_if_modified(source_id, file_key, etag=None):
    """Download file only if it has changed."""
    params = {"key": file_key}

    if etag:
        params["if_none_match"] = etag

    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "operation": "get_object",
            "parameters": params
        }
    )

    if response.status_code == 304:
        return None  # File not modified

    return response.json()
```

---

## Error Handling

### Common Errors

```python
class FileStorageError(Exception):
    """Base exception for file storage errors."""
    pass

class FileNotFoundError(FileStorageError):
    """File does not exist."""
    pass

class AccessDeniedError(FileStorageError):
    """Permission denied to access file."""
    pass

def safe_get_file(source_id, file_key):
    """Get file with error handling."""
    try:
        response = requests.post(
            f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={
                "operation": "get_object",
                "parameters": {"key": file_key}
            },
            timeout=30
        )

        if response.status_code == 404:
            raise FileNotFoundError(f"File not found: {file_key}")
        elif response.status_code == 403:
            raise AccessDeniedError(f"Access denied: {file_key}")
        elif response.status_code >= 500:
            raise FileStorageError("Storage service unavailable")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        raise FileStorageError("Request timeout")
    except requests.exceptions.ConnectionError:
        raise FileStorageError("Connection failed")
```

---

## Security Considerations

### Access Control

Implement proper access control:

```python
def validate_file_access(user_id, file_key):
    """Validate user has permission to access file."""
    # Check if file belongs to user's workspace
    allowed_prefix = f"users/{user_id}/"

    if not file_key.startswith(allowed_prefix):
        raise AccessDeniedError("User cannot access this file")

    return True

def get_user_file(source_id, user_id, file_key):
    """Get file with access validation."""
    validate_file_access(user_id, file_key)
    return safe_get_file(source_id, file_key)
```

### Sensitive Data Handling

Be cautious with sensitive files:

```python
SENSITIVE_EXTENSIONS = ['.key', '.pem', '.env', '.credentials']

def is_sensitive_file(file_key):
    """Check if file contains sensitive data."""
    return any(file_key.endswith(ext) for ext in SENSITIVE_EXTENSIONS)

def get_file_with_audit(source_id, file_key, user_id):
    """Get file with audit logging."""
    if is_sensitive_file(file_key):
        log_sensitive_access(user_id, file_key)

    return safe_get_file(source_id, file_key)
```

---

## Testing

### Unit Testing File Operations

```python
import unittest
from unittest.mock import patch, Mock

class TestFileStorageProxy(unittest.TestCase):

    @patch('requests.post')
    def test_get_file_success(self, mock_post):
        """Test successful file retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "test.txt",
            "content": base64.b64encode(b"test content").decode(),
            "content_type": "text/plain"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = safe_get_file("src_123", "test.txt")

        self.assertEqual(result["key"], "test.txt")
        self.assertEqual(result["content_type"], "text/plain")

    @patch('requests.post')
    def test_file_not_found(self, mock_post):
        """Test file not found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        with self.assertRaises(FileNotFoundError):
            safe_get_file("src_123", "nonexistent.txt")
```

---

## Best Practices

### 1. File Path Validation
Always validate and sanitize file paths:

```python
import os

def sanitize_file_path(file_path):
    """Sanitize file path to prevent directory traversal."""
    # Remove any parent directory references
    clean_path = os.path.normpath(file_path)

    if clean_path.startswith('..') or clean_path.startswith('/'):
        raise ValueError("Invalid file path")

    return clean_path
```

### 2. Content Type Validation
Validate file types before processing:

```python
ALLOWED_CONTENT_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'text/csv',
    'application/json'
]

def validate_content_type(content_type):
    """Validate file content type."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Content type not allowed: {content_type}")
```

### 3. Size Limits
Enforce file size limits:

```python
MAX_FILE_SIZE_MB = 50

def check_file_size(source_id, file_key):
    """Check if file size is within limits."""
    metadata = get_file_info(source_id, file_key)
    size_mb = metadata["size"] / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large: {size_mb:.2f}MB")

    return True
```

---

## Next Steps

- **[API Sources](./api-sources.md)** - Learn about API source proxying
- **[Quickstart Guide](../quickstart.md)** - Build your first integration
- **[Authentication](../embedded/api/authentication.md)** - Set up secure authentication

## Additional Resources

- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Azure Blob Storage Documentation](https://docs.microsoft.com/azure/storage/blobs/)
- [Airbyte S3 Source](https://docs.airbyte.com/integrations/sources/s3)
