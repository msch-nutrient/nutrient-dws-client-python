# Nutrient DWS Python Client

A Python client library for the Nutrient Document Web Services (DWS) API.

## Installation

```bash
pip install nutrient
```

## Quick Start

```python
from nutrient import NutrientClient

# Initialize the client
client = NutrientClient(api_key="YOUR_API_KEY")

# Convert a document to PDF
pdf_bytes = client.convert_to_pdf(input_file="document.docx")

# Use the Builder API for complex workflows
client.build(input_file="document.docx") \
    .add_step(tool="convert-to-pdf") \
    .add_step(tool="rotate-pages", options={"degrees": 90}) \
    .execute(output_path="output.pdf")
```

## Documentation

Full documentation is available at [https://nutrient-dws-client-python.readthedocs.io](https://nutrient-dws-client-python.readthedocs.io)

## License

MIT License - see LICENSE file for details.