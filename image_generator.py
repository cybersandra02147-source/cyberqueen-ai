import os
import requests
from dotenv import load_dotenv

load_dotenv()

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"


def generate_logo(prompt, output_path):
    if not STABILITY_API_KEY:
        raise RuntimeError(
            "STABILITY_API_KEY is not configured."
        )

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*",
    }

    data = {
        "prompt": (
            f"Professional business logo for: {prompt}. "
            "Clean modern logo, simple memorable design, "
            "professional branding, centered composition, "
            "no mockup, no photograph."
        ),
        "output_format": "jpeg",
    }

    response = requests.post(
        API_URL,
        headers=headers,
        files={
            "none": ""
        },
        data=data,
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Stability API error {response.status_code}: "
            f"{response.text[:500]}"
        )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(output_path, "wb") as file:
        file.write(response.content)

    return output_path
