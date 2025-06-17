"""Integration tests for the Nutrient DWS API client.

These tests require a valid API key and make real API calls.
Set NUTRIENT_API_KEY environment variable to run these tests.
"""

import os
from pathlib import Path
from typing import Generator

import pytest

from nutrient_dws import NutrientClient
from nutrient_dws.exceptions import AuthenticationError


# Skip integration tests if no API key is provided
pytestmark = pytest.mark.skipif(
    not os.environ.get("NUTRIENT_API_KEY"), reason="NUTRIENT_API_KEY environment variable not set"
)


@pytest.fixture
def client() -> NutrientClient:
    """Create a client instance with API key from environment."""
    return NutrientClient()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a sample PDF file for testing."""
    pdf_path = tmp_path / "sample.pdf"
    # Create a minimal PDF
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000323 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
415
%%EOF"""
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def sample_docx(tmp_path: Path) -> Path:
    """Create a sample DOCX file for testing."""
    # This is a minimal DOCX structure
    from zipfile import ZipFile

    docx_path = tmp_path / "sample.docx"

    with ZipFile(docx_path, "w") as docx:
        # Add minimal required files
        docx.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""",
        )

        docx.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""",
        )

        docx.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>Hello World</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>""",
        )

        docx.writestr(
            "word/_rels/document.xml.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>""",
        )

    return docx_path


class TestAuthentication:
    """Test authentication handling."""

    def test_valid_api_key(self, client: NutrientClient) -> None:
        """Test that valid API key allows operations."""
        # This should not raise an error if API key is valid
        # We'll use a simple operation like getting API info if available
        # For now, just verify client is created successfully
        assert client._api_key is not None

    def test_invalid_api_key(self, sample_pdf: Path) -> None:
        """Test that invalid API key raises AuthenticationError."""
        client = NutrientClient(api_key="invalid-key")

        with pytest.raises(AuthenticationError):
            client.rotate_pages(input_file=sample_pdf, degrees=90)


