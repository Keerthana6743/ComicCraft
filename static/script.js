/**
 * ComicCraft - Frontend Interactions & Dynamic Engine
 * Team ID: 6ab22cb7
 */

document.addEventListener("DOMContentLoaded", () => {
  initApiKeyStorage();
  initSurpriseMe();
  initFormSubmission();
  initPromptInspectors();
  initDynamicRegeneration();
  initTestImageModal();
});

/* ==========================================================================
   1. API Key LocalStorage Management
   ========================================================================== */
function initApiKeyStorage() {
  const apiKeyInput = document.getElementById("apiKeyInput");
  const accordionToggle = document.getElementById("apiKeyToggle");
  const accordionContent = document.getElementById("apiKeyAccordionContent");

  if (apiKeyInput) {
    const savedKey = localStorage.getItem("comiccraft_gemini_api_key");
    if (savedKey) {
      apiKeyInput.value = savedKey;
      if (accordionToggle) {
        accordionToggle.querySelector("span:first-child").innerHTML = "🔑 Gemini API Key (Saved in Browser)";
      }
    }

    apiKeyInput.addEventListener("input", (e) => {
      const val = e.target.value.trim();
      if (val) {
        localStorage.setItem("comiccraft_gemini_api_key", val);
      } else {
        localStorage.removeItem("comiccraft_gemini_api_key");
      }
    });
  }

  if (accordionToggle && accordionContent) {
    accordionToggle.addEventListener("click", () => {
      accordionContent.classList.toggle("open");
      const icon = accordionToggle.querySelector(".accordion-icon");
      if (icon) {
        icon.textContent = accordionContent.classList.contains("open") ? "▲" : "▼";
      }
    });
  }
}

/* ==========================================================================
   2. Surprise Me / Random Prompt Generator
   ========================================================================== */
const INSPIRATION_IDEAS = [
  {
    prompt: "A brave fox exploring an enchanted forest in search of the lost Crystal of Whispers",
    character: "Finn the Fox",
    setting: "Enchanted Glowing Forest",
    tone: "Adventure",
    art_style: "Comic Book"
  },
  {
    prompt: "A mischievous raccoon who accidentally activates a top-secret quantum teleportation device",
    character: "Rusty the Raccoon",
    setting: "Underground High-Tech Laboratory",
    tone: "Funny",
    art_style: "Cartoon"
  },
  {
    prompt: "A vigilante cyber-samurai defending the neon-lit alleyways of futuristic Neo-Tokyo from robotic enforcers",
    character: "Ren Kurogane",
    setting: "Neo-Tokyo Cyber City",
    tone: "Superhero",
    art_style: "Manga"
  },
  {
    prompt: "A steampunk airship captain racing through an electric thunderstorm to deliver the Cure of Zephyria",
    character: "Captain Lyra Vance",
    setting: "Floating Cloud City",
    tone: "Adventure",
    art_style: "Graphic Novel"
  },
  {
    prompt: "A clumsy apprentice wizard whose failed potion accidentally brings every gargoyle in the academy to life",
    character: "Oliver the Apprentice",
    setting: "Arcane High Tower",
    tone: "Funny",
    art_style: "Retro Pop Art"
  },
  {
    prompt: "An interstellar detective investigating the mysterious disappearance of the moon's brightest lighthouse beam",
    character: "Detective Orion Sol",
    setting: "Lunar Orbital Station",
    tone: "Mystery",
    art_style: "Comic Book"
  }
];

function initSurpriseMe() {
  const surpriseBtn = document.getElementById("surpriseBtn");
  if (!surpriseBtn) return;

  surpriseBtn.addEventListener("click", () => {
    const randomPick = INSPIRATION_IDEAS[Math.floor(Math.random() * INSPIRATION_IDEAS.length)];

    const promptInput = document.getElementById("storyPromptInput");
    const charInput = document.getElementById("charNameInput");
    const settingInput = document.getElementById("settingInput");

    if (promptInput) {
      promptInput.value = randomPick.prompt;
      promptInput.classList.add("highlight-change");
      setTimeout(() => promptInput.classList.remove("highlight-change"), 600);
    }
    if (charInput) charInput.value = randomPick.character;
    if (settingInput) settingInput.value = randomPick.setting;

    // Set tone radio
    const toneRadio = document.querySelector(`input[name="tone"][value="${randomPick.tone}"]`);
    if (toneRadio) toneRadio.checked = true;

    // Set art style radio
    const styleRadio = document.querySelector(`input[name="art_style"][value="${randomPick.art_style}"]`);
    if (styleRadio) styleRadio.checked = true;
  });
}

/* ==========================================================================
   3. Dynamic Loading Screen & Submission
   ========================================================================== */
