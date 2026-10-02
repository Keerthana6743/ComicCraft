"""
ComicCraft - Layout Builder
Team ID: 6ab22cb7

Combines Gemini Flash outline, Gemini Pro story narration and dialogues,
and Stable Diffusion generated images into unified, structured comic panels
ready for Jinja2 templates, REST APIs, and PDF compilation.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def build_comic_layout(
    outline: List[Dict[str, Any]],
    story: List[Dict[str, Any]],
    images: List[str],
    metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Match outline, story, and image paths into a consolidated list of panel dictionaries.

    Args:
        outline: List of panel outline dicts (title, scene_description, image_prompt).
        story: List of panel story dicts (narration, dialogue).
        images: List of relative image URL paths (/static/panels/...).
        metadata: Optional dictionary with story context (prompt, character, setting, tone, art_style).

    Returns:
        List of structured panel dictionaries with all attributes unified.
    """
    total_panels = max(len(outline), len(story), len(images))
    comic_panels = []

    # Map story items by panel_number for fast, accurate lookup
    story_map = {}
    for s in story:
        p_num = s.get("panel_number")
        if p_num is not None:
            story_map[int(p_num)] = s

    for i in range(total_panels):
        panel_num = i + 1

        # Retrieve outline piece
        outline_item = outline[i] if i < len(outline) else {}
        title = outline_item.get("title", f"Panel {panel_num}")
        scene_desc = outline_item.get("scene_description", "An exciting comic scene unfolds.")
        img_prompt = outline_item.get("image_prompt", "")

        # Retrieve story piece
        story_item = story_map.get(panel_num, (story[i] if i < len(story) else {}))
        narration = story_item.get("narration", f"Scene {panel_num} continues.")
        dialogue = story_item.get("dialogue", "")

        # Retrieve image path
        image_path = images[i] if i < len(images) else "/static/panels/placeholder.png"

        comic_panels.append({
            "panel_number": panel_num,
            "title": title,
            "scene_description": scene_desc,
            "image_prompt": img_prompt,
            "narration": narration,
            "dialogue": dialogue,
            "image_path": image_path,
            # Extra convenience aliases
            "story_text": narration,
            "image_url": image_path
        })

    logger.info(f"Built comic layout with {len(comic_panels)} panels successfully.")
    return comic_panels


def organize_comic_page(
    comic_panels: List[Dict[str, Any]],
    story_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Wraps panels with story metadata, team ID, and page layout configuration.
    """
    return {
        "team_id": "6ab22cb7",
        "project_title": "ComicCraft",
        "title": story_info.get("prompt", "My Comic Adventure"),
        "character": story_info.get("character", "Hero"),
        "setting": story_info.get("setting", "Mysterious World"),
        "tone": story_info.get("tone", "Adventure"),
        "art_style": story_info.get("art_style", "Comic Book"),
        "total_panels": len(comic_panels),
        "panels": comic_panels
    }
