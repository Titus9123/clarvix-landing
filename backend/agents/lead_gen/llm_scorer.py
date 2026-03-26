"""
LLM Scoring Agent (Groq / OpenRouter)
Usa un LLM para filtrar, enriquecer y puntuar cada lead según el ICP del cliente.
Solo runs después del permiso de Albert.
"""
import os
import json
import logging
from groq import Groq
from .apollo_search import ApolloContact

logger = logging.getLogger(__name__)


class ScoredLead(ApolloContact):
    score: int = 0           # 0-100
    score_reason: str = ""
    keep: bool = True
    enrichment_notes: str = ""


class LLMScorerAgent:
    """
    Dado un ICP y lista de contactos de Apollo,
    usa Groq LLM para puntuar y filtrar los mejores leads.
    """

    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not self.groq_key:
            raise ValueError("GROQ_API_KEY no está configurado en .env")

        self.client = Groq(api_key=self.groq_key)

    def score_batch(
        self,
        contacts: list[ApolloContact],
        icp_description: str,
        client_name: str,
    ) -> list[ScoredLead]:
        """
        Puntúa cada contacto del 0-100 según qué tan bien encaja con el ICP.
        Procesa en batches de 5 para no sobrecargar el contexto.
        """
        if not contacts:
            return []

        scored: list[ScoredLead] = []
        batch_size = 5

        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i + batch_size]
            batch_scored = self._score_batch(batch, icp_description, client_name)
            scored.extend(batch_scored)

        # Sort by score descending
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored

    def _score_batch(
        self,
        contacts: list[ApolloContact],
        icp_description: str,
        client_name: str,
    ) -> list[ScoredLead]:

        contacts_json = json.dumps([c.model_dump() for c in contacts], indent=2)

        prompt = f"""You are a B2B lead qualification expert for Clarvix, a digital agency.

CLIENT: {client_name}
IDEAL CUSTOMER PROFILE (ICP): {icp_description}

CONTACTS FROM APOLLO:
{contacts_json}

For each contact, return a JSON array with this exact structure:
[
  {{
    "index": 0,
    "score": 85,
    "keep": true,
    "score_reason": "CEO of 15-person real estate agency in Mexico - perfect ICP match",
    "enrichment_notes": "High intent signal: growing company, decision maker"
  }},
  ...
]

Scoring criteria:
- 80-100: Perfect ICP match, verified email, clear decision maker
- 60-79: Good match, minor gaps (no email, title slightly off)
- 40-59: Partial match, worth including but lower priority
- 0-39: Poor match, set keep=false

Return ONLY the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000,
            )
            raw = response.choices[0].message.content.strip()

            # Clean up any markdown code blocks
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            scores_data = json.loads(raw)

        except Exception as e:
            logger.error(f"LLM scoring error: {e}. Using default scores.")
            # Fallback: keep all with score 50
            scores_data = [
                {"index": j, "score": 50, "keep": True,
                 "score_reason": "Auto-scored (LLM unavailable)",
                 "enrichment_notes": ""}
                for j in range(len(contacts))
            ]

        results = []
        for j, contact in enumerate(contacts):
            score_info = next((s for s in scores_data if s.get("index") == j), {})
            scored = ScoredLead(
                **contact.model_dump(),
                score=score_info.get("score", 50),
                keep=score_info.get("keep", True),
                score_reason=score_info.get("score_reason", ""),
                enrichment_notes=score_info.get("enrichment_notes", ""),
            )
            results.append(scored)

        return results
