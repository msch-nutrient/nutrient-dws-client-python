#!/usr/bin/env python3
"""Generate Direct API methods from OpenAPI specification."""

import re
from pathlib import Path
from typing import Any


def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    # Handle common patterns
    name = name.replace("-", "_")
    # Insert underscore before uppercase letters
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return name


def get_python_type(schema: dict[str, Any]) -> str:
    """Convert OpenAPI schema type to Python type hint."""
    if not schema:
        return "Any"

    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List[Any]",
        "object": "Dict[str, Any]",
    }

    schema_type = schema.get("type", "string")
    return type_mapping.get(schema_type, "Any")


def create_manual_tools() -> list[dict[str, Any]]:
    """Create tool definitions based on the specification documentation.

    Since the Nutrient API uses a build endpoint with actions rather than
    individual tool endpoints, we'll create convenience methods that wrap
    the build API.
    """
    tools = [
        {
            "tool_name": "convert-to-pdf",
            "method_name": "convert_to_pdf",
            "summary": "Convert a document to PDF",
            "description": "Convert various document formats (DOCX, XLSX, PPTX, etc.) to PDF.",
            "parameters": {},
        },
        {
            "tool_name": "convert-to-pdfa",
            "method_name": "convert_to_pdfa",
            "summary": "Convert a document to PDF/A",
            "description": "Convert documents to PDF/A format for long-term archiving.",
            "parameters": {
                "conformance_level": {
                    "type": "str",
                    "required": False,
                    "description": "PDF/A conformance level (e.g., '2b', '3b')",
                    "default": "2b",
                },
            },
        },
        {
            "tool_name": "ocr-pdf",
            "method_name": "ocr_pdf",
            "summary": "Perform OCR on a PDF",
            "description": "Apply optical character recognition to make scanned PDFs searchable.",
            "parameters": {
                "language": {
                    "type": "str",
                    "required": False,
                    "description": "OCR language code (e.g., 'en', 'de', 'fr')",
                    "default": "en",
                },
            },
        },
        {
            "tool_name": "rotate-pages",
            "method_name": "rotate_pages",
            "summary": "Rotate PDF pages",
            "description": "Rotate pages in a PDF document.",
            "parameters": {
                "degrees": {
                    "type": "int",
                    "required": True,
                    "description": "Rotation angle in degrees (90, 180, 270)",
                },
                "page_indexes": {
                    "type": "List[int]",
                    "required": False,
                    "description": (
                        "List of page indexes to rotate (0-based). "
                        "If not specified, all pages are rotated."
                    ),
                },
            },
        },
        {
            "tool_name": "flatten-annotations",
            "method_name": "flatten_annotations",
            "summary": "Flatten PDF annotations",
            "description": "Flatten annotations and form fields in a PDF.",
            "parameters": {},
        },
        {
            "tool_name": "watermark-pdf",
            "method_name": "watermark_pdf",
            "summary": "Add watermark to PDF",
            "description": "Add text or image watermark to PDF pages.",
            "parameters": {
                "text": {
                    "type": "str",
                    "required": False,
                    "description": "Watermark text",
                },
                "image_url": {
                    "type": "str",
                    "required": False,
                    "description": "URL of watermark image",
                },
                "opacity": {
                    "type": "float",
                    "required": False,
                    "description": "Watermark opacity (0.0 to 1.0)",
                    "default": 0.5,
                },
                "position": {
                    "type": "str",
                    "required": False,
                    "description": "Watermark position",
                    "default": "center",
                },
            },
        },
        {
            "tool_name": "sign-pdf",
            "method_name": "sign_pdf",
            "summary": "Digitally sign a PDF",
            "description": "Add a digital signature to a PDF document.",
            "parameters": {
                "certificate_file": {
                    "type": "FileInput",
                    "required": True,
                    "description": "Digital certificate file (P12/PFX format)",
                },
                "certificate_password": {
                    "type": "str",
                    "required": True,
                    "description": "Certificate password",
                },
                "reason": {
                    "type": "str",
                    "required": False,
                    "description": "Reason for signing",
                },
                "location": {
                    "type": "str",
                    "required": False,
                    "description": "Location of signing",
                },
            },
        },
        {
            "tool_name": "redact-pdf",
            "method_name": "redact_pdf",
            "summary": "Redact sensitive information from PDF",
            "description": "Use AI to automatically redact sensitive information from a PDF.",
            "parameters": {
                "types": {
                    "type": "List[str]",
                    "required": False,
                    "description": "Types of information to redact (e.g., 'email', 'phone', 'ssn')",
                },
            },
        },
        {
            "tool_name": "export-pdf-to-office",
            "method_name": "export_pdf_to_office",
            "summary": "Export PDF to Office format",
            "description": "Convert PDF to Microsoft Office formats (DOCX, XLSX, PPTX).",
            "parameters": {
                "format": {
                    "type": "str",
                    "required": True,
                    "description": "Output format ('docx', 'xlsx', 'pptx')",
                },
            },
        },
        {
            "tool_name": "export-pdf-to-images",
            "method_name": "export_pdf_to_images",
            "summary": "Export PDF pages as images",
            "description": "Convert PDF pages to image files.",
            "parameters": {
                "format": {
                    "type": "str",
                    "required": False,
                    "description": "Image format ('png', 'jpeg', 'webp')",
                    "default": "png",
                },
                "dpi": {
                    "type": "int",
                    "required": False,
                    "description": "Image resolution in DPI",
                    "default": 150,
                },
                "page_indexes": {
                    "type": "List[int]",
                    "required": False,
                    "description": "List of page indexes to export (0-based)",
                },
            },
        },
    ]

    return tools


