"""HTTP client abstraction for API communication."""

import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with connection pooling and retry logic."""

    def __init__(self, api_key: str, timeout: int = 300) -> None:
        """Initialize HTTP client with authentication."""
        self._api_key = api_key
        self._timeout = timeout
        self._session = self._create_session()
        self._base_url = "https://www.nutrient.io/api/processor-api"

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({
            "X-Api-Key": self._api_key,
            "User-Agent": "nutrient-python-client/0.1.0",
        })

        return session

    def post(
        self,
        endpoint: str,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Make POST request to API.

        Args:
            endpoint: API endpoint path.
            files: Files to upload.
            data: Form data.

        Returns:
            Response object.
        """
        url = f"{self._base_url}{endpoint}"
        logger.debug(f"POST {url}")

        response = self._session.post(
            url,
            files=files,
            data=data,
            timeout=self._timeout,
        )

        logger.debug(f"Response: {response.status_code}")
        return response

    def close(self) -> None:
        """Close the session."""
        self._session.close()