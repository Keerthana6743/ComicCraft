"""
ComicCraft - Gemini Flash Integration
Team ID: 6ab22cb7

Generates a structured 5-panel comic outline using Google Gemini Flash (models/gemini-1.5-flash).
Outputs: Panel number, Panel title, Scene description, Image generation prompt.
"""

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Primary model name specified in requirements
FLASH_MODEL_NAME = "models/gemini-1.5-flash"
FALLBACK_FLASH_MODELS = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]


def _clean_json_text(text: str) -> str:
    """Clean markdown code fences and extraneous text from LLM response."""
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    return text


def _build_fallback_outline(prompt: str, character: str, setting: str, tone: str, art_style: str, num_panels: int = 5) -> List[Dict[str, Any]]:
    """
    Intelligent dynamic fallback generator used if API key is not configured
    or if API limits are temporarily hit. Ensures the application always works.
    """
    templates = [
        {
            "panel_number": 1,
            "title": "A New Journey Begins",
            "scene_description": f"{character} stands at the threshold of {setting}, observing the mysterious horizon with a sense of {tone.lower()}.",
            "image_prompt": f"A comic book panel showing {character} at {setting}, looking forward with excitement, {art_style} style, detailed linework, vibrant comic colors, establishing wide shot."
        },
        {
            "panel_number": 2,
            "title": "The Hidden Secret",
            "scene_description": f"{character} discovers an ancient glowing artifact or hidden clue inside {setting}, illuminated by dramatic lighting.",
            "image_prompt": f"Close-up comic panel of {character} discovering a glowing mysterious ancient artifact in {setting}, dramatic shadows, {art_style} style, vivid ink illustration."
        },
        {
            "panel_number": 3,
            "title": "Unforeseen Challenge",
            "scene_description": f"An unexpected obstacle or tricky rival appears in {setting}, testing {character}'s courage and wits in a {tone.lower()} manner.",
            "image_prompt": f"Dynamic action comic panel, {character} facing an obstacle or encounter in {setting}, energetic composition, speed lines, {art_style} style, bold comic coloring."
        },
        {
            "panel_number": 4,
            "title": "The Decisive Move",
            "scene_description": f"{character} uses quick thinking and special skills to solve the dilemma within {setting}.",
            "image_prompt": f"Heroic comic panel of {character} performing a clever and brave feat in {setting}, focused expression, {art_style} style, high quality comic book art."
        },
        {
            "panel_number": 5,
            "title": "Triumphant Horizon",
            "scene_description": f"With the mystery resolved, {character} celebrates success in {setting} as a peaceful aura settles across the land.",
            "image_prompt": f"Cinematic comic panel of {character} smiling in triumph at {setting} under a golden sky, heroic posture, {art_style} style, comic masterpiece."
        }
    ]
    return templates[:num_panels]


def generate_outline(
    prompt: str,
    character: str = "Hero",
    setting: str = "Mystic Realm",
    tone: str = "Adventure",
    art_style: str = "Comic Book",
    num_panels: int = 5,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate a structured N-panel comic outline using Gemini Flash.

    Args:
        prompt: User's core story prompt/premise.
        character: Main character name.
        setting: Story setting/environment.
        tone: Tone of the comic (e.g. Adventure, Funny, Sci-Fi, Dark).
        art_style: Visual style (e.g. Comic Book, Manga, Retro Pop Art).
        num_panels: Number of panels (default 5).
        api_key: Optional Gemini API key (defaults to os.environ['GEMINI_API_KEY']).

    Returns:
        List of dictionaries with keys:
            - panel_number: int
            - title: str
            - scene_description: str
            - image_prompt: str
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    if not key or key == "your_gemini_api_key_here":
        logger.warning("No valid GEMINI_API_KEY provided. Using intelligent fallback outline.")
        return _build_fallback_outline(prompt, character, setting, tone, art_style, num_panels)

    # Configure Gemini SDK
    try:
        genai.configure(api_key=key)
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return _build_fallback_outline(prompt, character, setting, tone, art_style, num_panels)

    system_instruction = (
        "You are an expert comic book story architect and visual storyboard designer. "
        "Your task is to take a user's story prompt and generate a structured, visually engaging "
        f"{num_panels}-panel comic outline.\n"
        "Rules:\n"
        "1. Every panel must advance the narrative clearly with a beginning, middle, turning point, and climax/resolution.\n"
        "2. The image_prompt must be highly descriptive, specifying character appearance, pose, camera angle, lighting, "
        f"and explicit art style: '{art_style}'. Avoid generic descriptions.\n"
        "3. You MUST respond with ONLY valid raw JSON array containing exactly "
        f"{num_panels} panel objects with keys: 'panel_number', 'title', 'scene_description', 'image_prompt'.\n"
        "4. Do NOT include markdown fences, comments, or introductory text."
    )

    user_query = f"""
Create a {num_panels}-panel comic outline based on the following details:
- Story Prompt: {prompt}
- Main Character: {character}
- Setting: {setting}
- Tone: {tone}
- Art Style: {art_style}

Format requirement: A JSON array of {num_panels} objects.
Example element:
{{
  "panel_number": 1,
  "title": "Panel Title",
  "scene_description": "Detailed description of what is happening in the scene.",
  "image_prompt": "{character} in {setting}, {art_style} comic style, bold ink lines, dynamic composition, dramatic lighting, high quality comic book panel"
}}
"""

    models_to_try = [FLASH_MODEL_NAME] + FALLBACK_FLASH_MODELS

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json" if "1.5" in model_name else "text/plain"
                }
            )

            response = model.generate_content(
                contents=[
                    {"role": "user", "parts": [system_instruction + "\n\n" + user_query]}
                ]
            )

            if response and response.text:
                cleaned = _clean_json_text(response.text)
                data = json.loads(cleaned)

                # If root is dict with a "panels" key
                if isinstance(data, dict):
                    for possible_key in ["panels", "outline", "comic"]:
                        if possible_key in data and isinstance(data[possible_key], list):
                            data = data[possible_key]
                            break

                if isinstance(data, list) and len(data) > 0:
                    validated_panels = []
                    for idx, item in enumerate(data, start=1):
                        validated_panels.append({
                            "panel_number": item.get("panel_number", idx),
                            "title": item.get("title", f"Panel {idx}"),
                            "scene_description": item.get("scene_description", f"Scene with {character}"),
                            "image_prompt": item.get("image_prompt", f"{character} in {setting}, {art_style} style, comic illustration")
                        })
                    logger.info(f"Successfully generated outline using {model_name}")
                    return validated_panels[:num_panels]

        except Exception as err:
            logger.warning(f"Error calling {model_name} for outline: {err}")
            last_error = err
            continue

    logger.error(f"All Gemini Flash models failed. Last error: {last_error}. Returning fallback outline.")
    return _build_fallback_outline(prompt, character, setting, tone, art_style, num_panels)
