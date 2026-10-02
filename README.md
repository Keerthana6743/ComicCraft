# 💥 ComicCraft – AI Comic Story Creator using Gemini Models

> **TEAM ID:** `6ab22cb7`  
> **Project Title:** ComicCraft – AI Comic Story Creator using Gemini Models  
> **Backend Framework:** FastAPI & Uvicorn  
> **AI Models:** Google Gemini 1.5 Flash, Google Gemini 1.5 Pro, Stable Diffusion v1-5  
> **Document Generation:** FPDF / FPDF2  

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features & Dynamic Capabilities](#-key-features--dynamic-capabilities)
3. [System Architecture & Workflow](#-system-architecture--workflow)
4. [File Structure & Responsibilities](#-file-structure--responsibilities)
5. [Prerequisites & Beginner Setup Guide (Windows & VS Code)](#-prerequisites--beginner-setup-guide-windows--vs-code)
6. [Running the Application](#-running-the-application)
7. [API Documentation & Testing Guide](#-api-documentation--testing-guide)
8. [Dynamic Tone & Art Style Regeneration](#-dynamic-tone--art-style-regeneration)
9. [Comprehensive Troubleshooting Guide](#-comprehensive-troubleshooting-guide)
10. [Submission Checklist](#-submission-checklist)

---

## 🌟 Project Overview

**ComicCraft** is an end-to-end Generative AI web platform that transforms a user's raw story idea into a full-fledged, multi-page comic book. By chaining cutting-edge Large Language Models and Diffusion models, ComicCraft automatically writes a structured narrative, crafts evocative scene descriptions, scripts lively character dialogues and narration captions, renders stylized comic art, and compiles the result into a print-ready downloadable PDF.

### What the User Inputs:
* **Story Prompt:** Core premise or idea (e.g., *"A brave fox exploring an enchanted forest"*).
* **Main Character Name:** Protagonist (e.g., *"Finn the Fox"*).
* **Setting:** Story world (e.g., *"Enchanted Forest"*).
* **Story Tone:** Narrative pacing & mood (e.g., *Adventure, Funny, Superhero, Sci-Fi, Mystery, Horror, Fantasy, Action*).
* **Art Style:** Visual treatment (e.g., *Comic Book, Manga, Graphic Novel, Retro Pop Art, Watercolor, Cartoon*).

### What ComicCraft Generates:
1. **5-Panel Comic Outline:** Sequenced with titles, descriptions, and Stable Diffusion prompts.
2. **Narration & Character Dialogues:** Comic captions and speech balloons tailored to the selected tone.
3. **AI Comic Illustrations:** Rendered using Stable Diffusion `runwayml/stable-diffusion-v1-5` (with intelligent fallback comic canvas).
4. **Interactive Comic Preview:** Responsive web preview with zoom, prompt inspectors, and panel re-rolling.
5. **Downloadable Multi-Page PDF:** Complete comic book with cover page, metadata box, framed illustrations, and styled speech bubbles.

---

## 🔄 System Architecture & Workflow

```text
               +----------------------------------+
               |     User Input / Web Form        |
               | (Prompt, Character, Tone, Style) |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |       FastAPI Backend API        |
               |         (app/routes.py)          |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |      1. Gemini 1.5 Flash         |
               |     (app/gemini_flash.py)        |
               |  Generates 5-Panel Story Outline |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |       2. Gemini 1.5 Pro          |
               |      (app/gemini_pro.py)         |
               | Detailed Narration & Dialogues   |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |     3. Stable Diffusion v1-5     |
               |    (app/image_generator.py)      |
               |  Renders Comic Panel Images      |
               +-----------------+----------------+
                                 |
                                 v
               +----------------------------------+
               |       4. Layout Builder          |
               |    (app/layout_builder.py)       |
               | Unifies Images, Text & Dialogue  |
               +-----------------+----------------+
                                 |
                    +------------+------------+
                    |                         |
                    v                         v
       +-----------------------+   +-----------------------+
       |   5. Comic Preview    |   |     6. FPDF Engine    |
       |  (comic_preview.html) |   |   (app/exporters.py)  |
       |  Interactive Browser  |   | Downloadable Multi-   |
       |      Experience       |   |       Page PDF        |
       +-----------------------+   +-----------------------+
```

---

## 📂 File Structure & Responsibilities

```text
ComicCraft/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI app initialization, static mounting, lifecycles
│   ├── routes.py             # Route handlers (/, /generate, /generate-comic/json, /test-image)
│   ├── gemini_flash.py       # Gemini 1.5 Flash outline generator
│   ├── gemini_pro.py         # Gemini 1.5 Pro story, narration & dialogue generator
│   ├── image_generator.py    # Stable Diffusion pipeline & Comic Canvas fallback generator
│   ├── layout_builder.py     # Data assembler linking text, dialogue, and image assets
│   └── exporters.py          # FPDF multi-page comic book PDF compiler
│
├── templates/
│   ├── index.html            # Studio creation form & tone/style selector
│   ├── comic_preview.html    # Interactive reading preview & dynamic re-generation toolbar
│   └── export_success.html   # PDF confirmation & embedded viewer
│
├── static/
│   ├── style.css             # Complete modern comic visual design system
│   ├── script.js             # Form animation, dynamic re-roll, and localStorage API key
│   ├── panels/               # Generated panel PNG illustrations
│   └── exports/              # Compiled downloadable PDF files
│
├── .env.example              # Environment variables template
├── requirements.txt          # Python package requirements
└── README.md                 # Complete project manual & guide
```

### Detailed File Responsibilities

| File | Primary Responsibility |
|---|---|
| `app/main.py` | Configures FastAPI, sets application lifespan (creates directories), mounts `/static`, includes routes, and handles exceptions. |
| `app/routes.py` | Exposes all web and JSON endpoints. Validates input using Pydantic, orchestrates AI generation steps, and serves HTML/JSON responses. |
| `app/gemini_flash.py` | Calls `models/gemini-1.5-flash` with system prompt engineering to generate a structured 5-panel outline containing titles, scenes, and image prompts. |
| `app/gemini_pro.py` | Calls `models/gemini-1.5-pro` to produce atmospheric narration captions and character-specific spoken dialogue matched to the outline and tone. |
| `app/image_generator.py` | Executes Stable Diffusion (`runwayml/stable-diffusion-v1-5`) on GPU or CPU. If hardware or internet is constrained, utilizes a high-res Comic Canvas fallback engine. |
| `app/layout_builder.py` | Merges outline metadata, story dialogue arrays, and saved image URLs into a coherent panel list for templating and API responses. |
| `app/exporters.py` | Uses FPDF to construct an authentic comic book PDF featuring a cover page, styled yellow caption boxes, speech bubbles, and decorative borders. |
| `templates/index.html` | Front-end comic studio interface with instant "Surprise Me" randomizer, visual art style cards, and an animated comic loading overlay. |
| `templates/comic_preview.html` | High-impact reading layout displaying comic panels, prompt inspection drawer, panel re-roll buttons, and dynamic tone switching. |
| `templates/export_success.html` | Celebration screen confirming PDF creation with embedded PDF viewer and instant download button. |
| `static/style.css` | Premium comic book aesthetic using Google Fonts (*Bangers*, *Comic Neue*, *Outfit*), halftone patterns, glassmorphism, and speech balloon geometry. |
| `static/script.js` | Manages loading progress animation ("POW!", "BAM!"), saves API keys to browser `localStorage`, and handles async panel regeneration. |

---

## 💻 Prerequisites & Beginner Setup Guide (Windows & VS Code)

Follow these step-by-step instructions to get ComicCraft running smoothly on Windows.

### Step 1: Install Python on Windows
1. Download Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/).
2. ⚠️ **CRITICAL STEP:** In the installer, **check the box** that says:  
   `[x] Add Python.exe to PATH` before clicking "Install Now".
3. Verify your installation by opening Windows PowerShell and typing:
   ```powershell
   python --version
   pip --version
   ```

### Step 2: Open Project in VS Code
1. Open Visual Studio Code.
2. Click **File > Open Folder...** and select the `comiccraft project` folder.
3. Open the built-in terminal by pressing `` Ctrl + ` `` (Backtick) or clicking **Terminal > New Terminal**.

### Step 3: Create and Activate Virtual Environment
Run the following commands in the VS Code PowerShell terminal:

```powershell
# 1. Create a virtual environment named comiccraft-env
python -m venv comiccraft-env

# 2. Activate the virtual environment on Windows
.\comiccraft-env\Scripts\Activate.ps1
```

> **Note on PowerShell Execution Policy:** If you see an error like `cannot be loaded because running scripts is disabled`, run this one-time command in PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then re-run `.\comiccraft-env\Scripts\Activate.ps1`. When activated, your prompt will show `(comiccraft-env)`.

### Step 4: Install Required Packages
Install the project dependencies defined in `requirements.txt`:

```powershell
pip install -r requirements.txt
```

*(Optional PyTorch with CUDA for NVIDIA GPU users):*
If your machine has a dedicated NVIDIA GPU and you want full hardware-accelerated Stable Diffusion:
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Step 5: Configure Gemini API Key
1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Open `.env` and replace `your_gemini_api_key_here` with your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
   *(Alternatively, you can paste your key directly in the web UI under the "Gemini API Key" toggle, which saves it in your browser!)*

---

## 🚀 Running the Application

Ensure your virtual environment is active `(comiccraft-env)`, then start the Uvicorn server:

```powershell
uvicorn app.main:app --reload
```

Output should show:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Open the Application:
* **Comic Studio UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative API Documentation (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 API Documentation & Testing Guide

FastAPI automatically provides an interactive OpenAPI / Swagger UI at `/docs`.

### Main Endpoints

#### 1. `GET /`
* **Purpose:** Loads the main comic creation web form (`index.html`).
* **Test:** Navigate to `http://127.0.0.1:8000/` in any browser.

#### 2. `POST /generate`
* **Purpose:** Accepts standard HTML Form submission from the web UI, executes the full pipeline, and returns the rendered `comic_preview.html`.
* **Form Parameters:**
  * `prompt`: Story premise
  * `character_name`: Protagonist name
  * `setting`: Story environment
  * `tone`: Tone name (e.g. `Adventure`, `Funny`)
  * `art_style`: Visual style (e.g. `Comic Book`, `Manga`)
  * `num_panels`: Number of panels (default `5`)
  * `api_key`: Optional Gemini key

#### 3. `POST /generate-comic/json`
* **Purpose:** Headless REST API endpoint validated via Pydantic. Returns JSON with panel outlines, narration, dialogues, image paths, and PDF file path.
* **Testing via curl:**
  ```powershell
  curl -X POST "http://127.0.0.1:8000/generate-comic/json" `
    -H "Content-Type: application/json" `
    -d '{
      "prompt": "A brave fox exploring an enchanted forest",
      "character_name": "Finn the Fox",
      "setting": "Enchanted Forest",
      "tone": "Adventure",
      "art_style": "Comic Book",
      "num_panels": 5
    }'
  ```
* **Sample JSON Response:**
  ```json
  {
    "status": "success",
    "team_id": "6ab22cb7",
    "project_title": "ComicCraft",
    "prompt": "A brave fox exploring an enchanted forest",
    "character": "Finn the Fox",
    "setting": "Enchanted Forest",
    "tone": "Adventure",
    "art_style": "Comic Book",
    "pdf_path": "/static/exports/comic_1711929381.pdf",
    "panels": [
      {
        "panel_number": 1,
        "title": "A New Journey Begins",
        "scene_description": "Finn stands at the entrance of the glowing forest.",
        "image_prompt": "Finn the Fox in an enchanted forest, comic book style...",
        "narration": "Deep within the heart of the realm, Finn prepared for the unknown.",
        "dialogue": "Finn: \"Today marks the day everything changes!\"",
        "image_path": "/static/panels/panel_1711929381_1.png"
      }
    ]
  }
  ```

#### 4. `GET /test-image`
* **Purpose:** Validates Stable Diffusion model pipeline and image generation speed.
* **Test:** Open `http://127.0.0.1:8000/test-image` in your browser or click **"🧪 Test Image AI"** in the top navigation bar.

#### 5. `POST /api/regenerate-panel`
* **Purpose:** Allows instant, single-panel re-generation when a user wants to re-roll a scene or experiment with new tone/style parameters.

---

## ⚡ Dynamic Tone & Art Style Regeneration

ComicCraft includes built-in dynamic adaptation. If you change the story tone or visual style:

1. **Full Storyline Regeneration:**
   * On the Comic Preview page, locate the **"DYNAMIC RE-GENERATION"** toolbar.
   * Change Tone (e.g. from `Adventure` to `Funny`) or Art Style (e.g. from `Comic Book` to `Manga`).
   * Click **"🔄 Re-generate Storyline"**.
   * The Gemini models re-script the character's voice (e.g., adding humorous dialogue and witty narration) and Stable Diffusion re-renders the panel artwork to match the new visual tokens.

2. **Single Panel Re-Roll:**
   * Click the **"🎲 Re-roll Panel"** button located on any individual comic panel card.
   * The panel will immediately re-generate and update seamlessly without refreshing the page!

---

## 🛠️ Comprehensive Troubleshooting Guide

### 1. `Python was not found; run without arguments to install from the Microsoft Store...`
* **Cause:** Windows App Execution Aliases intercepting the `python` command, or Python was installed without checking "Add Python to PATH".
* **Solution:**
  1. Open Windows **Settings > Apps > Advanced app settings > App execution aliases**.
  2. Toggle **OFF** both `python.exe` and `python3.exe` for "App Installer".
  3. Re-run your Python installer and select **"Add Python to PATH"** (or choose "Modify > Next > Check 'Add Python to environment variables'").
  4. Restart your terminal or VS Code.

### 2. Package Installation Errors (`pip install` fails)
* **Fix `pip` outdated:**
  ```powershell
  python -m pip install --upgrade pip setuptools wheel
  ```
* **Torch / CUDA Compatibility:**
  If installing full GPU PyTorch fails on your configuration, PyTorch CPU mode installs cleanly:
  ```powershell
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
  ```
  *(ComicCraft automatically detects CPU vs GPU and adjusts diffusion steps or utilizes the fallback comic canvas).*

### 3. API Key Errors (`google.api_core.exceptions.PermissionDenied` or `403`)
* **Cause:** The Gemini API key in `.env` is either invalid, expired, or has not been enabled for the Gemini 1.5 Flash/Pro models.
* **Solution:**
  1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and generate a fresh API key.
  2. Ensure there are no leading/trailing quotation marks or spaces in `.env`:
     ```env
     GEMINI_API_KEY=AIzaSyExampleKeyWithoutQuotes
     ```
  3. You can also paste the key directly into the Web UI field under "Gemini API Key".

### 4. Stable Diffusion Memory Errors (`CUDA out of memory`)
* **Cause:** Running 512x512 diffusion on a GPU with less than 4GB VRAM.
* **Solution:**
  1. Set `SD_DEVICE=cpu` in your `.env` file to use CPU inference with attention slicing.
  2. Or set `ENABLE_FALLBACK_IMAGE_GEN=true` in `.env` to enable ComicCraft's ultra-fast comic canvas generator that renders panels with vibrant comic halftones, emblems, and action badges without needing GPU VRAM!

### 5. Uvicorn Errors (`[Errno 10048] address already in use`)
* **Cause:** Another process or previous instance is running on port 8000.
* **Solution:**
  Run Uvicorn on a different port:
  ```powershell
  uvicorn app.main:app --reload --port 8080
  ```
  Then open `http://127.0.0.1:8080`.

---

## ✅ Submission Checklist

- [x] **Team ID Displayed:** `6ab22cb7` prominently embedded in web headers, footers, PDFs, and API schemas.
- [x] **Gemini 1.5 Flash Integration:** Outlines 5 structured panels (title, scene, image prompt).
- [x] **Gemini 1.5 Pro Integration:** Expands outline into narration captions and character dialogue.
- [x] **Stable Diffusion v1-5 Integration:** Generates panel illustrations with Hugging Face diffusers.
- [x] **Layout Builder:** Unifies text, dialogue, and illustrations into organized panel structures.
- [x] **FPDF Multi-Page PDF:** Generates downloadable comic book PDF with cover, borders, and speech captions.
- [x] **All Routes Implemented:** `/`, `/generate`, `/generate-comic/json`, `/test-image`, `/export-success`.
- [x] **Dynamic Regeneration:** Tone and art style updates trigger re-scripting and illustration re-generation.
- [x] **Full Source Code Provided:** Every file completely written without placeholders.
- [x] **Beginner Instructions:** Windows & VS Code setup guide and comprehensive troubleshooting included.

---
*Created for ComicCraft AI Comic Story Creator • Team ID: 6ab22cb7*