function initFormSubmission() {
  const comicForm = document.getElementById("comicCreationForm");
  const loadingOverlay = document.getElementById("loadingOverlay");

  if (!comicForm || !loadingOverlay) return;

  const stepTitle = document.getElementById("loadingStepTitle");
  const stepDesc = document.getElementById("loadingStepDesc");
  const progressBar = document.getElementById("loadingProgressBar");
  const soundBadge = document.getElementById("loadingSoundBadge");

  const soundWords = ["POW!", "BAM!", "WHOOSH!", "ZAP!", "KRAK!"];

  const steps = [
    { title: "Consulting Gemini Flash...", desc: "Drafting a structured 5-panel comic storyline & visual shot outlines", width: "25%", pillId: "step1" },
    { title: "Summoning Gemini Pro...", desc: "Writing dramatic comic captions, punchy dialogues, and character banter", width: "50%", pillId: "step2" },
    { title: "Diffusing Comic Illustrations...", desc: "Stable Diffusion is generating stylized high-res comic art panels", width: "75%", pillId: "step3" },
    { title: "Assembling Comic & PDF...", desc: "Binding panels, speech bubbles, and rendering downloadable comic PDF", width: "95%", pillId: "step4" }
  ];

  comicForm.addEventListener("submit", (e) => {
    // Show overlay
    loadingOverlay.classList.add("active");

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      if (currentStep < steps.length) {
        const s = steps[currentStep];
        if (stepTitle) stepTitle.textContent = s.title;
        if (stepDesc) stepDesc.textContent = s.desc;
        if (progressBar) progressBar.style.width = s.width;

        if (soundBadge) {
          soundBadge.textContent = soundWords[currentStep % soundWords.length];
        }

        // Highlight step pills
        document.querySelectorAll(".loading-steps-pills .step-item").forEach(el => el.classList.remove("active"));
        const activePill = document.getElementById(s.pillId);
        if (activePill) activePill.classList.add("active");
      } else {
        clearInterval(interval);
      }
    }, 2800);
  });
}

/* ==========================================================================
   4. Prompt Inspectors on Comic Preview
   ========================================================================== */
function initPromptInspectors() {
  document.querySelectorAll(".prompt-details-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      const panelCard = btn.closest(".comic-panel-card");
      if (!panelCard) return;
      const inspector = panelCard.querySelector(".panel-prompt-inspector");
      if (inspector) {
        inspector.classList.toggle("open");
        const isOpen = inspector.classList.contains("open");
        btn.innerHTML = isOpen ? "👁️ Hide Prompt Inspector" : "🔍 Inspect Prompt & Shot Details";
      }
    });
  });
}

/* ==========================================================================
   5. Dynamic Panel Regeneration
   ========================================================================== */
function initDynamicRegeneration() {
  document.querySelectorAll(".btn-reroll-panel").forEach(btn => {
    btn.addEventListener("click", async () => {
      const panelCard = btn.closest(".comic-panel-card");
      if (!panelCard) return;

      const panelNum = btn.dataset.panelNumber;
      const title = panelCard.querySelector(".panel-title-text")?.textContent || `Panel ${panelNum}`;
      const sceneDesc = btn.dataset.sceneDesc || "";
      const prompt = document.getElementById("previewPrompt")?.value || "";
      const character = document.getElementById("previewCharacter")?.value || "Hero";
      const setting = document.getElementById("previewSetting")?.value || "World";
      const currentTone = document.getElementById("previewTone")?.value || "Adventure";
      const currentStyle = document.getElementById("previewArtStyle")?.value || "Comic Book";

      const originalBtnText = btn.innerHTML;
      btn.innerHTML = "⏳ Re-rolling...";
      btn.disabled = true;

      const apiKey = localStorage.getItem("comiccraft_gemini_api_key") || "";

      try {
        const response = await fetch("/api/regenerate-panel", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: prompt,
            character_name: character,
            setting: setting,
            panel_number: parseInt(panelNum, 10),
            current_title: title,
            current_scene: sceneDesc,
            new_tone: currentTone,
            new_art_style: currentStyle,
            api_key: apiKey
          })
        });

        if (!response.ok) {
          throw new Error("Regeneration failed");
        }

        const data = await response.json();

        // Update image
        const imgElem = panelCard.querySelector(".panel-image-img");
        if (imgElem && data.image_path) {
          imgElem.src = `${data.image_path}?t=${Date.now()}`;
        }

        // Update narration
        const narrationElem = panelCard.querySelector(".caption-text");
        if (narrationElem && data.narration) {
          narrationElem.textContent = data.narration;
        }

        // Update dialogue
        const dialogueElem = panelCard.querySelector(".bubble-dialogue-text");
        if (dialogueElem && data.dialogue) {
          dialogueElem.textContent = data.dialogue;
        }

        btn.innerHTML = "✨ Done!";
        setTimeout(() => {
          btn.innerHTML = originalBtnText;
          btn.disabled = false;
        }, 1500);

      } catch (err) {
        console.error("Error regenerating panel:", err);
        btn.innerHTML = "⚠️ Retry";
        btn.disabled = false;
      }
    });
  });
}

/* ==========================================================================
   6. Test Image Trigger
   ========================================================================== */
function initTestImageModal() {
  const testBtn = document.getElementById("testImageBtn");
  if (!testBtn) return;

  testBtn.addEventListener("click", async () => {
    const originalText = testBtn.innerHTML;
    testBtn.innerHTML = "🧪 Testing Generator...";
    testBtn.disabled = true;

    try {
      const res = await fetch("/test-image?prompt=Finn the Fox in an enchanted forest&art_style=Comic Book");
      const data = await res.json();
      alert(`Stable Diffusion Pipeline Test:\n\nStatus: ${data.status}\nDevice: ${data.device}\nModel: ${data.model}\nActive: ${data.pipeline_active}\nTime: ${data.duration_seconds}s\nSaved to: ${data.image_path}`);
    } catch (err) {
      alert("Test failed: " + err.message);
    } finally {
      testBtn.innerHTML = originalText;
      testBtn.disabled = false;
    }
  });
}
