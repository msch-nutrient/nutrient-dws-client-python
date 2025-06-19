# Supported Operations

This document lists all operations currently supported by the Nutrient DWS API through this Python client.

## 🎯 Important Discovery: Implicit Document Conversion

The Nutrient DWS API automatically converts Office documents (DOCX, XLSX, PPTX) to PDF when processing them. This means:

- **No explicit conversion needed** - Just pass your Office documents to any method
- **All methods accept Office documents** - `rotate_pages()`, `ocr_pdf()`, etc. work with DOCX files
- **Seamless operation chaining** - Convert and process in one API call

### Example:
```python
# This automatically converts DOCX to PDF and rotates it!
client.rotate_pages("document.docx", degrees=90)

# Merge PDFs and Office documents together
client.merge_pdfs(["file1.pdf", "file2.docx", "spreadsheet.xlsx"])
```

## Direct API Methods

The following methods are available on the `NutrientClient` instance:

### 1. `convert_to_pdf(input_file, output_path=None)`
Converts Office documents to PDF format using implicit conversion.

**Parameters:**
- `input_file`: Office document (DOCX, XLSX, PPTX)
- `output_path`: Optional path to save output

**Example:**
```python
# Convert DOCX to PDF
client.convert_to_pdf("document.docx", "document.pdf")

# Convert and get bytes
pdf_bytes = client.convert_to_pdf("spreadsheet.xlsx")
```

**Note:** HTML files are not currently supported.

### 2. `flatten_annotations(input_file, output_path=None)`
Flattens all annotations and form fields in a PDF, converting them to static page content.

**Parameters:**
- `input_file`: PDF or Office document
- `output_path`: Optional path to save output

**Example:**
```python
client.flatten_annotations("document.pdf", "flattened.pdf")
# Works with Office docs too!
client.flatten_annotations("form.docx", "flattened.pdf")
```

### 3. `rotate_pages(input_file, output_path=None, degrees=0, page_indexes=None)`
Rotates pages in a PDF or converts Office document to PDF and rotates.

**Parameters:**
- `input_file`: PDF or Office document
- `output_path`: Optional output path
- `degrees`: Rotation angle (90, 180, 270, or -90)
- `page_indexes`: Optional list of page indexes to rotate (0-based)

**Example:**
```python
# Rotate all pages 90 degrees
client.rotate_pages("document.pdf", "rotated.pdf", degrees=90)

# Works with Office documents too!
client.rotate_pages("presentation.pptx", "rotated.pdf", degrees=180)

# Rotate specific pages
client.rotate_pages("document.pdf", "rotated.pdf", degrees=180, page_indexes=[0, 2])
```

### 4. `ocr_pdf(input_file, output_path=None, language="english")`
Applies OCR to make a PDF searchable. Converts Office documents to PDF first if needed.

**Parameters:**
- `input_file`: PDF or Office document
- `output_path`: Optional output path
- `language`: OCR language - supported values:
  - `"english"` or `"eng"` - English
  - `"deu"` or `"german"` - German

**Example:**
```python
client.ocr_pdf("scanned.pdf", "searchable.pdf", language="english")
# Convert DOCX to searchable PDF
client.ocr_pdf("document.docx", "searchable.pdf", language="eng")
```

### 5. `watermark_pdf(input_file, output_path=None, text=None, image_url=None, width=200, height=100, opacity=1.0, position="center")`
Adds a watermark to all pages of a PDF. Converts Office documents to PDF first if needed.

**Parameters:**
- `input_file`: PDF or Office document
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

### 6. `apply_redactions(input_file, output_path=None)`
Applies redaction annotations to permanently remove content. Converts Office documents to PDF first if needed.

**Parameters:**
- `input_file`: PDF or Office document with redaction annotations
- `output_path`: Optional output path

**Example:**
```python
client.apply_redactions("document_with_redactions.pdf", "redacted.pdf")
```

### 7. `merge_pdfs(input_files, output_path=None)`
Merges multiple files into one PDF. Automatically converts Office documents to PDF before merging.

**Parameters:**
- `input_files`: List of files to merge (PDFs and/or Office documents)
- `output_path`: Optional output path

**Example:**
```python
# Merge PDFs only
client.merge_pdfs(
    ["document1.pdf", "document2.pdf", "document3.pdf"],
    "merged.pdf"
)

# Mix PDFs and Office documents - they'll be converted automatically!
client.merge_pdfs(
    ["report.pdf", "spreadsheet.xlsx", "presentation.pptx"],
    "combined.pdf"
)
```

### 8. `split_pdf(input_file, page_ranges=None, output_paths=None)`
Splits a PDF into multiple documents by page ranges.

**Parameters:**
- `input_file`: PDF file to split
- `page_ranges`: List of page range dictionaries with `start`/`end` keys (0-based indexing)
- `output_paths`: Optional list of paths to save output files

**Returns:**
- List of PDF bytes for each split, or empty list if `output_paths` provided

**Example:**
```python
# Split into custom ranges
parts = client.split_pdf(
    "document.pdf", 
    page_ranges=[
        {"start": 0, "end": 5},      # Pages 1-5
        {"start": 5, "end": 10},     # Pages 6-10
        {"start": 10}                # Pages 11 to end
    ]
)

# Save to specific files
client.split_pdf(
    "document.pdf",
    page_ranges=[{"start": 0, "end": 2}, {"start": 2}],
    output_paths=["part1.pdf", "part2.pdf"]
)

# Default behavior (extracts first page)
pages = client.split_pdf("document.pdf")
```

## Builder API

The Builder API allows chaining multiple operations. Like the Direct API, it automatically converts Office documents to PDF when needed:

```python
# Works with PDFs
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

# Also works with Office documents!
client.build(input_file="report.docx") \
    .add_step("watermark-pdf", {"text": "CONFIDENTIAL", "width": 300, "height": 150}) \
    .add_step("flatten-annotations") \
    .execute(output_path="watermarked_report.pdf")
```

### Supported Builder Actions

1. **flatten-annotations** - No parameters required
2. **rotate-pages** - Parameters: `degrees`, `page_indexes` (optional)
3. **ocr-pdf** - Parameters: `language`
4. **watermark-pdf** - Parameters: `text` or `image_url`, `width`, `height`, `opacity`, `position`
5. **apply-redactions** - No parameters required

## API Limitations

The following operations are **NOT** currently supported by the API:

- HTML to PDF conversion (only Office documents are supported)
- PDF to image export
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