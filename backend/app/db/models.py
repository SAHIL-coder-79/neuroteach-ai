import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Profile & settings
    selected_subjects = Column(JSON, default=list) # e.g. ["python", "dsa", "ai_ml", "mathematics"]
    daily_goal_minutes = Column(Integer, default=20)
    daily_goal_concepts = Column(Integer, default=3)
    streak_days = Column(Integer, default=0)
    last_active_date = Column(DateTime, nullable=True)
    
    sessions = relationship("TutoringSession", back_populates="user", cascade="all, delete-orphan")
    attempts = relationship("StudentAttempt", back_populates="user", cascade="all, delete-orphan")
    misconceptions = relationship("LearnerMisconceptionProfile", back_populates="user", cascade="all, delete-orphan")
    mastery_scores = relationship("ConceptMastery", back_populates="user", cascade="all, delete-orphan")

class TutoringSession(Base):
    __tablename__ = "tutoring_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    summary_json = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="sessions")
    turns = relationship("DialogueTurn", back_populates="session", cascade="all, delete-orphan")

class DialogueTurn(Base):
    __tablename__ = "dialogue_turns"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("tutoring_sessions.id"), nullable=False, index=True)
    turn_index = Column(Integer, nullable=False)
    student_message = Column(Text, nullable=True)
    student_reasoning = Column(Text, nullable=True)
    error_type = Column(String(50), nullable=True) # careless, conceptual, unclear
    misconception_id = Column(String(100), nullable=True)
    strategy_name = Column(String(50), nullable=True) # progressive_hint, step_by_step, etc.
    intervention_text = Column(Text, nullable=False)
    visual_spec = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("TutoringSession", back_populates="turns")

class MisconceptionCatalog(Base):
    __tablename__ = "misconceptions_catalog"
    
    id = Column(String(100), primary_key=True) # e.g. "sign_error_vertex"
    subject = Column(String(50), nullable=False)
    concept_id = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    wrong_rule = Column(Text, nullable=False)
    counterexample = Column(Text, nullable=False)
    root_concepts = Column(JSON, default=list) # e.g. ["quadratic.standard_form"]

class LearnerMisconceptionProfile(Base):
    __tablename__ = "learner_misconceptions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    misconception_id = Column(String(100), ForeignKey("misconceptions_catalog.id"), nullable=False, index=True)
    status = Column(String(50), default="active") # active, improving, resolved, regressed
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    occurrences = Column(Integer, default=1)
    interventions_tried = Column(Integer, default=0)
    resolved_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="misconceptions")

class Concept(Base):
    __tablename__ = "concepts"
    
    id = Column(String(100), primary_key=True) # e.g. "quadratic.vertex"
    subject = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    prerequisites = Column(JSON, default=list) # list of concept_ids
    order_index = Column(Integer, default=0)

class ConceptMastery(Base):
    __tablename__ = "concept_mastery"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    concept_id = Column(String(100), ForeignKey("concepts.id"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0)
    is_mastered = Column(Boolean, default=False)
    evidence_count = Column(Integer, default=0)
    last_assessed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="mastery_scores")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String(100), primary_key=True)
    subject = Column(String(50), nullable=False)
    concept_id = Column(String(100), ForeignKey("concepts.id"), nullable=False, index=True)
    pattern_id = Column(String(100), nullable=True)
    difficulty = Column(String(20), default="medium") # easy, medium, hard
    question_text = Column(Text, nullable=False)
    canonical_answer = Column(String(255), nullable=False)
    visual_spec = Column(JSON, nullable=True)
    hint_ladder = Column(JSON, default=list) # 3 levels of static hints

class StudentAttempt(Base):
    __tablename__ = "student_attempts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String(100), ForeignKey("questions.id"), nullable=False, index=True)
    submitted_answer = Column(String(255), nullable=False)
    reasoning_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    error_type = Column(String(50), nullable=True) # careless, conceptual, unclear
    misconception_id = Column(String(100), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="attempts")

class ModelCallLog(Base):
    __tablename__ = "model_calls"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    input_hash = Column(String(64), nullable=False, index=True)
    model_version = Column(String(100), nullable=False)
    latency_ms = Column(Float, nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    validator_verdicts = Column(JSON, default=dict)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
