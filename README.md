# GraphViz SVG Generator API

A Flask REST API that generates SVG diagrams from GraphViz DOT files.

## Features

- Generate SVG from uploaded DOT files
- Generate SVG from existing DOT files in the project folder
- List available DOT files
- Download generated SVG files
- RESTful API with JSON responses

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure GraphViz is installed on your system:
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
# Download and install from: https://graphviz.org/download/
```

## Usage

### Start the API server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### GET /
Get API documentation and available endpoints.

```bash
curl http://localhost:5000/
```

#### GET /health
Health check endpoint.

```bash
curl http://localhost:5000/health
```

#### GET /list_dot_files
List all DOT files in the current directory.

```bash
curl http://localhost:5000/list_dot_files
```

#### POST /generate_from_existing
Generate SVG from an existing DOT file in the folder.

```bash
curl -X POST http://localhost:5000/generate_from_existing \
  -H "Content-Type: application/json" \
  -d '{"filename": "voltage_accuracy_test_setup.dot"}'
```

#### POST /generate
Generate SVG from an uploaded DOT file.

```bash
curl -X POST http://localhost:5000/generate \
  -F "file=@your_file.dot"
```

#### GET /download/<filename>
Download a generated SVG file.

```bash
curl http://localhost:5000/download/output_file.svg -o diagram.svg
```

## Testing

Run the test script to verify the API is working:

```bash
python test_api.py
```

This will:
1. Check API health
2. List available DOT files
3. Generate SVG from the existing `voltage_accuracy_test_setup.dot` file
4. Save the result as `test_output.svg`

## Example Usage with Python

```python
import requests
import json

# Generate SVG from existing file
payload = {"filename": "voltage_accuracy_test_setup.dot"}
response = requests.post(
    "http://localhost:5000/generate_from_existing",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

if response.status_code == 200:
    data = response.json()
    svg_content = data['svg_content']
    
    # Save SVG to file
    with open('diagram.svg', 'w') as f:
        f.write(svg_content)
    print("SVG generated successfully!")
```

## Example Usage with curl

```bash
# Generate SVG from existing DOT file
curl -X POST http://localhost:5000/generate_from_existing \
  -H "Content-Type: application/json" \
  -d '{"filename": "voltage_accuracy_test_setup.dot"}' \
  | jq '.svg_content' > diagram.svg

# Upload and generate SVG
curl -X POST http://localhost:5000/generate \
  -F "file=@mydiagram.dot" \
  | jq '.svg_content' > output.svg
```

## Response Format

All endpoints return JSON responses:

```json
{
  "message": "SVG generated successfully",
  "source_file": "voltage_accuracy_test_setup.dot",
  "svg_content": "<svg>...</svg>",
  "output_file": "voltage_accuracy_test_setup_12345.svg"
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400: Bad Request (missing file, invalid format)
- 404: File Not Found
- 500: Internal Server Error

## File Structure

```
graphwiz-test/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── test_api.py                    # API test script
├── README.md                      # This file
├── voltage_accuracy_test_setup.dot # Sample DOT file
├── uploads/                       # Temporary upload directory
└── outputs/                       # Generated SVG files
```
