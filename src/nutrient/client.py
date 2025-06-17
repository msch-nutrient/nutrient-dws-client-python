"""Main client module for Nutrient DWS API."""

from typing import Optional

from nutrient.builder import BuildAPIWrapper
from nutrient.exceptions import AuthenticationError


class NutrientClient:
    """Main client for interacting with Nutrient DWS API.

    Args:
        api_key: API key for authentication. If not provided, will look for
            NUTRIENT_API_KEY environment variable.
        timeout: Request timeout in seconds. Defaults to 300.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 300) -> None:
        """Initialize the Nutrient client."""
        self._api_key = api_key
        self._timeout = timeout

    def build(self, input_file) -> BuildAPIWrapper:
        """Start a Builder API workflow.

        Args:
            input_file: Input file (path, bytes, or file-like object).

        Returns:
            BuildAPIWrapper instance for chaining operations.
        """
        raise NotImplementedError("Builder API not yet implemented")