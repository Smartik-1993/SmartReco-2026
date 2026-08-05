# app/core/mesh_client.py
import os
from openai import OpenAI


class MeshClient:

    def __init__(self):
        # Ensure base_url matches Mesh API's base endpoint specification
        self.api_key = os.getenv("MESH_API_KEY", "your_mesh_api_key")
        self.base_url = os.getenv(
            "MESH_API_BASE_URL", "https://api.meshapi.ai/v1"
        )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def get_embedding(self, text: str) -> list[float]:
        """Generates text vector embeddings via Mesh API (or falls back gracefully)."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # Mesh API embedding model
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            print(
                f"⚠️ Mesh API embedding failed ({e}). Returning fallback vector."
            )
            # Fallback zero vector (1536 dimensions for similarity matching)
            return [0.0] * 1536

    def generate_recommendation(
        self, prompt: str, model: str = "qwen-2.5-72b-instruct"
    ) -> str:
        """Generates chat completion narrative via Mesh API."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are SmartReco, an AI recommendation engine.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=250,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Mesh API Chat Completion failed: {e}")
            return f"Recommended resources based on your recent activity: {prompt}"


# Module-level instance expected by dual_write and scheduler
mesh_client = MeshClient()