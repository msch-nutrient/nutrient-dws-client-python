# Nutrient DWS Python Client

A Python client library for the [Nutrient Document Web Services (DWS) API](https://www.nutrient.io/). This library provides a Pythonic interface to interact with Nutrient's document processing services, supporting both Direct API calls and Builder API workflows.

## Features

- 🚀 **Two API styles**: Direct API for single operations, Builder API for complex workflows
- 📄 **Comprehensive document tools**: Convert, merge, rotate, OCR, watermark, and more
- 🔄 **Automatic retries**: Built-in retry logic for transient failures
- 📁 **Flexible file handling**: Support for file paths, bytes, and file-like objects
- 🔒 **Type-safe**: Full type hints for better IDE support
- ⚡ **Streaming support**: Memory-efficient processing of large files
- 🧪 **Well-tested**: Comprehensive test suite with high coverage

## Installation

```bash
pip install nutrient-dws
```

## Quick Start

```python
from nutrient import NutrientClient

# Initialize the client
client = NutrientClient(api_key="your-api-key")

# Direct API - Convert Office document to PDF
pdf = client.convert_to_pdf(
    input_file="document.docx",
    output_path="converted.pdf"
)

# Builder API - Chain multiple operations
client.build(input_file="document.pdf") \
    .add_step("rotate-pages", {"degrees": 90}) \
    .add_step("ocr-pdf", {"language": "en"}) \
    .add_step("watermark-pdf", {"text": "CONFIDENTIAL"}) \
    .execute(output_path="processed.pdf")
```

## Authentication

The client supports API key authentication through multiple methods:

```python
# 1. Pass directly to client
client = NutrientClient(api_key="your-api-key")

# 2. Set environment variable
# export NUTRIENT_API_KEY=your-api-key
client = NutrientClient()  # Will use env variable

# 3. Use context manager for automatic cleanup
with NutrientClient(api_key="your-api-key") as client:
    client.convert_to_pdf("document.docx")
```

## Direct API Examples

### Convert to PDF

```python
# Convert Office document to PDF
client.convert_to_pdf(
    input_file="presentation.pptx",
    output_path="presentation.pdf"
)

# Convert with options
client.convert_to_pdf(
    input_file="spreadsheet.xlsx",
    output_path="spreadsheet.pdf",
    page_range="1-3"
)
```

### Merge PDFs

```python
# Merge multiple PDFs
client.merge_pdfs(
    input_files=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_path="merged.pdf"
)
```

### OCR PDF

```python
# Add OCR layer to scanned PDF
client.ocr_pdf(
    input_file="scanned.pdf",
    output_path="searchable.pdf",
    language="en"
)
```

### Rotate Pages

```python
# Rotate all pages
client.rotate_pages(
    input_file="document.pdf",
    output_path="rotated.pdf",
    degrees=180
)

# Rotate specific pages
client.rotate_pages(
    input_file="document.pdf",
    output_path="rotated.pdf",
    degrees=90,
    page_indexes=[0, 2, 4]  # Pages 1, 3, and 5
)
```

### Watermark PDF

```python
# Add text watermark
client.watermark_pdf(
    input_file="document.pdf",
    output_path="watermarked.pdf",
    text="DRAFT",
    opacity=0.5
)

# Add image watermark
client.watermark_pdf(
    input_file="document.pdf",
    output_path="watermarked.pdf",
    image_url="https://example.com/logo.png",
    position="center"
)
```

## Builder API Examples

The Builder API allows you to chain multiple operations in a single workflow:

```python
# Complex document processing pipeline
result = client.build(input_file="raw-scan.pdf") \
    .add_step("ocr-pdf", {"language": "en"}) \
    .add_step("rotate-pages", {"degrees": -90, "page_indexes": [0]}) \
    .add_step("watermark-pdf", {
        "text": "PROCESSED",
        "opacity": 0.3,
        "position": "top-right"
    }) \
    .add_step("flatten-annotations") \
    .set_output_options(
        metadata={"title": "Processed Document", "author": "DWS Client"},
        optimize=True
    ) \
    .execute(output_path="final.pdf")
```

## File Input Options

The library supports multiple ways to provide input files:

```python
# File path (string or Path object)
client.convert_to_pdf("document.docx")
client.convert_to_pdf(Path("document.docx"))

# Bytes
with open("document.docx", "rb") as f:
    file_bytes = f.read()
client.convert_to_pdf(file_bytes)

# File-like object
with open("document.docx", "rb") as f:
    client.convert_to_pdf(f)

# URL (for supported operations)
client.import_from_url("https://example.com/document.pdf")
```

## Error Handling

The library provides specific exceptions for different error scenarios:

```python
from nutrient import (
    NutrientError,
    AuthenticationError,
    APIError,
    ValidationError,
    TimeoutError,
    FileProcessingError
)

try:
    client.convert_to_pdf("document.docx")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid parameters: {e.errors}")
except APIError as e:
    print(f"API error: {e.status_code} - {e.message}")
except TimeoutError:
    print("Request timed out")
except FileProcessingError as e:
    print(f"File processing failed: {e}")
```

## Advanced Configuration

### Custom Timeout

```python
# Set timeout to 10 minutes for large files
client = NutrientClient(api_key="your-api-key", timeout=600)
```

### Streaming Large Files

Files larger than 10MB are automatically streamed to avoid memory issues:

```python
# This will stream the file instead of loading it into memory
client.convert_to_pdf("large-presentation.pptx")
```

## Available Tools

### Document Conversion
- `convert_to_pdf` - Convert Office documents to PDF
- `convert_from_pdf` - Convert PDF to Office formats
- `convert_pdf_page_to_image` - Convert PDF pages to images
- `import_from_url` - Import documents from URLs

### PDF Manipulation
- `merge_pdfs` - Merge multiple PDFs
- `split_pdf` - Split PDF into multiple files
- `rotate_pages` - Rotate PDF pages
- `delete_pages` - Remove pages from PDF
- `duplicate_pages` - Duplicate pages in PDF
- `move_pages` - Reorder pages in PDF

### PDF Enhancement
- `ocr_pdf` - Add searchable text layer
- `watermark_pdf` - Add text or image watermarks
- `flatten_annotations` - Flatten form fields and annotations
- `linearize_pdf` - Optimize for web viewing

### PDF Security
- `apply_redactions` - Permanently remove sensitive content
- `create_redactions` - Mark content for redaction
- `sanitize_pdf` - Remove potentially harmful content

### Annotations and Forms
- `apply_instant_json` - Apply Nutrient Instant JSON annotations
- `export_instant_json` - Export annotations as Instant JSON
- `apply_xfdf` - Apply XFDF annotations
- `export_xfdf` - Export annotations as XFDF
- `export_pdf_info` - Extract PDF metadata and structure

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/jdrhyne/nutrient-dws-client-python.git
cd nutrient-dws-client-python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy src tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nutrient --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@nutrient.io
- 📚 Documentation: https://www.nutrient.io/docs/
- 🐛 Issues: https://github.com/jdrhyne/nutrient-dws-client-python/issues