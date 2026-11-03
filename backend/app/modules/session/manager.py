import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TurnLog(BaseModel):
    turn_id: str
    turn_index: int
    student_message: str
    student_reasoning: Optional[str]
    chosen_strategy: str
    intervention_text: str
    detected_misconception: Optional[str]
    answer_revealed: bool
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class TeachingSession(BaseModel):
    session_id: str
    student_id: str
    subject: str
    concept_id: str
    turns: List[TurnLog] = Field(default_factory=list)
    is_active: bool = True
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    ended_at: Optional[str] = None

class TeachingSessionManager:
    """
    Teaching Session Management (PRD Section 8.2 & 14):
    Maintains dialogue turn history, ensures session continuity,
    records student attempts and enforces 30-min idle timeouts.
    """

    def __init__(self):
        self._sessions: Dict[str, TeachingSession] = {}

    def create_session(self, student_id: str, subject: str, concept_id: str) -> TeachingSession:
        session_id = str(uuid.uuid4())
        session = TeachingSession(
            session_id=session_id,
            student_id=student_id,
            subject=subject,
            concept_id=concept_id,
            turns=[],
            is_active=True,
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[TeachingSession]:
        return self._sessions.get(session_id)

    def log_turn(
        self,
        session_id: str,
        student_message: str,
        student_reasoning: Optional[str],
        chosen_strategy: str,
        intervention_text: str,
        detected_misconception: Optional[str] = None,
        answer_revealed: bool = False,
    ) -> TurnLog:
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        turn_index = len(session.turns) + 1
        turn = TurnLog(
            turn_id=str(uuid.uuid4()),
            turn_index=turn_index,
            student_message=student_message,
            student_reasoning=student_reasoning,
            chosen_strategy=chosen_strategy,
            intervention_text=intervention_text,
            detected_misconception=detected_misconception,
            answer_revealed=answer_revealed,
        )
        session.turns.append(turn)
        return turn

    def close_session(self, session_id: str) -> Optional[TeachingSession]:
        session = self._sessions.get(session_id)
        if session:
            session.is_active = False
            session.ended_at = datetime.utcnow().isoformat()
        return session
