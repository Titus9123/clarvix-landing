"""
Lead Generation Workflow — Orquestador principal
================================================
Flujo completo:
  1. Recibe ICP del admin panel (después del PERMISO de Albert)
  2. Llama a Apollo para buscar contactos
  3. LLM (Groq) puntúa y filtra los mejores leads
  4. Retorna lista lista para entregar al cliente

Solo se ejecuta cuando Albert hace click en "Run Agent" en el admin panel.
"""
import csv
import io
import logging
from datetime import datetime

from .apollo_search import ApolloSearchAgent, ApolloSearchParams
from .llm_scorer import LLMScorerAgent, ScoredLead

logger = logging.getLogger(__name__)


class LeadGenJobInput:
    def __init__(
        self,
        client_name: str,
        icp_description: str,
        titles: list[str],
        industries: list[str],
        locations: list[str],
        employee_ranges: list[str] | None = None,
        leads_requested: int = 10,
        min_score: int = 40,
    ):
        self.client_name = client_name
        self.icp_description = icp_description
        self.titles = titles
        self.industries = industries
        self.locations = locations
        self.employee_ranges = employee_ranges or ["1,10", "11,50"]
        self.leads_requested = leads_requested
        self.min_score = min_score


class LeadGenResult:
    def __init__(self, leads: list[ScoredLead], job_input: LeadGenJobInput):
        self.leads = leads
        self.total_found = len(leads)
        self.top_leads = [l for l in leads if l.keep and l.score >= job_input.min_score]
        self.generated_at = datetime.now().isoformat()
        self.client_name = job_input.client_name

    def to_csv(self) -> str:
        """Export top leads to CSV for client delivery."""
        output = io.StringIO()
        fieldnames = [
            "Score", "First Name", "Last Name", "Title", "Company",
            "Website", "Email", "LinkedIn", "City", "Country",
            "Employees", "Notes"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for lead in self.top_leads:
            writer.writerow({
                "Score": lead.score,
                "First Name": lead.first_name,
                "Last Name": lead.last_name,
                "Title": lead.title,
                "Company": lead.company,
                "Website": lead.company_website,
                "Email": lead.email,
                "LinkedIn": lead.linkedin_url,
                "City": lead.city,
                "Country": lead.country,
                "Employees": lead.employee_count,
                "Notes": lead.enrichment_notes,
            })
        return output.getvalue()

    def summary(self) -> dict:
        return {
            "client": self.client_name,
            "generated_at": self.generated_at,
            "total_searched": self.total_found,
            "qualified_leads": len(self.top_leads),
            "avg_score": round(
                sum(l.score for l in self.top_leads) / len(self.top_leads), 1
            ) if self.top_leads else 0,
            "top_lead": (
                f"{self.top_leads[0].first_name} {self.top_leads[0].last_name} "
                f"@ {self.top_leads[0].company} ({self.top_leads[0].score}/100)"
            ) if self.top_leads else "None",
        }


class LeadGenWorkflow:
    """
    Orquesta el flujo completo de generación de leads.
    Se ejecuta SOLO con aprobación explícita de Albert.
    """

    def __init__(self):
        self.apollo = ApolloSearchAgent()
        self.scorer = LLMScorerAgent()

    def run(self, job: LeadGenJobInput) -> LeadGenResult:
        """
        Ejecuta el workflow completo. Requiere permiso explícito.
        """
        logger.info(f"[LeadGen] Starting job for client: {job.client_name}")
        logger.info(f"[LeadGen] ICP: {job.icp_description}")

        # Step 1: Search Apollo
        logger.info("[LeadGen] Step 1: Searching Apollo...")
        search_params = ApolloSearchParams(
            titles=job.titles,
            industries=job.industries,
            locations=job.locations,
            employee_ranges=job.employee_ranges,
            per_page=min(job.leads_requested * 3, 50),  # Get 3x to have room to filter
        )
        raw_contacts = self.apollo.search(search_params)
        logger.info(f"[LeadGen] Apollo returned {len(raw_contacts)} raw contacts")

        if not raw_contacts:
            logger.warning("[LeadGen] No contacts found. Check ICP filters.")
            return LeadGenResult(leads=[], job_input=job)

        # Step 2: LLM scoring
        logger.info("[LeadGen] Step 2: Scoring with Groq LLM...")
        scored_leads = self.scorer.score_batch(
            contacts=raw_contacts,
            icp_description=job.icp_description,
            client_name=job.client_name,
        )

        # Step 3: Filter to requested count
        qualified = [l for l in scored_leads if l.keep and l.score >= job.min_score]
        final_leads = qualified[:job.leads_requested]

        logger.info(
            f"[LeadGen] Done. {len(raw_contacts)} found → "
            f"{len(qualified)} qualified → {len(final_leads)} delivered"
        )

        return LeadGenResult(leads=final_leads, job_input=job)
