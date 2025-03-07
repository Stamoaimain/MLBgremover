from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
import logging
import sys
import multiprocessing
from PIL import Image, UnidentifiedImageError, ImageFile
from rembg import remove  # Faster than CarveKit!
import os

# Allow PIL to process truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True  

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Get optimal CPU threads for parallel processing
cpu_count = multiprocessing.cpu_count()
optimal_threads = max(1, min(cpu_count - 1, 6))  # Use N-1 cores but cap at 6
logger.info(f"Using {optimal_threads} CPU threads for processing")

# Initialize FastAPI app
app = FastAPI(title="Ultra-Fast Background Removal API")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "threads": optimal_threads}

class ImageRequest(BaseModel):
    image: str  # base64 encoded image

class ImageResponse(BaseModel):
    image: str  # base64 encoded image

def is_valid_base64(s: str) -> bool:
    """Efficiently validate base64 string"""
    try:
        return len(s) % 4 == 0 and all(c in b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in s.encode())
    except Exception:
        return False

@app.post("/remove-background", response_model=ImageResponse)
async def remove_background(request: ImageRequest):
    logger.info("Processing background removal request")

    try:
        # Validate input image
        if not request.image:
            raise HTTPException(status_code=400, detail="No image data provided")

        # Remove base64 prefix if present
        if "base64," in request.image:
            request.image = request.image.split("base64,")[1]

        if not is_valid_base64(request.image):
            raise HTTPException(status_code=400, detail="Invalid base64 string")

        try:
            # Decode base64 image
            image_data = base64.b64decode(request.image)
            input_image = Image.open(BytesIO(image_data))

            # Resize large images to speed up processing
            max_dimension = 1500
            if max(input_image.size) > max_dimension:
                ratio = max_dimension / max(input_image.size)
                new_size = (int(input_image.size[0] * ratio), int(input_image.size[1] * ratio))
                input_image = input_image.resize(new_size, Image.LANCZOS)
                logger.info(f"Resized image to {new_size}")

        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="Invalid image format")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error decoding image: {str(e)}")

        # Remove background using rembg (Faster than CarveKit)
        output_image = remove(input_image)

        # Convert back to base64
        buffered = BytesIO()
        output_image.save(buffered, format="PNG", optimize=True)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        logger.info("Background removal completed successfully")
        return ImageResponse(image=img_str)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))

    logger.info(f"Starting server on port {port} with {optimal_threads} threads")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=75,
        workers=1  # Use single worker for stability
    )
