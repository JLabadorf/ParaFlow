import base64
import os
from google import genai
from google.genai import types


def generate(api_key, input_text, system_instruction):
    client = genai.Client(
        api_key=os.environ.get(api_key),
    )

    model = "gemini-2.0-flash-thinking-exp-01-21"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=64,
        max_output_tokens=65536,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=system_instruction),
        ],
    )
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
