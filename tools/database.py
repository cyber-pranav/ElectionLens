"""
ElectionLens — SQLite database layer (SQLAlchemy).
Handles schema creation, seed-data ingestion, and all CRUD operations.
"""

import json
import os
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column, Float, Integer, String, Text, create_engine
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class Constituency(Base):
    """One row per constituency-year combination."""

    __tablename__ = "constituencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    winner = Column(String(200), nullable=False)
    party = Column(String(50), nullable=False, index=True)
    votes = Column(Integer, nullable=False)
    runner_up = Column(String(200), nullable=False)
    runner_up_party = Column(String(50), nullable=False)
    runner_up_votes = Column(Integer, nullable=False)
    margin = Column(Integer, nullable=False)
    turnout_percent = Column(Float, nullable=False)
    total_voters = Column(Integer, nullable=False)
    nota_votes = Column(Integer, default=0)
    year = Column(Integer, nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "winner": self.winner,
            "party": self.party,
            "votes": self.votes,
            "runner_up": self.runner_up,
            "runner_up_party": self.runner_up_party,
            "runner_up_votes": self.runner_up_votes,
            "margin": self.margin,
            "turnout_percent": self.turnout_percent,
            "total_voters": self.total_voters,
            "nota_votes": self.nota_votes,
            "year": self.year,
        }


class Alert(Base):
    """Monitoring alerts persisted by the MonitoringAgent."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    constituency = Column(String(200), nullable=False)
    state = Column(String(100), nullable=False)
    alert_type = Column(String(50), nullable=False)  # anomaly | close_contest | recount_risk
    severity = Column(String(20), nullable=False)     # INFO | WARNING | CRITICAL
    message = Column(Text, nullable=False)
    year = Column(Integer, default=2024)


# ---------------------------------------------------------------------------
# Engine / Session factory
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).resolve().parent.parent
_DB_PATH = _BASE_DIR / "data" / "elections.db"

_engine = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
_SessionLocal = sessionmaker(bind=_engine)


def get_session() -> Session:
    """Return a new SQLAlchemy session."""
    return _SessionLocal()


# ---------------------------------------------------------------------------
# Schema + Seed
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create tables and seed from sample_elections.json if empty."""
    os.makedirs(_BASE_DIR / "data", exist_ok=True)
    Base.metadata.create_all(_engine)

    session = get_session()
    try:
        if session.query(Constituency).count() == 0:
            _seed_from_json(session)
    finally:
        session.close()


def _seed_from_json(session: Session) -> None:
    json_path = _BASE_DIR / "data" / "sample_elections.json"
    if not json_path.exists():
        return
    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    for row in data.get("constituencies", []):
        session.add(Constituency(
            name=row["name"],
            state=row["state"],
            winner=row["winner"],
            party=row["party"],
            votes=row["votes"],
            runner_up=row["runner_up"],
            runner_up_party=row["runner_up_party"],
            runner_up_votes=row["runner_up_votes"],
            margin=row["margin"],
            turnout_percent=row["turnout_percent"],
            total_voters=row["total_voters"],
            nota_votes=row.get("nota_votes", 0),
            year=row["year"],
        ))
    session.commit()


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_all_constituencies(year: int = 2024) -> list[dict]:
    """Return every constituency for a given year."""
    session = get_session()
    try:
        rows = session.query(Constituency).filter_by(year=year).all()
        return [r.to_dict() for r in rows]
    finally:
        session.close()


def get_constituency(name: str, year: int = 2024) -> Optional[dict]:
    """Lookup a single constituency by name (case-insensitive)."""
    session = get_session()
    try:
        row = (
            session.query(Constituency)
            .filter(Constituency.name.ilike(name), Constituency.year == year)
            .first()
        )
        return row.to_dict() if row else None
    finally:
        session.close()


def get_constituencies_by_state(state: str, year: int = 2024) -> list[dict]:
    """Return all constituencies in a state."""
    session = get_session()
    try:
        rows = (
            session.query(Constituency)
            .filter(Constituency.state.ilike(f"%{state}%"), Constituency.year == year)
            .all()
        )
        return [r.to_dict() for r in rows]
    finally:
        session.close()


def get_constituencies_by_party(party: str, year: int = 2024) -> list[dict]:
    """Return all constituencies won by a party."""
    session = get_session()
    try:
        rows = (
            session.query(Constituency)
            .filter(Constituency.party.ilike(f"%{party}%"), Constituency.year == year)
            .all()
        )
        return [r.to_dict() for r in rows]
    finally:
        session.close()


def get_all_parties(year: int = 2024) -> list[str]:
    """Return distinct winning-party names."""
    session = get_session()
    try:
        rows = (
            session.query(Constituency.party)
            .filter_by(year=year)
            .distinct()
            .all()
        )
        return sorted([r[0] for r in rows])
    finally:
        session.close()


def get_all_states(year: int = 2024) -> list[str]:
    """Return distinct states."""
    session = get_session()
    try:
        rows = (
            session.query(Constituency.state)
            .filter_by(year=year)
            .distinct()
            .all()
        )
        return sorted([r[0] for r in rows])
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Alert helpers
# ---------------------------------------------------------------------------

def save_alert(constituency: str, state: str, alert_type: str,
               severity: str, message: str, year: int = 2024) -> None:
    session = get_session()
    try:
        session.add(Alert(
            constituency=constituency,
            state=state,
            alert_type=alert_type,
            severity=severity,
            message=message,
            year=year,
        ))
        session.commit()
    finally:
        session.close()


def get_all_alerts() -> list[dict]:
    session = get_session()
    try:
        rows = session.query(Alert).all()
        return [
            {
                "id": r.id,
                "constituency": r.constituency,
                "state": r.state,
                "alert_type": r.alert_type,
                "severity": r.severity,
                "message": r.message,
                "year": r.year,
            }
            for r in rows
        ]
    finally:
        session.close()


def clear_alerts() -> None:
    session = get_session()
    try:
        session.query(Alert).delete()
        session.commit()
    finally:
        session.close()
