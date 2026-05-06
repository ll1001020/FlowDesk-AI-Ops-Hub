from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent import OpsAgent, classify_issue
from app.config import get_settings
from app.db import TicketStore
from app.providers import build_provider
from app.rag import KnowledgeBase
from app.schemas import AssistRequest, AssistResponse, Ticket, TicketCreate

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@lru_cache
def get_kb() -> KnowledgeBase:
    return KnowledgeBase(settings.knowledge_path)


@lru_cache
def get_agent() -> OpsAgent:
    return OpsAgent(get_kb(), build_provider(settings))


@lru_cache
def get_store() -> TicketStore:
    return TicketStore(settings.database_url)


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"ok": True, "provider": settings.llm_provider, "knowledge_chunks": len(get_kb().chunks)}


@app.post("/api/assist", response_model=AssistResponse)
def assist(payload: AssistRequest):
    return get_agent().assist(payload.question, payload.scenario)


@app.post("/api/tickets", response_model=Ticket)
def create_ticket(payload: TicketCreate):
    assist_result = get_agent().assist(payload.description, payload.scenario)
    return get_store().create_ticket(
        title=payload.title,
        description=payload.description,
        scenario=payload.scenario,
        severity=assist_result.severity,
        owner_team=assist_result.owner_team,
        ai_summary=assist_result.answer,
    )


@app.get("/api/tickets", response_model=list[Ticket])
def list_tickets(limit: int = 50):
    return get_store().list_tickets(limit=limit)


@app.patch("/api/tickets/{ticket_id}/status", response_model=Ticket)
def update_status(ticket_id: int, status: str):
    ticket = get_store().update_status(ticket_id, status)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.get("/api/classify")
def classify(text: str, scenario: str = "general"):
    severity, owner_team, sla = classify_issue(text, scenario)
    return {"severity": severity, "owner_team": owner_team, "suggested_sla": sla}
