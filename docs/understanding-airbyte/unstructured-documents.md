# Parsing Unstructured Documents

Airbyte provides capabilities for extracting and processing unstructured text documents from various sources. This document explains how Airbyte's unstructured document parsing works, which connectors support it, and how to use it.

## Overview

Traditional data integration typically focuses on structured data with well-defined schemas. However, many organizations need to extract value from unstructured documents such as:

- Text documents (Word, PDF, TXT)
- Emails and email attachments
- Web pages and HTML content
- Presentations and spreadsheets
- Scanned documents with OCR text

Airbyte's unstructured document parsing capabilities address these needs by extracting text content from various document formats and making it available for analysis, search, or AI processing.

## How Unstructured Document Parsing Works

When using unstructured document parsing:

1. The source connector identifies documents to be processed.
2. The document parser extracts text content from the documents.
3. The extracted text is normalized and cleaned.
4. The text is sent as records to the destination.

This process enables you to work with text from documents in the same way you work with other structured data in Airbyte.

## Supported Connectors

Unstructured document parsing is currently supported by the following connectors:

### Sources

- Google Drive
- Microsoft SharePoint
- S3
- SFTP (Gen 2)

## Using Unstructured Document Parsing

To use unstructured document parsing:

1. Configure a connection using a source that supports document parsing.
2. Enable the document parsing option in the connection settings.
3. Configure any additional parsing options (e.g., language detection, OCR settings).
4. The parsed text will be extracted and sent to your destination.

### Configuration Example

When configuring a connection between Google Drive (source) and a destination:

1. Set up the Google Drive source with your account credentials.
2. Enable the "Parse Documents" option in the advanced settings.
3. Configure document type filters if needed (e.g., only process PDFs).
4. Complete the connection setup with your desired destination.

## Limitations

- Document parsing may not extract formatting, images, or complex layouts.
- Very large documents may be truncated based on size limits.
- OCR accuracy depends on document quality and language support.
- Some document types may require specific parser configurations.

## Technical Implementation

Unstructured document parsing is implemented using the "Unstructured Text Documents" parser in the Python Files CDK. This parser leverages open-source libraries to extract text from various document formats.

Connectors that support this feature have the `supportsUnstructuredDocumentParsing: true` flag in their metadata.yaml file.

## Future Enhancements

The unstructured document parsing capability is being actively developed with plans to support more document types and extraction features. Future enhancements will include:

- Improved layout preservation.
- Better table extraction from documents.
- Enhanced metadata extraction.
- Support for more document formats.
- Integration with AI models for content analysis.

## Related Topics

- [File Sync](./file-transfer.md) - Learn about transferring files between systems without parsing
- [Permission Sync](./permission-sync.md) - Learn about transferring access control information between systems
