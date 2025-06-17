"""Main client module for Nutrient DWS API."""

import os
from typing import Any, Optional

from nutrient.api.direct import DirectAPIMixin
from nutrient.builder import BuildAPIWrapper
from nutrient.exceptions import AuthenticationError
from nutrient.file_handler import FileInput, prepare_file_for_upload, save_file_output
from nutrient.http_client import HTTPClient


class NutrientClient(DirectAPIMixin):
    """Main client for interacting with Nutrient DWS API.
    
    This client provides two ways to interact with the API:
    
    1. Direct API: Individual method calls for single operations
       Example: client.convert_to_pdf(input_file="document.docx")
    
    2. Builder API: Fluent interface for chaining multiple operations
       Example: client.build(input_file="doc.docx").add_step("convert-to-pdf").execute()

    Args:
        api_key: API key for authentication. If not provided, will look for
            NUTRIENT_API_KEY environment variable.
        timeout: Request timeout in seconds. Defaults to 300.
            
    Raises:
        AuthenticationError: When making API calls without a valid API key.
        
    Example:
        >>> from nutrient import NutrientClient
        >>> client = NutrientClient(api_key="your-api-key")
        >>> # Direct API
        >>> pdf = client.convert_to_pdf(input_file="document.docx")
        >>> # Builder API
        >>> client.build(input_file="document.docx") \\
        ...       .add_step(tool="convert-to-pdf") \\
        ...       .add_step(tool="ocr-pdf") \\
        ...       .execute(output_path="output.pdf")
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 300) -> None:
        """Initialize the Nutrient client."""
        # Get API key from parameter or environment
        self._api_key = api_key or os.environ.get("NUTRIENT_API_KEY")
        self._timeout = timeout
        
        # Initialize HTTP client
        self._http_client = HTTPClient(api_key=self._api_key, timeout=timeout)
        
        # Direct API methods will be added dynamically

    def build(self, input_file: FileInput) -> BuildAPIWrapper:
        """Start a Builder API workflow.

        Args:
            input_file: Input file (path, bytes, or file-like object).

        Returns:
            BuildAPIWrapper instance for chaining operations.
            
        Example:
            >>> builder = client.build(input_file="document.pdf")
            >>> builder.add_step(tool="rotate-pages", options={"degrees": 90})
            >>> result = builder.execute()
        """
        return BuildAPIWrapper(client=self, input_file=input_file)
    
    def _process_file(
        self,
        tool: str,
        input_file: FileInput,
        output_path: Optional[str] = None,
        **options: Any,
    ) -> Optional[bytes]:
        """Process a file using the Direct API.
        
        This is the internal method used by all Direct API methods.
        
        Args:
            tool: The tool identifier from the API.
            input_file: Input file to process.
            output_path: Optional path to save the output.
            **options: Tool-specific options.
            
        Returns:
            Processed file as bytes, or None if output_path is provided.
            
        Raises:
            AuthenticationError: If API key is missing or invalid.
            APIError: For other API errors.
        """
        # Prepare file for upload
        file_field, file_data = prepare_file_for_upload(input_file)
        files = {file_field: file_data}
        
        # Prepare form data with options
        data = {k: str(v) for k, v in options.items() if v is not None}
        
        # Make API request
        endpoint = f"/process/{tool}"
        result = self._http_client.post(endpoint, files=files, data=data)
        
        # Handle output
        if output_path:
            save_file_output(result, output_path)
            return None
        else:
            return result
    
    def close(self) -> None:
        """Close the HTTP client session."""
        self._http_client.close()
    
    def __enter__(self) -> "NutrientClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()