import os
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """
    LLM Client Wrapper supporting OpenAI API (v1.x & v0.x) and fallback structured response generation
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.has_openai = bool(self.api_key and self.api_key.strip())
        self.client = None
        self.is_legacy_openai = False

        if self.has_openai:
            try:
                import openai
                if hasattr(openai, "OpenAI"):
                    self.client = openai.OpenAI(api_key=self.api_key)
                else:
                    openai.api_key = self.api_key
                    self.is_legacy_openai = True
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.has_openai = False

    def generate_json(self, system_prompt: str, user_prompt: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured JSON output using LLM or structured fallback engine.
        """
        if self.has_openai:
            try:
                if not self.is_legacy_openai and self.client:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt + "\nReturn ONLY valid JSON matching the requested structure."},
                            {"role": "user", "content": user_prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.2,
                    )
                    content = response.choices[0].message.content
                    return json.loads(content)
                else:
                    import openai
                    response = openai.ChatCompletion.create(
                        model=self.model if self.model != "gpt-4o-mini" else "gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt + "\nReturn ONLY valid JSON matching the requested structure."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2,
                    )
                    content = response.choices[0]["message"]["content"]
                    return json.loads(content)
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}. Falling back to deterministic engine.")
                return fallback_data
        else:
            logger.info("No OpenAI API key provided. Operating in deterministic AI simulation mode.")
            return fallback_data

llm_client = LLMClient()
