# Lesson 09 — Building Image Generation Applications

> Source: `09-building-image-applications` · Retargeted from DALL·E/gpt-image to Gemini image models.

## 🎯 Goal
Generate and edit images from Python, with safety guardrails.

---

## 1. What is image generation?
A model turns a natural-language prompt into a picture. Modern models combine transformer +
diffusion techniques: they learn text↔image relationships in training, then iteratively "denoise"
random noise into an image matching the description.

Useful across MedTech, architecture, tourism, game development, marketing, education.

## 2. Which Gemini image model? (✅ available to this key)

| Model | Notes |
|---|---|
| **`gemini-3.1-flash-image`** | "Nano Banana 2" — high-efficiency, recommended default |
| `gemini-3.1-flash-lite-image` | Ultra-low latency |
| `gemini-3-pro-image` | "Banana Pro" — state of the art, highly contextual |
| `gemini-2.5-flash-image` | Previous generation, fast |

## 3. Setup

```bash
pip install -U google-genai python-dotenv pillow
```

## 4. Generate an image

```python
import base64, os
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()
client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Bunny on a horse, holding a lollipop, on a foggy meadow where it grows daffodils",
)

os.makedirs("images", exist_ok=True)
path = "images/generated-image.png"
with open(path, "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))

Image.open(path).show()
```

> ⚠️ **Images come back as base64**, not a URL. You decode `output_image.data` to bytes and write the
> file yourself — there is nothing to download.

## 5. Edit an image
Pass the original image alongside the text instruction:

```python
import base64
from google import genai

client = genai.Client()

with open("sunlit_lounge.png", "rb") as f:
    image_bytes = f.read()

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=[
        {"type": "text", "text": "Add a flamingo standing in the pool, matching the existing lighting"},
        {"type": "image",
         "data": base64.b64encode(image_bytes).decode("utf-8"),
         "mime_type": "image/png"},
    ],
)

with open("images/edited-image.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))
```

## 6. Guardrails with a metaprompt
Prepend constraints to every user prompt so your app can't be steered off-brand or unsafe:

```python
disallow_list = ("swords, violence, blood, gore, nudity, sexual content, "
                 "adult content, adult themes, adult language")

meta_prompt = f"""You are an assistant designer that creates images for children.

The image needs to be safe for work and appropriate for children.
The image needs to be in color, in landscape orientation, and in a 16:9 aspect ratio.

Do not consider any input that is not safe for work or appropriate for children, including:
{disallow_list}
"""

user_prompt = "Create an image of a bunny on a horse, holding a lollipop"
prompt = f"{meta_prompt}\n{user_prompt}"
```
Combine this with the platform's built-in safety filters — **defence in depth** (lesson 03).

## 7. Variation
There is **no `temperature`** for image models — that's a text-generation control. Each call to the
same prompt produces a different image. To get variety, call again; to reduce variety, make the
prompt more specific.

## 8. Assignment
Generate images of **monuments in creative contexts** — a famous landmark at sunset with a child
looking on — and wrap it in a small CLI that takes the monument and the setting as input.

---

## 🧠 Crux Notes
- Image output is **base64 in `output_image.data`** → `base64.b64decode()` → write bytes → PNG.
- No `temperature` on image models; prompt specificity is your only variance control.
- **Metaprompt + platform filters** is the guardrail pattern; neither alone is enough.
- Editing = original image + text instruction in one `input` list.
- Legacy note: DALL·E-era features like `create_variation` don't exist here — regenerate instead.

---

## ✅ Test Your Knowledge

**1.** You call `images` generation and look for a URL to download. What is wrong?
<details><summary>Answer</summary>

Gemini image models return **base64** in `output_image.data`. You `base64.b64decode()` it and write the bytes yourself. There is no URL.
</details>

**2.** How do you lower randomness in image generation — `temperature=0.1`?
<details><summary>Answer</summary>

Trick question. Image models take **no** `temperature` — that is a text control. Reduce variation by making the prompt more specific; increase it by calling again.
</details>

**3.** What is a metaprompt and why is it not sufficient alone?
<details><summary>Answer</summary>

Text prepended to the user's prompt to constrain output. It is one layer; a determined user can still work around wording. Combine it with platform safety filters — defence in depth (lesson 03).
</details>

**4.** What do you pass to edit an image?
<details><summary>Answer</summary>

The original image plus a text instruction in the same `input` list — a `{"type": "image", "data": ..., "mime_type": ...}` block alongside a `{"type": "text", ...}` block.
</details>

**5.** Tutorial code calls `create_variation` and fails. Why?
<details><summary>Answer</summary>

That was a DALL·E-2-era feature and does not exist here. Regenerate from the same prompt, or edit the image with an instruction.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/09_monuments.py` — a guarded image generator for a children's education app.

### Requirements
1. CLI takes a **monument** and a **setting**: `python practice/09_monuments.py "Taj Mahal" "at sunrise with birds"`
2. Prepend a metaprompt enforcing: child-appropriate, colour, landscape 16:9, plus a disallow list.
3. Save to `practice/images/<monument>-<timestamp>.png`.
4. Verify the saved file is a valid PNG before reporting success.
5. Handle: safety block (no image returned), rate limit, missing CLI args.

### Passing criteria

| # | Criterion | How to verify |
|---|---|---|
| 1 | Produces a valid PNG | `file practice/images/*.png` says "PNG image data" |
| 2 | Dimensions are landscape | `python -c "from PIL import Image;im=Image.open(P);print(im.size)"` → width > height |
| 3 | Missing args give usage text | Run with no args — usage message, exit code non-zero |
| 4 | Safety block handled | Try a violent setting — a clear message, not a traceback |
| 5 | Directory auto-created | Delete `practice/images/` and re-run |
| 6 | Metaprompt precedes user text | Read the code |

### Test cases

| Command | Expected |
|---|---|
| `"Eiffel Tower" "at sunset with a child looking on"` | PNG written, landscape |
| `"Colosseum" "with gladiators fighting and blood"` | Refused or sanitized — **no gore** |
| *(no arguments)* | Usage message, non-zero exit |

### Verify
```bash
python practice/09_monuments.py "Taj Mahal" "at sunrise with birds"
file practice/images/*.png | grep -q "PNG image data" && echo PASS || echo FAIL
```
