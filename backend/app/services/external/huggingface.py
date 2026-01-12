import asyncio
from typing import Any, Dict, List

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.services.cache_service import cache_service

logger = get_logger()


class HuggingFaceService:
    """
    Hugging Face Inference API service for text classification.
    
    Model: valhalla/distilbart-mnli-12-3 (zero-shot classification)
    - Switchable via MODEL_NAME env var
    - Timeout: 30s (configurable via AI_REQUEST_TIMEOUT)
    - Retry: 3 tentativas com exponential backoff
    - Fallback: retorna None para fallback manual no serviço de recomendação
    
    Cache: TTL 24h (classificações não mudam para mesmo input)
    """

    def __init__(self):
        self.base_url = settings.HUGGINGFACE_BASE_URL
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.model_name = settings.MODEL_NAME
        self.timeout = settings.AI_REQUEST_TIMEOUT
        self.max_retries = settings.AI_RETRY_MAX_ATTEMPTS
        self.backoff_factor = settings.AI_RETRY_BACKOFF_FACTOR

    async def classify_text(
        self,
        text: str,
        candidate_labels: List[str],
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Classify text using zero-shot classification.
        
        Args:
            text: Text to classify
            candidate_labels: List of possible labels
            use_cache: Whether to use cache
            
        Returns:
            Classification results with labels and scores
            Returns None if all retries fail (triggers fallback)
        """
        # Check cache
        if use_cache:
            cache_key = f"huggingface:classify:{self.model_name}:{hash(text)}:{hash(tuple(candidate_labels))}"
            cached_result = cache_service.get(cache_key)
            if cached_result:
                logger.info("Hugging Face classification cache HIT")
                return cached_result

        logger.info("Hugging Face classification cache MISS, calling API")

        # Prepare payload for zero-shot classification
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": candidate_labels,
                "multi_label": True,  # Permite múltiplos labels
            },
        }

        # Retry with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/{self.model_name}",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json=payload,
                        timeout=self.timeout,
                    )
                    response.raise_for_status()
                    data = response.json()

                # Success - cache and return
                if use_cache:
                    cache_service.set(cache_key, data)
                
                logger.info(f"Hugging Face API success on attempt {attempt}")
                return data

            except httpx.TimeoutException:
                wait_time = self.backoff_factor ** (attempt - 1)
                logger.warning(
                    f"Hugging Face API timeout on attempt {attempt}/{self.max_retries}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Hugging Face API: All retry attempts exhausted (timeout)")
                    return None

            except httpx.HTTPError as e:
                wait_time = self.backoff_factor ** (attempt - 1)
                logger.warning(
                    f"Hugging Face API error on attempt {attempt}/{self.max_retries}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Hugging Face API: All retry attempts exhausted: {e}")
                    return None

        return None

    async def classify_book_genre(
        self,
        description: str,
        title: str = "",
    ) -> Dict[str, Any]:
        """
        Classify book into game-relevant genres.
        
        Args:
            description: Book description
            title: Book title (optional, helps context)
            
        Returns:
            Classification results or None for fallback
        """
        # Combine title and description for better context
        text = f"{title}. {description}" if title else description
        
        # Genres relevantes para mapeamento com jogos
        candidate_labels = [
            "fantasy",
            "science fiction",
            "adventure",
            "mystery",
            "thriller",
            "horror",
            "romance",
            "historical",
            "action",
            "drama",
            "comedy",
            "dystopian",
            "post-apocalyptic",
            "superhero",
            "crime",
            "war",
            "magic",
            "dark",
            "epic",
        ]

        result = await self.classify_text(text, candidate_labels)
        
        if result is None:
            logger.warning("Hugging Face classification failed, will use manual fallback")
        
        return result

    def parse_classification_result(
        self,
        result: Dict[str, Any],
        threshold: float = 0.3,
    ) -> List[Dict[str, float]]:
        """
        Parse classification result and filter by threshold.
        
        Args:
            result: Raw classification result from API
            threshold: Minimum score threshold
            
        Returns:
            List of labels with scores above threshold
        """
        if not result or "labels" not in result:
            return []

        labels = result.get("labels", [])
        scores = result.get("scores", [])

        filtered = [
            {"label": label, "score": round(score, 2)}
            for label, score in zip(labels, scores)
            if score >= threshold
        ]

        return filtered

    async def generate_text_with_llama(
        self,
        prompt: str,
        max_tokens: int = 150,
        use_cache: bool = True,
    ) -> str:
        """
        Gera texto usando Llama 3.1 8B Instruct via Chat Completions API.
        
        Args:
            prompt: Prompt de instrução
            max_tokens: Máximo de tokens a gerar
            use_cache: Se deve usar cache
            
        Returns:
            Texto gerado ou None se falhar
        """
        # Check cache
        if use_cache:
            cache_key = f"llama:generate:{hash(prompt)}:{max_tokens}"
            cached_result = cache_service.get(cache_key)
            if cached_result:
                logger.info("Llama text generation cache HIT")
                return cached_result

        logger.info("Llama text generation cache MISS, calling API")

        # Payload para Chat Completions (novo formato)
        payload = {
            "model": settings.TEXT_GENERATION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        # Retry with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                url = "https://router.huggingface.co/v1/chat/completions"
                logger.info(f"[Llama API] Attempt {attempt}/{self.max_retries} - POST {url}")
                logger.info(f"[Llama API] Model: {settings.TEXT_GENERATION_MODEL}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json=payload,
                        timeout=self.timeout,
                    )
                    
                    logger.info(f"[Llama API] Status Code: {response.status_code}")
                    
                    response.raise_for_status()
                    data = response.json()

                # Extract generated text from chat completions format
                generated_text = ""
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    generated_text = message.get("content", "").strip()

                logger.info(f"[Llama API] Extracted text length: {len(generated_text)} chars")

                # Success - cache and return
                if use_cache and generated_text:
                    cache_service.set(cache_key, generated_text)
                
                logger.info(f"[Llama API] SUCCESS on attempt {attempt}")
                return generated_text

            except httpx.TimeoutException:
                wait_time = self.backoff_factor ** (attempt - 1)
                logger.warning(
                    f"Llama text generation timeout on attempt {attempt}/{self.max_retries}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Llama text generation: All retry attempts exhausted (timeout)")
                    return None

            except httpx.HTTPError as e:
                wait_time = self.backoff_factor ** (attempt - 1)
                logger.warning(
                    f"Llama text generation error on attempt {attempt}/{self.max_retries}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Llama text generation: All retry attempts exhausted: {e}")
                    return None

        return None


# Singleton instance
huggingface_service = HuggingFaceService()
