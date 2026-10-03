"""
ComicCraft - AI Comic Story Creator using Gemini Models
Team ID: 6ab22cb7

Main FastAPI Application Entry Point.
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("comiccraft")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: prepare directories on startup."""
    # Ensure static directories exist
    os.makedirs("static/panels", exist_ok=True)
    os.makedirs("static/exports", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    logger.info("ComicCraft startup: verified static/panels and static/exports directories.")
    yield
    logger.info("ComicCraft shutdown: cleanup complete.")


app = FastAPI(
    title="ComicCraft – AI Comic Story Creator",
    description="Generates personalized comic stories, narration, dialogues, AI illustrations, and multi-page PDFs using Gemini Flash, Gemini Pro, and Stable Diffusion. Team ID: 6ab22cb7.",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static folder for CSS, JS, generated panel images and exported PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import and include routes
from app.routes import router as comic_router
app.include_router(comic_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Friendly global exception handler."""
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "team_id": "6ab22cb7",
            "message": "An error occurred while creating your comic.",
            "detail": str(exc),
            "hint": "Check that requirements are installed and your Gemini API key is valid."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
@app.get("/test-image")
def test_image():
    from app.image_generator import test_generation
    return test_generation()