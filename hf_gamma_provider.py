import os
from huggingface_hub import InferenceClient
from typing import Optional, Dict, Any

class HuggingFaceGammaProvider:
    """
    Provider za Gamma model hostovan na Hugging Face-u.
    Integrisano sa ModelRouter-om za fallback i 429 handling.
    """
    
    def __init__(self, model_id: str = "google/gemma-2-9b", token: Optional[str] = None):
        # Koristi token iz okruženja ako nije prosleđen
        self.token = token or os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError("HF_TOKEN nije pronađen u environment varijablama.")
            
        self.model_id = model_id
        self.client = InferenceClient(model=self.model_id, token=self.token)

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generiše odgovor koristeći HF API. 
        Ovdje bi ModelRouter trebao da uhvati 429 grešku.
        """
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                stop_sequences=["\n\n"], # Primer stop sekvence
                return_full_text=False
            )
            return response.strip()
        except Exception as e:
            # Ako dobijemo 429 (Rate Limit), prosleđujemo grešku ruteru
            if "429" in str(e):
                print(f"[HF_PROVIDER] Rate limit hit for {self.model_id}. Triggering fallback...")
            raise e

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "huggingface",
            "model_id": self.model_id,
            "status": "active"
        }