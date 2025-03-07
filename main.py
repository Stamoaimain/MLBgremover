from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from carvekit.api.high import HiInterface
import os
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize the interface at module level with all parameters explicitly set
logger.info("Initializing CarveKit interface...")
interface = HiInterface(
    object_type="object",
    device='cpu',
    seg_mask_size=640,  # Add default segmentation mask size
 # No preprocessing
)
logger.info("CarveKit interface initialized successfully")

app = FastAPI(title="Background Removal API")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ImageRequest(BaseModel):
    image: str  # base64 encoded image

class ImageResponse(BaseModel):
    image: str  # base64 encoded image

def is_valid_base64(s):
    try:
        # Check if string is valid base64
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False

@app.post("/remove-background", response_model=ImageResponse)
async def remove_background(request: ImageRequest):
    print("Received request")
    try:
        # Validate base64 string
        if not request.image:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove potential base64 header
        if "base64," in request.image:
            request.image = request.image.split("base64,")[1]
            
        if not is_valid_base64(request.image):
            raise HTTPException(status_code=400, detail="Invalid base64 string")

        try:
            # Decode base64 image
            image_data = base64.b64decode(request.image)
            input_image = Image.open(BytesIO(image_data))
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="Invalid image format")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error decoding image: {str(e)}")
        
        # Remove background using carvekit
        output_image = interface([input_image])[0]
        
        # Convert back to base64
        buffered = BytesIO()
        output_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return ImageResponse(image=img_str)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=75,
        workers=1
    ) 