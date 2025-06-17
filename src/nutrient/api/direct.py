"""Direct API methods for individual document processing tools.

This file provides convenient methods that wrap the Nutrient Build API
for common document processing operations.
"""

from typing import TYPE_CHECKING, Any, List, Optional

from nutrient.file_handler import FileInput

if TYPE_CHECKING:
    from nutrient.client import NutrientClient


class DirectAPIMixin:
    """Mixin class containing Direct API methods.
    
    These methods provide a simplified interface to common document
    processing operations. They internally use the Build API.
    """

    def _process_file(
        self: "NutrientClient",
        tool: str,
        input_file: FileInput,
        output_path: Optional[str] = None,
        **options: Any,
    ) -> Optional[bytes]:
        """Process file method that will be provided by NutrientClient."""
        raise NotImplementedError("This method is provided by NutrientClient")

    def convert_to_pdf(self, input_file: FileInput, output_path: Optional[str] = None) -> Optional[bytes]:
        """Convert a document to PDF

        Convert various document formats (DOCX, XLSX, PPTX, etc.) to PDF.

        Args:
            input_file: Input file (path, bytes, or file-like object).
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("convert-to-pdf", input_file, output_path)

    def convert_to_pdfa(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        conformance_level: str = "2b",
    ) -> Optional[bytes]:
        """Convert a document to PDF/A

        Convert documents to PDF/A format for long-term archiving.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        conformance_level: PDF/A conformance level (e.g., '2b', '3b')
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("convert-to-pdfa", input_file, output_path, conformance_level=conformance_level)

    def export_pdf_to_images(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        format: str = "png",
        dpi: int = 150,
        page_indexes: Optional[List[int]] = None,
    ) -> Optional[bytes]:
        """Export PDF pages as images

        Convert PDF pages to image files.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        format: Image format ('png', 'jpeg', 'webp')
        dpi: Image resolution in DPI
        page_indexes: List of page indexes to export (0-based)
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("export-pdf-to-images", input_file, output_path, format=format, dpi=dpi, page_indexes=page_indexes)

    def export_pdf_to_office(
        self,
        input_file: FileInput,
        format: str,
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Export PDF to Office format

        Convert PDF to Microsoft Office formats (DOCX, XLSX, PPTX).

        Args:
            input_file: Input file (path, bytes, or file-like object).
        format: Output format ('docx', 'xlsx', 'pptx')
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("export-pdf-to-office", input_file, output_path, format=format)

    def flatten_annotations(self, input_file: FileInput, output_path: Optional[str] = None) -> Optional[bytes]:
        """Flatten PDF annotations

        Flatten annotations and form fields in a PDF.

        Args:
            input_file: Input file (path, bytes, or file-like object).
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("flatten-annotations", input_file, output_path)

    def ocr_pdf(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        language: str = "en",
    ) -> Optional[bytes]:
        """Perform OCR on a PDF

        Apply optical character recognition to make scanned PDFs searchable.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        language: OCR language code (e.g., 'en', 'de', 'fr')
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("ocr-pdf", input_file, output_path, language=language)

    def redact_pdf(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        types: Optional[List[str]] = None,
    ) -> Optional[bytes]:
        """Redact sensitive information from PDF

        Use AI to automatically redact sensitive information from a PDF.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        types: Types of information to redact (e.g., 'email', 'phone', 'ssn')
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("redact-pdf", input_file, output_path, types=types)

    def rotate_pages(
        self,
        input_file: FileInput,
        degrees: int,
        output_path: Optional[str] = None,
        page_indexes: Optional[List[int]] = None,
    ) -> Optional[bytes]:
        """Rotate PDF pages

        Rotate pages in a PDF document.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        degrees: Rotation angle in degrees (90, 180, 270)
        page_indexes: List of page indexes to rotate (0-based). If not specified, all pages are rotated.
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("rotate-pages", input_file, output_path, degrees=degrees, page_indexes=page_indexes)

    def sign_pdf(
        self,
        input_file: FileInput,
        certificate_file: 'FileInput',
        certificate_password: str,
        output_path: Optional[str] = None,
        reason: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Optional[bytes]:
        """Digitally sign a PDF

        Add a digital signature to a PDF document.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        certificate_file: Digital certificate file (P12/PFX format)
        certificate_password: Certificate password
        reason: Reason for signing
        location: Location of signing
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("sign-pdf", input_file, output_path, certificate_file=certificate_file, certificate_password=certificate_password, reason=reason, location=location)

    def watermark_pdf(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        opacity: float = 0.5,
        position: str = "center",
    ) -> Optional[bytes]:
        """Add watermark to PDF

        Add text or image watermark to PDF pages.

        Args:
            input_file: Input file (path, bytes, or file-like object).
        text: Watermark text
        image_url: URL of watermark image
        opacity: Watermark opacity (0.0 to 1.0)
        position: Watermark position
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("watermark-pdf", input_file, output_path, text=text, image_url=image_url, opacity=opacity, position=position)
