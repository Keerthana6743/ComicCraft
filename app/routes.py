"""
ComicCraft - FastAPI Routes
Team ID: 6ab22cb7

Defines all web and API endpoints:
- GET / : Loads comic creation studio (index.html)
- POST /generate : Handles form submission, orchestrates AI pipeline, renders comic_preview.html
- POST /generate-comic/json : Validates JSON with Pydantic, returns comic data & PDF path
- GET/POST /test-image : Tests Stable Diffusion image generation pipeline
- GET /export-success : Displays PDF download confirmation (export_success.html)
- POST /api/regenerate-panel : Dynamically re-rolls a single panel with updated tone or art style
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image, test_generation
from app.layout_builder import build_comic_layout, organize_comic_page
from app.exporters import save_pdf

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# =============================================================================
# Pydantic Schemas for JSON Endpoint
# =============================================================================

class ComicGenerationRequest(BaseModel):
    """Pydantic schema for /generate-comic/json endpoint."""
    prompt: str = Field(..., min_length=3, description="Core story premise or prompt")
    character_name: str = Field(default="Finn the Fox", description="Main character name")
    setting: str = Field(default="Enchanted Forest", description="Story world or environment")
    tone: str = Field(default="Adventure", description="Story tone (e.g. Adventure, Funny, Sci-Fi)")
    art_style: str = Field(default="Comic Book", description="Visual comic art style")
    num_panels: int = Field(default=5, ge=1, le=10, description="Number of comic panels (default 5)")
    api_key: Optional[str] = Field(default=None, description="Optional Google Gemini API key")


class PanelData(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    narration: str
    dialogue: str
    image_path: str


class ComicGenerationResponse(BaseModel):
    status: str
    team_id: str = "6ab22cb7"
    project_title: str = "ComicCraft"
    prompt: str
    character: str
    setting: str
    tone: str
    art_style: str
    pdf_path: str
    panels: List[PanelData]


class RegeneratePanelRequest(BaseModel):
    prompt: str
    character_name: str
    setting: str
    panel_number: int
    current_title: str
    current_scene: str
    new_tone: str
    new_art_style: str
    api_key: Optional[str] = None


# =============================================================================
# Routes
# =============================================================================

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Renders the ComicCraft studio home page (index.html).
    Provides the comic creation form for story prompt, character, setting, tone, and art style.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "project_title": "ComicCraft",
            "team_id": "6ab22cb7",
            "default_prompt": "A brave fox exploring an enchanted forest",
            "default_character": "Finn the Fox",
            "default_setting": "Enchanted Forest",
            "default_tone": "Adventure",
            "default_art_style": "Comic Book"
        },
    )

@router.post("/generate", response_class=HTMLResponse)
async def post_generate_form(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(default="Finn the Fox"),
    setting: str = Form(default="Enchanted Forest"),
    tone: str = Form(default="Adventure"),
    art_style: str = Form(default="Comic Book"),
    num_panels: int = Form(default=5),
    api_key: Optional[str] = Form(default=None)
):
    """
    Accepts the user's form from index.html:
    1. Generates 5-panel outline via Gemini Flash
    2. Generates detailed story narration & dialogues via Gemini Pro
    3. Generates comic illustrations via Stable Diffusion
    4. Builds comic layout
    5. Creates downloadable PDF
    6. Displays comic_preview.html
    """
    logger.info(f"Received form generation request: '{prompt}', character='{character_name}', tone='{tone}', style='{art_style}'")

    # Step 1: Gemini Flash outline
    outline = generate_outline(
        prompt=prompt,
        character=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
        num_panels=num_panels,
        api_key=api_key
    )

    # Step 2: Gemini Pro story & dialogues
    story = generate_story(
        outline=outline,
        prompt=prompt,
        character=character_name,
        setting=setting,
        tone=tone,
        api_key=api_key
    )

    # Step 3: Stable Diffusion image generation for each panel
    images = []
    for item in outline:
        p_num = item.get("panel_number", len(images) + 1)
        img_prompt = item.get("image_prompt", f"{character_name} in {setting}")
        img_path = generate_image(
            prompt=img_prompt,
            panel_number=p_num,
            art_style=art_style
        )
        images.append(img_path)

    # Step 4: Layout Builder
    story_metadata = {
        "prompt": prompt,
        "character": character_name,
        "setting": setting,
        "tone": tone,
        "art_style": art_style
    }
    panels = build_comic_layout(outline, story, images, metadata=story_metadata)

    # Step 5: PDF Generation
    pdf_path = save_pdf(
        comic_title=prompt,
        panels=panels,
        metadata=story_metadata
    )

    # Render comic_preview.html
    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "request": request,
            "project_title": "ComicCraft",
            "team_id": "6ab22cb7",
            "prompt": prompt,
            "character": character_name,
            "setting": setting,
            "tone": tone,
            "art_style": art_style,
            "num_panels": len(panels),
            "panels": panels,
            "pdf_path": pdf_path
        }
    )


@router.post("/generate-comic/json", response_model=ComicGenerationResponse)
async def post_generate_comic_json(payload: ComicGenerationRequest):
    """
    Accepts JSON input, validates request using Pydantic,
    orchestrates AI models, and returns comic layout data and PDF path.
    """
    logger.info(f"Received JSON generation request: {payload.prompt}")

    # 1. Gemini Flash Outline
    outline = generate_outline(
        prompt=payload.prompt,
        character=payload.character_name,
        setting=payload.setting,
        tone=payload.tone,
        art_style=payload.art_style,
        num_panels=payload.num_panels,
        api_key=payload.api_key
    )

    # 2. Gemini Pro Story
    story = generate_story(
        outline=outline,
        prompt=payload.prompt,
        character=payload.character_name,
        setting=payload.setting,
        tone=payload.tone,
        api_key=payload.api_key
    )

    # 3. Stable Diffusion Images
    images = []
    for item in outline:
        p_num = item.get("panel_number", len(images) + 1)
        img_prompt = item.get("image_prompt", f"{payload.character_name} in {payload.setting}")
        img_path = generate_image(
            prompt=img_prompt,
            panel_number=p_num,
            art_style=payload.art_style
        )
        images.append(img_path)

    # 4. Layout Builder
    story_metadata = {
        "prompt": payload.prompt,
        "character": payload.character_name,
        "setting": payload.setting,
        "tone": payload.tone,
        "art_style": payload.art_style
    }
    panels = build_comic_layout(outline, story, images, metadata=story_metadata)

    # 5. PDF Generation
    pdf_path = save_pdf(
        comic_title=payload.prompt,
        panels=panels,
        metadata=story_metadata
    )

    return ComicGenerationResponse(
        status="success",
        team_id="6ab22cb7",
        project_title="ComicCraft",
        prompt=payload.prompt,
        character=payload.character_name,
        setting=payload.setting,
        tone=payload.tone,
        art_style=payload.art_style,
        pdf_path=pdf_path,
        panels=[
            PanelData(
                panel_number=p["panel_number"],
                title=p["title"],
                scene_description=p["scene_description"],
                image_prompt=p["image_prompt"],
                narration=p["narration"],
                dialogue=p["dialogue"],
                image_path=p["image_path"]
            )
            for p in panels
        ]
    )


@router.get("/test-image")
@router.post("/test-image")
async def get_test_image(
    prompt: str = Query(default="Finn the Fox exploring an enchanted glowing forest"),
    art_style: str = Query(default="Comic Book")
):
    """
    Tests Stable Diffusion image generation and returns pipeline status and image URL.
    """
    result = test_generation(prompt=prompt, art_style=art_style)
    return JSONResponse(result)


@router.get("/export-success", response_class=HTMLResponse)
async def get_export_success(
    request: Request,
    pdf_path: str = Query(...),
    title: str = Query(default="ComicCraft Comic")
):
    """
    Displays successful PDF export confirmation page with direct download link.
    """
    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
            "project_title": "ComicCraft",
            "team_id": "6ab22cb7",
            "pdf_path": pdf_path,
            "comic_title": title
        }
    )


@router.post("/api/regenerate-panel")
async def api_regenerate_panel(payload: RegeneratePanelRequest):
    """
    Dynamic Regeneration Endpoint:
    Allows user to switch tone (e.g. Adventure -> Funny) or art style (e.g. Comic Book -> Manga)
    and regenerate dialogues and image illustration for an individual panel or scene on the fly.
    """
    logger.info(f"Regenerating panel #{payload.panel_number} with tone={payload.new_tone}, style={payload.new_art_style}")

    # Re-craft outline element
    single_outline = [{
        "panel_number": payload.panel_number,
        "title": payload.current_title,
        "scene_description": payload.current_scene,
        "image_prompt": f"{payload.character_name} in {payload.setting}, {payload.new_art_style} style, vivid illustration"
    }]

    # Re-craft story dialogues with new tone
    new_story = generate_story(
        outline=single_outline,
        prompt=payload.prompt,
        character=payload.character_name,
        setting=payload.setting,
        tone=payload.new_tone,
        api_key=payload.api_key
    )

    # Re-generate image with new art style
    new_image_path = generate_image(
        prompt=single_outline[0]["image_prompt"],
        panel_number=payload.panel_number,
        art_style=payload.new_art_style
    )

    narration = new_story[0].get("narration", "") if new_story else ""
    dialogue = new_story[0].get("dialogue", "") if new_story else ""

    return JSONResponse({
        "status": "success",
        "panel_number": payload.panel_number,
        "new_tone": payload.new_tone,
        "new_art_style": payload.new_art_style,
        "narration": narration,
        "dialogue": dialogue,
        "image_path": new_image_path
    })
