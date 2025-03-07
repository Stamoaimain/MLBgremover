# Background Removal API

This is a FastAPI-based application that removes backgrounds from images using the U2Net model in ONNX format. The API accepts base64 encoded images and returns the processed images with backgrounds removed, also in base64 format.

## Features

- Background removal using U2Net model
- Base64 image input/output
- High-quality image processing
- Automatic model download
- FastAPI-based REST API

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Usage

### Remove Background Endpoint

**POST** `/remove-background`

Request body:

```json
{
  "image": "base64_encoded_image_string"
}
```

Response:

```json
{
  "image": "base64_encoded_result_image_string"
}
```

### Example Usage (Python)

```python
import requests
import base64

# Read and encode image
with open("input_image.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()

# Make API request
response = requests.post(
    "http://localhost:8000/remove-background",
    json={"image": encoded_string}
)

# Save result
if response.status_code == 200:
    result = response.json()
    img_data = base64.b64decode(result["image"])
    with open("output_image.png", "wb") as f:
        f.write(img_data)
```

## Notes

- The U2Net model will be automatically downloaded on first run
- Supported input image formats: JPG, PNG
- Output images are saved in PNG format with transparency
- The API processes one image at a time
- For best results, use images with clear subjects and contrasting backgrounds