def generate_method_code(tool_info: dict[str, Any]) -> str:
    """Generate Python method code for a tool."""
    method_name = tool_info["method_name"]
    tool_name = tool_info["tool_name"]
    summary = tool_info["summary"]
    description = tool_info["description"]
    parameters = tool_info["parameters"]

    # Build parameter list
    param_list = ["self", "input_file: FileInput"]
    param_docs = []

    # Add required parameters first
    for param_name, param_info in parameters.items():
        if param_info["required"]:
            param_type = param_info["type"]
            # Handle imports for complex types
            if param_type == "FileInput":
                param_type = "'FileInput'"  # Forward reference
            param_list.append(f"{param_name}: {param_type}")
            param_docs.append(f"        {param_name}: {param_info['description']}")

    # Always add output_path
    param_list.append("output_path: Optional[str] = None")

    # Add optional parameters
    for param_name, param_info in parameters.items():
        if not param_info["required"]:
            param_type = param_info["type"]
            # Handle List types
            base_type = param_type

            default = param_info.get("default")
            if default is None:
                param_list.append(f"{param_name}: Optional[{base_type}] = None")
            else:
                if isinstance(default, str):
                    param_list.append(f'{param_name}: {base_type} = "{default}"')
                else:
                    param_list.append(f"{param_name}: {base_type} = {default}")
            param_docs.append(f"        {param_name}: {param_info['description']}")

    # Build method signature
    if len(param_list) > 3:  # Multiple parameters
        params_str = ",\n        ".join(param_list)
        method_signature = (
            f"    def {method_name}(\n        {params_str},\n    ) -> Optional[bytes]:"
        )
    else:
        params_str = ", ".join(param_list)
        method_signature = f"    def {method_name}({params_str}) -> Optional[bytes]:"

    # Build docstring
    docstring_lines = [f'        """{summary}']
    if description and description != summary:
        docstring_lines.append("")
        docstring_lines.append(f"        {description}")

    docstring_lines.extend(
        [
            "",
            "        Args:",
            "            input_file: Input file (path, bytes, or file-like object).",
        ]
    )

    if param_docs:
        docstring_lines.extend(param_docs)

    docstring_lines.extend(
        [
            "            output_path: Optional path to save the output file.",
            "",
            "        Returns:",
            "            Processed file as bytes, or None if output_path is provided.",
            "",
            "        Raises:",
            "            AuthenticationError: If API key is missing or invalid.",
            "            APIError: For other API errors.",
            '        """',
        ]
    )

    # Build method body
    method_body = []

    # Collect kwargs
    kwargs_params = [f"{name}={name}" for name in parameters]

    if kwargs_params:
        kwargs_str = ", ".join(kwargs_params)
        method_body.append(
            f'        return self._process_file("{tool_name}", input_file, '
            f"output_path, {kwargs_str})"
        )
    else:
        method_body.append(
            f'        return self._process_file("{tool_name}", input_file, output_path)'
        )

    # Combine all parts
    return "\n".join(
        [
            method_signature,
            "\n".join(docstring_lines),
            "\n".join(method_body),
        ]
    )


def generate_api_methods(spec_path: Path, output_path: Path) -> None:
    """Generate API methods from OpenAPI specification."""
    # For Nutrient API, we'll use manually defined tools since they use
    # a build endpoint with actions rather than individual endpoints
    tools = create_manual_tools()

    # Sort tools by method name
    tools.sort(key=lambda t: t["method_name"])

    # Generate code
    code_lines = [
        '"""Direct API methods for individual document processing tools.',
        "",
        "This file provides convenient methods that wrap the Nutrient Build API",
        "for common document processing operations.",
        '"""',
        "",
        "from typing import List, Optional",
        "",
        "from nutrient_dws.file_handler import FileInput",
        "",
        "",
        "class DirectAPIMixin:",
        '    """Mixin class containing Direct API methods.',
        "    ",
        "    These methods provide a simplified interface to common document",
        "    processing operations. They internally use the Build API.",
        '    """',
        "",
    ]

    # Add methods
    for tool in tools:
        code_lines.append(generate_method_code(tool))
        code_lines.append("")  # Empty line between methods

    # Write to file
    output_path.write_text("\n".join(code_lines))
    print(f"Generated {len(tools)} API methods in {output_path}")


if __name__ == "__main__":
    spec_path = Path("openapi_spec.yml")
    output_path = Path("src/nutrient/api/direct.py")

    generate_api_methods(spec_path, output_path)
