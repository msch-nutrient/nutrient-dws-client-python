# Supported Operations

This document lists all operations currently supported by the Nutrient DWS API through this Python client.

## Direct API Methods

The following methods are available on the `NutrientClient` instance:

### 1. `flatten_annotations(input_file, output_path=None)`
Flattens all annotations and form fields in a PDF, converting them to static page content.

**Parameters:**
- `input_file`: PDF file (path, bytes, or file-like object)
- `output_path`: Optional path to save output

**Example:**
```python
client.flatten_annotations("document.pdf", "flattened.pdf")
```

### 2. `rotate_pages(input_file, output_path=None, degrees=0, page_indexes=None)`
Rotates pages in a PDF.

**Parameters:**
- `input_file`: PDF file
- `output_path`: Optional output path
- `degrees`: Rotation angle (90, 180, 270, or -90)
- `page_indexes`: Optional list of page indexes to rotate (0-based)

**Example:**
```python
# Rotate all pages 90 degrees
client.rotate_pages("document.pdf", "rotated.pdf", degrees=90)

# Rotate specific pages
client.rotate_pages("document.pdf", "rotated.pdf", degrees=180, page_indexes=[0, 2])
```

### 3. `ocr_pdf(input_file, output_path=None, language="english")`
Applies OCR to make a PDF searchable.

**Parameters:**
- `input_file`: PDF file
- `output_path`: Optional output path
- `language`: OCR language - supported values:
  - `"english"` or `"eng"` - English
  - `"deu"` or `"german"` - German

**Example:**
```python
client.ocr_pdf("scanned.pdf", "searchable.pdf", language="english")
```

### 4. `watermark_pdf(input_file, output_path=None, text=None, image_url=None, width=200, height=100, opacity=1.0, position="center")`
Adds a watermark to all pages of a PDF.

**Parameters:**
- `input_file`: PDF file
- `output_path`: Optional output path
- `text`: Text for watermark (either text or image_url required)
- `image_url`: URL of image for watermark
- `width`: Width in points (required)
- `height`: Height in points (required)
- `opacity`: Opacity from 0.0 to 1.0
- `position`: One of: "top-left", "top-center", "top-right", "center", "bottom-left", "bottom-center", "bottom-right"

**Example:**
```python
# Text watermark
client.watermark_pdf(
    "document.pdf",
    "watermarked.pdf",
    text="CONFIDENTIAL",
    width=300,
    height=150,
    opacity=0.5,
    position="center"
)
```

### 5. `apply_redactions(input_file, output_path=None)`
Applies redaction annotations to permanently remove content.

**Parameters:**
- `input_file`: PDF file with redaction annotations
- `output_path`: Optional output path

**Example:**
```python
client.apply_redactions("document_with_redactions.pdf", "redacted.pdf")
```

### 6. `merge_pdfs(input_files, output_path=None)`
Merges multiple PDF files into one.

**Parameters:**
- `input_files`: List of PDF files to merge
- `output_path`: Optional output path

**Example:**
```python
client.merge_pdfs(
    ["document1.pdf", "document2.pdf", "document3.pdf"],
    "merged.pdf"
)
```

## Builder API

The Builder API allows chaining multiple operations:

```python
client.build(input_file="document.pdf") \
    .add_step("rotate-pages", {"degrees": 90}) \
    .add_step("ocr-pdf", {"language": "english"}) \
    .add_step("watermark-pdf", {
        "text": "DRAFT",
        "width": 200,
        "height": 100,
        "opacity": 0.3
    }) \
    .add_step("flatten-annotations") \
    .execute(output_path="processed.pdf")
```

### Supported Builder Actions

1. **flatten-annotations** - No parameters required
2. **rotate-pages** - Parameters: `degrees`, `page_indexes` (optional)
3. **ocr-pdf** - Parameters: `language`
4. **watermark-pdf** - Parameters: `text` or `image_url`, `width`, `height`, `opacity`, `position`
5. **apply-redactions** - No parameters required

## API Limitations

The following operations are **NOT** currently supported by the API:

- Document conversion (Office to PDF, HTML to PDF)
- PDF to image export
- PDF splitting
- Form filling
- Digital signatures
- Compression/optimization
- Linearization
- Creating redactions (only applying existing ones)
- Instant JSON annotations
- XFDF annotations

## Language Support

OCR currently supports:
- English (`"english"` or `"eng"`)
- German (`"deu"` or `"german"`)

## File Input Types

All methods accept files as:
- String paths: `"document.pdf"`
- Path objects: `Path("document.pdf")`
- Bytes: `b"...pdf content..."`
- File-like objects: `open("document.pdf", "rb")`

## Error Handling

Common exceptions:
- `AuthenticationError` - Invalid or missing API key
- `APIError` - General API errors with status code
- `ValidationError` - Invalid parameters
- `FileNotFoundError` - File not found
- `ValueError` - Invalid input values