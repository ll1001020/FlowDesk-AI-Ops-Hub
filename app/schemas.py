from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AssistRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    scenario: str = Field(default="general", description="retail_ops | ecommerce_support | campus_ops | device_inspection | general")


class Citation(BaseModel):
    source: str
    section: str
    score: float
    content: str


class AssistResponse(BaseModel):
    answer: str
    severity: str
    owner_team: str
    suggested_sla: str
    checklist: List[str]
    citations: List[Citation]


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=2, max_length=5000)
    scenario: str = "general"


class Ticket(BaseModel):
    id: int
    title: str
    description: str
    scenario: str
    severity: str
    status: str
    owner_team: str
    ai_summary: str
    created_at: datetime
