"""
ComicCraft - Gemini Pro Integration
Team ID: 6ab22cb7

Expands a comic outline into detailed narration and character dialogues using Google Gemini Pro (models/gemini-1.5-pro).
Outputs: Panel number, Narration (captions), Dialogue (speech balloons).
"""

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Primary model name specified in requirements
PRO_MODEL_NAME = "models/gemini-1.5-pro"
FALLBACK_PRO_MODELS = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]


def _clean_json_text(text: str) -> str:
    """Clean markdown code fences and extraneous text from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    return text


def _build_fallback_story(outline: List[Dict[str, Any]], character: str, tone: str) -> List[Dict[str, Any]]:
    """
    Intelligent fallback story writer matching the outline panels
    when API key is absent or unreachable.
    """
    tone_lower = tone.lower()
    story_panels = []

    for idx, panel in enumerate(outline, start=1):
        title = panel.get("title", f"Scene {idx}")
        desc = panel.get("scene_description", "")

        if idx == 1:
            narration = f"Deep within the heart of the realm, {character} prepared for the unknown. The air was thick with mystery."
            if "funny" in tone_lower:
                dialogue = f'{character}: "Note to self: next time, remember to pack snacks before diving into an epic adventure!"'
            elif "horror" in tone_lower:
                dialogue = f'{character}: "Did... did you hear that whispering in the dark?"'
            elif "superhero" in tone_lower:
                dialogue = f'{character}: "This city needs a guardian, and I won\'t back down!"'
            else:
                dialogue = f'{character}: "Today marks the day everything changes. Time to uncover the truth!"'

        elif idx == 2:
            narration = f"Before {character}'s eyes lay the clue they had sought for months, pulsing with ancient power."
            if "funny" in tone_lower:
                dialogue = f'{character}: "Well, that looks suspiciously shiny. What could possibly go wrong?"'
            else:
                dialogue = f'{character}: "The legends were real! The relic is right here!"'

        elif idx == 3:
            narration = f"Without warning, the peace shattered as danger lurched forward to contest every step."
            if "funny" in tone_lower:
                dialogue = f'{character}: "Whoa! Could we discuss this over herbal tea instead?!"'
            else:
                dialogue = f'{character}: "Stand back! I won\'t let you take this world!"'

        elif idx == 4:
            narration = f"Summoning every ounce of focus, {character} executed a breathtaking maneuver against impossible odds."
            if "funny" in tone_lower:
                dialogue = f'{character}: "Ta-da! Step aside, physics, I have improvisation on my side!"'
            else:
                dialogue = f'{character}: "Now or never! For honor and tomorrow!"'

        else:
            narration = f"As the dust settled, victory shone brightly across the land. A new legend was carved in history."
            if "funny" in tone_lower:
                dialogue = f'{character}: "Piece of cake! Now... where did I leave my keys?"'
            else:
                dialogue = f'{character}: "We did it. The realm is finally safe once again."'

        story_panels.append({
            "panel_number": panel.get("panel_number", idx),
            "narration": narration,
            "dialogue": dialogue
        })

    return story_panels


def generate_story(
    outline: List[Dict[str, Any]],
    prompt: str,
    character: str = "Hero",
    setting: str = "Mystic Realm",
    tone: str = "Adventure",
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Expand a comic outline into rich narration and character dialogues using Gemini Pro.

    Args:
        outline: List of panels from generate_outline().
        prompt: Original user story prompt.
        character: Main character name.
        setting: Story setting.
        tone: Tone (Adventure, Funny, Superhero, Sci-Fi, etc.).
        api_key: Optional Gemini API key.

    Returns:
        List of dictionaries with keys:
            - panel_number: int
            - narration: str (comic caption text)
            - dialogue: str (character spoken lines with character name tag)
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    if not key or key == "your_gemini_api_key_here":
        logger.warning("No valid GEMINI_API_KEY provided. Using intelligent fallback story.")
        return _build_fallback_story(outline, character, tone)

    try:
        genai.configure(api_key=key)
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return _build_fallback_story(outline, character, tone)

    system_instruction = (
        "You are an award-winning comic book writer and dialogue specialist. "
        "Your role is to take a panel-by-panel comic outline and script compelling comic narration "
        "captions and punchy character dialogue.\n"
        "Guidelines:\n"
        f"1. Tone: '{tone}'. Tailor the vocabulary, humor, drama, or suspense strictly to this tone.\n"
        f"2. Main Character: '{character}'. Ensure their personality shines through their speech.\n"
        "3. Narration should read like traditional comic book caption boxes (atmospheric, concise, evocative, 1-2 sentences).\n"
        "4. Dialogue should be formatted clearly as speech balloons, e.g. CharacterName: \"Dialogue line!\". "
        "Can also include secondary characters or sound effects if appropriate.\n"
        "5. Return ONLY a valid JSON array of objects with keys: 'panel_number', 'narration', 'dialogue'.\n"
        "6. Do not include markdown formatting or commentary."
    )

    outline_summary = json.dumps(outline, indent=2)

    user_query = f"""
Given this comic outline:
{outline_summary}

Story Context:
- Story Prompt: {prompt}
- Main Character: {character}
- Setting: {setting}
- Tone: {tone}

Generate the narration caption and character dialogue for each panel in the outline.
Format requirement: JSON array of objects with keys:
"panel_number", "narration", "dialogue"
"""

    models_to_try = [PRO_MODEL_NAME] + FALLBACK_PRO_MODELS

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.75,
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

                if isinstance(data, dict):
                    for possible_key in ["panels", "story", "dialogues"]:
                        if possible_key in data and isinstance(data[possible_key], list):
                            data = data[possible_key]
                            break

                if isinstance(data, list) and len(data) > 0:
                    validated_story = []
                    for idx, item in enumerate(data, start=1):
                        validated_story.append({
                            "panel_number": item.get("panel_number", idx),
                            "narration": item.get("narration", f"Scene {idx} unfolds in {setting}."),
                            "dialogue": item.get("dialogue", f'{character}: "Let us see what lies ahead!"')
                        })
                    logger.info(f"Successfully generated story dialogues using {model_name}")
                    return validated_story

        except Exception as err:
            logger.warning(f"Error calling {model_name} for story: {err}")
            last_error = err
            continue

    logger.error(f"All Gemini Pro models failed. Last error: {last_error}. Returning fallback story.")
    return _build_fallback_story(outline, character, tone)
