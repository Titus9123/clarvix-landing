"""
Apollo.io Search Agent
Busca contactos usando la API de Apollo con los filtros del ICP del cliente.
Solo corre cuando Albert da permiso explícito desde el admin panel.
"""
import os
import httpx
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

APOLLO_BASE_URL = "https://api.apollo.io/api/v1"


class ApolloSearchParams(BaseModel):
    titles: list[str] = Field(description="Decision-maker titles, e.g. ['CEO', 'Owner']")
    industries: list[str] = Field(description="Target industries, e.g. ['Real Estate', 'Restaurants']")
    locations: list[str] = Field(description="Countries or cities, e.g. ['Mexico', 'Israel']")
    employee_ranges: list[str] = Field(
        default=["1,10", "11,50"],
        description="Employee count ranges e.g. ['1,10', '11,50']"
    )
    per_page: int = Field(default=10, ge=1, le=50)


class ApolloContact(BaseModel):
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    company: str = ""
    company_website: str = ""
    email: str = ""
    linkedin_url: str = ""
    city: str = ""
    country: str = ""
    employee_count: str = ""


class ApolloSearchAgent:
    """
    Llama a Apollo API para buscar leads según el ICP.
    Requiere APOLLO_API_KEY en .env
    """

    def __init__(self):
        self.api_key = os.getenv("APOLLO_API_KEY", "")
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY no está configurado en .env")

    def search(self, params: ApolloSearchParams) -> list[ApolloContact]:
        """
        Busca contactos en Apollo y retorna lista de leads.
        """
        logger.info(f"Apollo search: {params.titles} in {params.industries} @ {params.locations}")

        # Build the person_titles filter
        payload = {
            "api_key": self.api_key,
            "page": 1,
            "per_page": params.per_page,
            "person_titles": params.titles,
            "organization_industry_tag_ids": [],
            "person_locations": params.locations,
            "contact_email_status": ["verified", "likely to engage"],
        }

        # Add industry keywords if provided
        if params.industries:
            payload["q_keywords"] = " OR ".join(params.industries)

        # Add employee ranges
        if params.employee_ranges:
            payload["organization_num_employees_ranges"] = params.employee_ranges

        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    f"{APOLLO_BASE_URL}/mixed_people/search",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache",
                    }
                )
                response.raise_for_status()
                data = response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Apollo API error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Apollo API error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Apollo connection error: {e}")
            raise RuntimeError(f"Apollo connection error: {e}")

        contacts = []
        for person in data.get("people", []):
            org = person.get("organization") or {}
            contact = ApolloContact(
                first_name=person.get("first_name") or "",
                last_name=person.get("last_name") or "",
                title=person.get("title") or "",
                company=org.get("name") or person.get("organization_name") or "",
                company_website=org.get("website_url") or "",
                email=person.get("email") or "",
                linkedin_url=person.get("linkedin_url") or "",
                city=person.get("city") or "",
                country=person.get("country") or "",
                employee_count=str(org.get("estimated_num_employees") or ""),
            )
            contacts.append(contact)

        logger.info(f"Apollo returned {len(contacts)} contacts")
        return contacts
