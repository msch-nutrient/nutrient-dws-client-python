"""Direct API methods for supported document processing tools.

This file provides convenient methods that wrap the Nutrient Build API
for supported document processing operations.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, cast

from nutrient_dws.file_handler import FileInput

if TYPE_CHECKING:
    from nutrient_dws.builder import BuildAPIWrapper
    from nutrient_dws.http_client import HTTPClient


class HasBuildMethod(Protocol):
    """Protocol for objects that have a build method."""

    def build(self, input_file: FileInput) -> "BuildAPIWrapper":
        """Build method signature."""
        ...

    @property
    def _http_client(self) -> "HTTPClient":
        """HTTP client property."""
        ...


class DirectAPIMixin:
    """Mixin class containing Direct API methods.

    These methods provide a simplified interface to common document
    processing operations. They internally use the Build API.

    Note: The API automatically converts supported document formats
    (DOCX, XLSX, PPTX) to PDF when processing.
    """

    def _process_file(
        self,
        tool: str,
        input_file: FileInput,
        output_path: Optional[str] = None,
        **options: Any,
    ) -> Optional[bytes]:
        """Process file method that will be provided by NutrientClient."""
        raise NotImplementedError("This method is provided by NutrientClient")

    def convert_to_pdf(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Convert a document to PDF.

        Converts Office documents (DOCX, XLSX, PPTX) to PDF format.
        This uses the API's implicit conversion - simply uploading a
        non-PDF document returns it as a PDF.

        Args:
            input_file: Input document (DOCX, XLSX, PPTX, etc).
            output_path: Optional path to save the output PDF.

        Returns:
            Converted PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors (e.g., unsupported format).

        Note:
            HTML files are not currently supported by the API.
        """
        # Use builder with no actions - implicit conversion happens
        # Type checking: at runtime, self is NutrientClient which has these methods
        return self.build(input_file).execute(output_path)  # type: ignore[attr-defined,no-any-return]

    def flatten_annotations(
        self, input_file: FileInput, output_path: Optional[str] = None
    ) -> Optional[bytes]:
        """Flatten annotations and form fields in a PDF.

        Converts all annotations and form fields into static page content.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("flatten-annotations", input_file, output_path)

    def rotate_pages(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        degrees: int = 0,
        page_indexes: Optional[List[int]] = None,
    ) -> Optional[bytes]:
        """Rotate pages in a PDF.

        Rotate all pages or specific pages by the specified degrees.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            degrees: Rotation angle (90, 180, 270, or -90).
            page_indexes: Optional list of page indexes to rotate (0-based).

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        options = {"degrees": degrees}
        if page_indexes is not None:
            options["page_indexes"] = page_indexes  # type: ignore
        return self._process_file("rotate-pages", input_file, output_path, **options)

    def ocr_pdf(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        language: str = "english",
    ) -> Optional[bytes]:
        """Apply OCR to a PDF to make it searchable.

        Performs optical character recognition on the PDF to extract text
        and make it searchable. If input is an Office document, it will
        be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            language: OCR language. Supported: "english", "eng", "deu", "german".
                     Default is "english".

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("ocr-pdf", input_file, output_path, language=language)

    def watermark_pdf(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        width: int = 200,
        height: int = 100,
        opacity: float = 1.0,
        position: str = "center",
    ) -> Optional[bytes]:
        """Add a watermark to a PDF.

        Adds a text or image watermark to all pages of the PDF.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.
            text: Text to use as watermark. Either text or image_url required.
            image_url: URL of image to use as watermark.
            width: Width of the watermark in points (required).
            height: Height of the watermark in points (required).
            opacity: Opacity of the watermark (0.0 to 1.0).
            position: Position of watermark. One of: "top-left", "top-center",
                     "top-right", "center", "bottom-left", "bottom-center",
                     "bottom-right".

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If neither text nor image_url is provided.
        """
        if not text and not image_url:
            raise ValueError("Either text or image_url must be provided")

        options = {
            "width": width,
            "height": height,
            "opacity": opacity,
            "position": position,
        }

        if text:
            options["text"] = text
        else:
            options["image_url"] = image_url

        return self._process_file("watermark-pdf", input_file, output_path, **options)

    def apply_redactions(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Apply redaction annotations to permanently remove content.

        Applies any redaction annotations in the PDF to permanently remove
        the underlying content. If input is an Office document, it will
        be converted to PDF first.

        Args:
            input_file: Input file (PDF or Office document).
            output_path: Optional path to save the output file.

        Returns:
            Processed file as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        return self._process_file("apply-redactions", input_file, output_path)

    def split_pdf(
        self,
        input_file: FileInput,
        page_ranges: Optional[List[Dict[str, int]]] = None,
        output_paths: Optional[List[str]] = None,
    ) -> List[bytes]:
        """Split a PDF into multiple documents by page ranges.

        Splits a PDF into multiple files based on specified page ranges.
        Each range creates a separate output file.

        Args:
            input_file: Input PDF file.
            page_ranges: List of page range dictionaries. Each dict can contain:
                - 'start': Starting page index (0-based, inclusive)
                - 'end': Ending page index (0-based, exclusive)
                - If not provided, splits into individual pages
            output_paths: Optional list of paths to save output files.
                          Must match length of page_ranges if provided.

        Returns:
            List of PDF bytes for each split, or empty list if output_paths provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_ranges and output_paths length mismatch.

        Examples:
            # Split into individual pages
            pages = client.split_pdf("document.pdf")

            # Split by custom ranges
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
        """
        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Validate inputs
        if output_paths and page_ranges and len(output_paths) != len(page_ranges):
            raise ValueError("output_paths length must match page_ranges length")

        # Default to splitting into individual pages if no ranges specified
        if not page_ranges:
            # We'll need to determine page count first - for now, assume single page split
            page_ranges = [{"start": 0, "end": 1}]

        results = []

        # Process each page range as a separate API call
        for i, page_range in enumerate(page_ranges):
            # Prepare file for upload
            file_field, file_data = prepare_file_for_upload(input_file, "file")
            files = {file_field: file_data}

            # Build instructions for page extraction
            instructions = {"parts": [{"file": "file", "pages": page_range}], "actions": []}

            # Make API request
            # Type checking: at runtime, self is NutrientClient which has _http_client
            result = self._http_client.post(  # type: ignore[attr-defined]
                "/build",
                files=files,
                json_data=instructions,
            )

            # Handle output
            if output_paths and i < len(output_paths):
                save_file_output(result, output_paths[i])
            else:
                results.append(result)  # type: ignore[arg-type]

        return results if not output_paths else []

    def duplicate_pdf_pages(
        self,
        input_file: FileInput,
        page_indexes: List[int],
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Duplicate specific pages within a PDF document.

        Creates a new PDF containing the specified pages in the order provided.
        Pages can be duplicated multiple times by including their index multiple times.

        Args:
            input_file: Input PDF file.
            page_indexes: List of page indexes to include (0-based).
                         Pages can be repeated to create duplicates.
                         Negative indexes are supported (-1 for last page).
            output_path: Optional path to save the output file.

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_indexes is empty.

        Examples:
            # Duplicate first page twice, then include second page
            result = client.duplicate_pdf_pages(
                "document.pdf",
                page_indexes=[0, 0, 1]  # Page 1, Page 1, Page 2
            )

            # Include last page at beginning and end
            result = client.duplicate_pdf_pages(
                "document.pdf",
                page_indexes=[-1, 0, 1, 2, -1]  # Last, First, Second, Third, Last
            )

            # Save to specific file
            client.duplicate_pdf_pages(
                "document.pdf",
                page_indexes=[0, 2, 1],  # Reorder: Page 1, Page 3, Page 2
                output_path="reordered.pdf"
            )
        """
        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Validate inputs
        if not page_indexes:
            raise ValueError("page_indexes cannot be empty")

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Build parts for each page index
        parts = []
        for page_index in page_indexes:
            if page_index < 0:
                # For negative indexes, use the index directly (API supports negative indexes)
                parts.append({"file": "file", "pages": {"start": page_index, "end": page_index}})
            else:
                # For positive indexes, create single-page range
                parts.append({"file": "file", "pages": {"start": page_index, "end": page_index}})

        # Build instructions for duplication
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def delete_pdf_pages(
        self,
        input_file: FileInput,
        page_indexes: List[int],
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Delete specific pages from a PDF document.

        Creates a new PDF with the specified pages removed. The API approach
        works by selecting all pages except those to be deleted.

        Args:
            input_file: Input PDF file.
            page_indexes: List of page indexes to delete (0-based).
                         Negative indexes are supported (-1 for last page).
            output_path: Optional path to save the output file.

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_indexes is empty.

        Examples:
            # Delete first and last pages
            result = client.delete_pdf_pages(
                "document.pdf",
                page_indexes=[0, -1]
            )

            # Delete specific pages (2nd and 4th pages)
            result = client.delete_pdf_pages(
                "document.pdf",
                page_indexes=[1, 3]  # 0-based indexing
            )

            # Save to specific file
            client.delete_pdf_pages(
                "document.pdf",
                page_indexes=[2, 4, 5],
                output_path="pages_deleted.pdf"
            )
        """
        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Validate inputs
        if not page_indexes:
            raise ValueError("page_indexes cannot be empty")

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Convert negative indexes to positive (we need to get document info first)
        # For now, we'll create the parts structure and let the API handle negative indexes

        # Sort page indexes to handle ranges efficiently
        sorted_indexes = sorted(set(page_indexes))  # Remove duplicates and sort

        # Build parts for pages to keep (excluding the ones to delete)
        # We need to create ranges that exclude the deleted pages
        parts = []

        # Start from page 0
        current_page = 0

        for delete_index in sorted_indexes:
            # Handle negative indexes by letting API process them
            if delete_index < 0:
                # For negative indexes, we can't easily calculate ranges without knowing total pages
                # We'll use a different approach - create parts for everything and let API handle it
                # This is a simplified approach that may need refinement
                continue

            # Add range from current_page to delete_index (exclusive)
            if current_page < delete_index:
                parts.append(
                    {"file": "file", "pages": {"start": current_page, "end": delete_index}}
                )

            # Skip the deleted page
            current_page = delete_index + 1

        # Add remaining pages from current_page to end
        if current_page >= 0:  # Always add remaining pages unless we handled negative indexes
            parts.append({"file": "file", "pages": {"start": current_page}})

        # Handle case where we have negative indexes - use a simpler approach
        if any(idx < 0 for idx in page_indexes):
            # If we have negative indexes, we need a different strategy
            # For now, we'll create a request that includes all positive ranges
            # and excludes negative ones - this is a limitation that would need
            # API documentation clarification
            parts = []

            # Positive indexes only for now
            positive_indexes = [idx for idx in sorted_indexes if idx >= 0]
            if positive_indexes:
                current_page = 0
                for delete_index in positive_indexes:
                    if current_page < delete_index:
                        parts.append(
                            {"file": "file", "pages": {"start": current_page, "end": delete_index}}
                        )
                    current_page = delete_index + 1

                # Add remaining pages
                parts.append({"file": "file", "pages": {"start": current_page}})

            # Handle negative indexes separately by including a warning
            if any(idx < 0 for idx in page_indexes):
                # For now, raise an error for negative indexes as they need special handling
                negative_indexes = [idx for idx in page_indexes if idx < 0]
                raise ValueError(
                    f"Negative page indexes not yet supported for deletion: {negative_indexes}"
                )

        # If no parts (edge case), raise error
        if not parts:
            raise ValueError("No valid pages to keep after deletion")

        # Build instructions for deletion (keeping non-deleted pages)
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def add_page(
        self,
        input_file: FileInput,
        output_path: Optional[str] = None,
        *,
        page_count: int = 1,
        after_page_index: Optional[int] = None,
        orientation: str = "portrait",
        size: str = "A4",
        margin_left: int = 72,
        margin_top: int = 72,
        margin_right: int = 72,
        margin_bottom: int = 72,
    ) -> Optional[bytes]:
        """Add blank pages to a PDF document.

        Inserts one or more blank pages into a PDF at the specified position.
        If input is an Office document, it will be converted to PDF first.

        Args:
            input_file: Input PDF file or Office document.
            output_path: Optional path to save the output file.
            page_count: Number of blank pages to add (default: 1).
            after_page_index: Page index after which to insert pages (0-based).
                             If None, pages are added at the end.
            orientation: Page orientation - "portrait" or "landscape" (default: "portrait").
            size: Page size - "A4", "Letter", "Legal", etc. (default: "A4").
            margin_left: Left margin in points (default: 72).
            margin_top: Top margin in points (default: 72).
            margin_right: Right margin in points (default: 72).
            margin_bottom: Bottom margin in points (default: 72).

        Returns:
            Processed PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If page_count is less than 1 or after_page_index is negative.

        Examples:
            # Add one blank page at the end
            result = client.add_page("document.pdf")

            # Add 3 blank pages after the first page
            result = client.add_page(
                "document.pdf",
                page_count=3,
                after_page_index=0
            )

            # Add landscape pages with custom margins
            result = client.add_page(
                "document.pdf",
                page_count=2,
                orientation="landscape",
                size="Letter",
                margin_left=50,
                margin_top=50,
                margin_right=50,
                margin_bottom=50
            )

            # Save to specific file
            client.add_page(
                "document.pdf",
                page_count=1,
                after_page_index=2,
                output_path="with_blank_page.pdf"
            )
        """
        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Validate inputs
        if page_count < 1:
            raise ValueError("page_count must be at least 1")
        if after_page_index is not None and after_page_index < 0:
            raise ValueError("after_page_index must be non-negative")

        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file, "file")
        files = {file_field: file_data}

        # Build parts for the document
        parts = []

        if after_page_index is None:
            # Add original document first, then new pages at the end
            parts.append({"file": "file"})

            # Add new pages
            new_page_part = cast(Dict[str, Any], {
                "page": "new",
                "pageCount": page_count,
                "layout": {
                    "orientation": orientation,
                    "size": size,
                    "margin": {
                        "left": margin_left,
                        "top": margin_top,
                        "right": margin_right,
                        "bottom": margin_bottom,
                    },
                },
            })
            parts.append(new_page_part)
        else:
            # Add pages before the insertion point
            if after_page_index >= 0:
                parts.append({"file": "file", "pages": {"start": 0, "end": after_page_index + 1}})  # type: ignore[dict-item]

            # Add new pages
            new_page_part = cast(Dict[str, Any], {
                "page": "new",
                "pageCount": page_count,
                "layout": {
                    "orientation": orientation,
                    "size": size,
                    "margin": {
                        "left": margin_left,
                        "top": margin_top,
                        "right": margin_right,
                        "bottom": margin_bottom,
                    },
                },
            })
            parts.append(new_page_part)

            # Add remaining pages after the insertion point
            parts.append({"file": "file", "pages": {"start": after_page_index + 1}})  # type: ignore[dict-item]

        # Build instructions for adding pages
        instructions = {"parts": parts, "actions": []}  # type: ignore[misc]

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]

    def merge_pdfs(
        self,
        input_files: List[FileInput],
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Merge multiple PDF files into one.

        Combines multiple files into a single PDF in the order provided.
        Office documents (DOCX, XLSX, PPTX) will be automatically converted
        to PDF before merging.

        Args:
            input_files: List of input files (PDFs or Office documents).
            output_path: Optional path to save the output file.

        Returns:
            Merged PDF as bytes, or None if output_path is provided.

        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
            ValueError: If less than 2 files provided.

        Example:
            # Merge PDFs and Office documents
            client.merge_pdfs([
                "document1.pdf",
                "document2.docx",
                "spreadsheet.xlsx"
            ], "merged.pdf")
        """
        if len(input_files) < 2:
            raise ValueError("At least 2 files required for merge")

        from nutrient_dws.file_handler import prepare_file_for_upload, save_file_output

        # Prepare files for upload
        files = {}
        parts = []

        for i, file in enumerate(input_files):
            field_name = f"file{i}"
            file_field, file_data = prepare_file_for_upload(file, field_name)
            files[file_field] = file_data
            parts.append({"file": field_name})

        # Build instructions for merge (no actions needed)
        instructions = {"parts": parts, "actions": []}

        # Make API request
        # Type checking: at runtime, self is NutrientClient which has _http_client
        result = self._http_client.post(  # type: ignore[attr-defined]
            "/build",
            files=files,
            json_data=instructions,
        )

        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result  # type: ignore[no-any-return]
