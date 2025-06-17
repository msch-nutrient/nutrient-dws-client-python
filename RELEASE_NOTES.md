# Release Notes - v1.0.0

**Release Date**: June 17, 2024

We are excited to announce the first release of the official Python client library for Nutrient Document Web Services (DWS) API! This library provides a comprehensive, Pythonic interface for document processing operations including PDF manipulation, OCR, watermarking, and more.

## 🎉 Highlights

### Dual API Design
The library offers two complementary ways to interact with the Nutrient API:

1. **Direct API** - Simple method calls for single operations
2. **Builder API** - Fluent interface for complex, multi-step workflows

### Automatic Office Document Conversion
A major discovery during development: the Nutrient API automatically converts Office documents (DOCX, XLSX, PPTX) to PDF when processing them. This means you can:
- Apply any PDF operation directly to Office documents
- Mix PDFs and Office documents in merge operations
- Skip explicit conversion steps in your workflows

### Enterprise-Ready Features
- **Robust Error Handling**: Comprehensive exception hierarchy for different error scenarios
- **Automatic Retries**: Built-in retry logic for transient failures
- **Connection Pooling**: Optimized performance for multiple requests
- **Large File Support**: Automatic streaming for files over 10MB
- **Type Safety**: Full type hints for better IDE support

## 📦 Installation

```bash
pip install nutrient-dws
```

## 🚀 Quick Start

```python
from nutrient_dws import NutrientClient

# Initialize client
client = NutrientClient(api_key="your-api-key")

# Direct API - Single operation
client.rotate_pages("document.pdf", output_path="rotated.pdf", degrees=90)

# Convert Office document to PDF (automatic!)
client.convert_to_pdf("report.docx", output_path="report.pdf")

# Builder API - Complex workflow
client.build(input_file="scan.pdf") \
    .add_step("ocr-pdf", {"language": "english"}) \
    .add_step("watermark-pdf", {"text": "CONFIDENTIAL"}) \
    .add_step("flatten-annotations") \
    .execute(output_path="processed.pdf")

# Merge PDFs and Office documents together
client.merge_pdfs([
    "chapter1.pdf",
    "chapter2.docx",
    "appendix.xlsx"
], output_path="complete_document.pdf")
```

## 🔧 Supported Operations

- **convert_to_pdf** - Convert Office documents to PDF
- **flatten_annotations** - Flatten form fields and annotations
- **rotate_pages** - Rotate specific or all pages
- **ocr_pdf** - Make scanned PDFs searchable (English & German)
- **watermark_pdf** - Add text or image watermarks
- **apply_redactions** - Apply redaction annotations
- **merge_pdfs** - Combine multiple documents

## 🛡️ Error Handling

The library provides specific exceptions for different error scenarios:

```python
from nutrient_dws import NutrientClient, AuthenticationError, ValidationError

try:
    client = NutrientClient(api_key="your-api-key")
    result = client.ocr_pdf("scan.pdf")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid parameters: {e.errors}")
```

## 📚 Documentation

- [README](https://github.com/jdrhyne/nutrient-dws-client-python/blob/main/README.md) - Getting started guide
- [SUPPORTED_OPERATIONS](https://github.com/jdrhyne/nutrient-dws-client-python/blob/main/SUPPORTED_OPERATIONS.md) - Detailed operation documentation
- [API Reference](https://nutrient-dws-client-python.readthedocs.io) - Coming soon!

## 🧪 Quality Assurance

- **Test Coverage**: 92.46% with 82 unit tests
- **Type Checking**: Full mypy compliance
- **Code Quality**: Enforced with ruff and pre-commit hooks
- **CI/CD**: Automated testing on Python 3.8-3.12

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/jdrhyne/nutrient-dws-client-python/blob/main/CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Special thanks to the Nutrient team for their excellent API and documentation.

---

**Note**: This is the initial release. We're actively working on additional features including more language support for OCR, additional file format support, and performance optimizations. Stay tuned!

For questions or support, please [open an issue](https://github.com/jdrhyne/nutrient-dws-client-python/issues).