from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class NewsItem(BaseModel):
    timestamp: datetime
    title: str
    currency: str
    impact: Literal["low", "medium", "high"]
    source: str


class Decision(BaseModel):
    """Sortie stricte attendue du cerveau LLM (etape 3)."""

    action: Literal["BUY", "SELL", "HOLD"]
    confidence: int = Field(ge=1, le=5)
    reason: str


class RiskVerdict(BaseModel):
    """Sortie du moteur de risque (etape 4) : a le dernier mot sur une Decision."""

    approved: bool
    reason: str
    stop_loss: float | None = None
    position_size: float | None = None