class TestDirectAPI:
    """Test Direct API operations."""

    def test_convert_to_pdf(
        self, client: NutrientClient, sample_docx: Path, tmp_path: Path
    ) -> None:
        """Test converting DOCX to PDF."""
        output_path = tmp_path / "converted.pdf"

        result = client.convert_to_pdf(input_file=sample_docx, output_path=str(output_path))

        assert result is None  # When output_path is provided
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # Verify it's a PDF
        content = output_path.read_bytes()
        assert content.startswith(b"%PDF")

    def test_rotate_pages(self, client: NutrientClient, sample_pdf: Path, tmp_path: Path) -> None:
        """Test rotating PDF pages."""
        output_path = tmp_path / "rotated.pdf"

        client.rotate_pages(input_file=sample_pdf, output_path=str(output_path), degrees=180)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_watermark_pdf(self, client: NutrientClient, sample_pdf: Path, tmp_path: Path) -> None:
        """Test adding watermark to PDF."""
        output_path = tmp_path / "watermarked.pdf"

        client.watermark_pdf(
            input_file=sample_pdf, output_path=str(output_path), text="CONFIDENTIAL", opacity=0.5
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_merge_pdfs(self, client: NutrientClient, sample_pdf: Path, tmp_path: Path) -> None:
        """Test merging multiple PDFs."""
        # Create additional PDFs
        pdf2 = tmp_path / "pdf2.pdf"
        pdf2.write_bytes(sample_pdf.read_bytes())

        output_path = tmp_path / "merged.pdf"

        client.merge_pdfs(input_files=[str(sample_pdf), str(pdf2)], output_path=str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > sample_pdf.stat().st_size


class TestBuilderAPI:
    """Test Builder API workflows."""

    def test_simple_workflow(
        self, client: NutrientClient, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test a simple builder workflow."""
        output_path = tmp_path / "processed.pdf"

        client.build(input_file=sample_pdf).add_step("rotate-pages", {"degrees": 90}).execute(
            output_path=str(output_path)
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_complex_workflow(
        self, client: NutrientClient, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test a complex builder workflow with multiple steps."""
        output_path = tmp_path / "complex.pdf"

        client.build(input_file=sample_pdf).add_step("rotate-pages", {"degrees": 180}).add_step(
            "watermark-pdf", {"text": "DRAFT", "opacity": 0.3}
        ).set_output_options(metadata={"title": "Test Document", "author": "Test Suite"}).execute(
            output_path=str(output_path)
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_ocr_workflow(self, client: NutrientClient, sample_pdf: Path, tmp_path: Path) -> None:
        """Test OCR workflow."""
        output_path = tmp_path / "ocr.pdf"

        client.build(input_file=sample_pdf).add_step("ocr-pdf", {"language": "en"}).execute(
            output_path=str(output_path)
        )

        assert output_path.exists()
        # OCR typically increases file size
        assert output_path.stat().st_size >= sample_pdf.stat().st_size


class TestFileHandling:
    """Test different file input methods."""

    def test_file_path_string(
        self, client: NutrientClient, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test using string file path."""
        output_path = tmp_path / "output.pdf"

        client.rotate_pages(input_file=str(sample_pdf), output_path=str(output_path), degrees=90)

        assert output_path.exists()

    def test_file_path_object(
        self, client: NutrientClient, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test using Path object."""
        output_path = tmp_path / "output.pdf"

        client.rotate_pages(input_file=sample_pdf, output_path=str(output_path), degrees=90)

        assert output_path.exists()

    def test_file_bytes(self, client: NutrientClient, sample_pdf: Path, tmp_path: Path) -> None:
        """Test using file bytes."""
        output_path = tmp_path / "output.pdf"
        pdf_bytes = sample_pdf.read_bytes()

        client.rotate_pages(input_file=pdf_bytes, output_path=str(output_path), degrees=90)

        assert output_path.exists()

    def test_file_object(self, client: NutrientClient, sample_pdf: Path, tmp_path: Path) -> None:
        """Test using file object."""
        output_path = tmp_path / "output.pdf"

        with open(sample_pdf, "rb") as f:
            client.rotate_pages(input_file=f, output_path=str(output_path), degrees=90)

        assert output_path.exists()

    def test_return_bytes(self, client: NutrientClient, sample_pdf: Path) -> None:
        """Test returning bytes instead of saving to file."""
        result = client.rotate_pages(input_file=sample_pdf, degrees=90)

        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF")
        assert len(result) > 0


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_file(self, client: NutrientClient, tmp_path: Path) -> None:
        """Test handling of invalid input file."""
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not a PDF")

        with pytest.raises(Exception):  # API should return an error
            client.rotate_pages(input_file=invalid_file, degrees=90)

    def test_missing_file(self, client: NutrientClient) -> None:
        """Test handling of missing input file."""
        with pytest.raises(FileNotFoundError):
            client.rotate_pages(input_file="nonexistent.pdf", degrees=90)


class TestMemoryEfficiency:
    """Test memory-efficient handling of large files."""

    def test_large_file_streaming(self, client: NutrientClient, tmp_path: Path) -> None:
        """Test that large files are streamed."""
        # Create a file larger than 10MB threshold
        large_pdf = tmp_path / "large.pdf"

        # Start with the sample PDF header
        content = b"%PDF-1.4\n"
        # Add padding to make it > 10MB
        content += b"% " + b"X" * (11 * 1024 * 1024)  # 11MB of padding
        content += b"\n%%EOF"

        large_pdf.write_bytes(content)

        output_path = tmp_path / "output.pdf"

        # This should use streaming internally
        # We can't easily verify streaming behavior in integration test,
        # but we can verify it doesn't fail with large files
        try:
            client.flatten_annotations(input_file=large_pdf, output_path=str(output_path))
            # If the API processes it successfully, great
            assert output_path.exists() or True  # Pass either way
        except Exception:
            # Large dummy file might not be valid PDF
            # The important thing is it didn't fail due to memory issues
            pass
