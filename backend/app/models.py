from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Table, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

evidence_capabilities = Table('evidence_capabilities', Base.metadata, Column('evidence_id', ForeignKey('evidence_items.id'), primary_key=True), Column('capability_id', ForeignKey('capabilities.id'), primary_key=True))
evidence_projects = Table('evidence_projects', Base.metadata, Column('evidence_id', ForeignKey('evidence_items.id'), primary_key=True), Column('project_id', ForeignKey('projects.id'), primary_key=True))
evidence_tasks = Table('evidence_tasks', Base.metadata, Column('evidence_id', ForeignKey('evidence_items.id'), primary_key=True), Column('task_id', ForeignKey('tasks.id'), primary_key=True))
evidence_fgas = Table('evidence_fgas', Base.metadata, Column('evidence_id', ForeignKey('evidence_items.id'), primary_key=True), Column('fga_id', ForeignKey('fgas.id'), primary_key=True))
evidence_opportunities = Table('evidence_opportunities', Base.metadata, Column('evidence_id', ForeignKey('evidence_items.id'), primary_key=True), Column('opportunity_id', ForeignKey('opportunities.id'), primary_key=True))

class Project(Base):
    __tablename__='projects'
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False, index=True)
    objective=Column(Text, default='')
    status=Column(String, default='active', index=True)
    priority=Column(String, default='medium')
    start_date=Column(Date, nullable=True)
    target_date=Column(Date, nullable=True)
    tasks=relationship('Task', back_populates='project', cascade='all, delete-orphan')
    decisions=relationship('Decision', back_populates='project')
    evidence=relationship('EvidenceItem', secondary=evidence_projects, back_populates='projects')

class Task(Base):
    __tablename__='tasks'
    id=Column(Integer, primary_key=True)
    title=Column(String, nullable=False, index=True)
    description=Column(Text, default='')
    status=Column(String, default='backlog', index=True)
    priority=Column(String, default='medium')
    due_date=Column(Date, nullable=True)
    project_id=Column(Integer, ForeignKey('projects.id'), nullable=True)
    project=relationship('Project', back_populates='tasks')
    evidence=relationship('EvidenceItem', secondary=evidence_tasks, back_populates='tasks')

class Opportunity(Base):
    __tablename__='opportunities'
    id=Column(Integer, primary_key=True)
    company=Column(String, nullable=False, index=True)
    role=Column(String, nullable=False)
    salary=Column(String, default='')
    status=Column(String, default='found', index=True)
    capability_fit=Column(Float, default=0)
    evidence_fit=Column(Float, default=0)
    resume_fit=Column(Float, default=0)
    interview_fit=Column(Float, default=0)
    notes=Column(Text, default='')
    evidence=relationship('EvidenceItem', secondary=evidence_opportunities, back_populates='opportunities')

class Capability(Base):
    __tablename__='capabilities'
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False, unique=True, index=True)
    description=Column(Text, default='')
    score=Column(Float, default=0, index=True)
    growth_history=Column(Text, default='')
    evidence=relationship('EvidenceItem', secondary=evidence_capabilities, back_populates='capabilities')
    fgas=relationship('FGA', back_populates='capability')

class CapabilityHistory(Base):
    __tablename__='capability_history'
    id=Column(Integer, primary_key=True)
    capability_id=Column(Integer, ForeignKey('capabilities.id'), nullable=False, index=True)
    score=Column(Float, default=0)
    note=Column(Text, default='')
    created_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)

class FGA(Base):
    __tablename__='fgas'
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False, index=True)
    goal=Column(Text, default='')
    outcome=Column(Text, default='')
    completed=Column(Boolean, default=False, index=True)
    evidence_generated=Column(Boolean, default=False)
    portfolio_value=Column(String, default='')
    reflection=Column(Text, default='')
    capability_id=Column(Integer, ForeignKey('capabilities.id'), nullable=True)
    capability=relationship('Capability', back_populates='fgas')
    evidence=relationship('EvidenceItem', secondary=evidence_fgas, back_populates='fgas')

class EvidenceItem(Base):
    __tablename__='evidence_items'
    id=Column(Integer, primary_key=True)
    title=Column(String, nullable=False, index=True)
    evidence_type=Column(String, default='artifact')
    summary=Column(Text, default='')
    tags=Column(String, default='')
    file_path=Column(String, nullable=True)
    source=Column(String, default='manual')
    resume_bullet_draft=Column(Text, default='')
    interview_story_draft=Column(Text, default='')
    star_story_draft=Column(Text, default='')
    evidence_score=Column(Float, default=0)
    completeness_notes=Column(Text, default='')
    created_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)
    capabilities=relationship('Capability', secondary=evidence_capabilities, back_populates='evidence')
    projects=relationship('Project', secondary=evidence_projects, back_populates='evidence')
    tasks=relationship('Task', secondary=evidence_tasks, back_populates='evidence')
    fgas=relationship('FGA', secondary=evidence_fgas, back_populates='evidence')
    opportunities=relationship('Opportunity', secondary=evidence_opportunities, back_populates='evidence')

class AIItem(Base):
    __tablename__='ai_items'
    id=Column(Integer, primary_key=True)
    title=Column(String, nullable=False)
    item_type=Column(String, default='prompt')
    model=Column(String, default='')
    content=Column(Text, default='')
    outcome=Column(Text, default='')
    tags=Column(String, default='')
    created_at=Column(DateTime(timezone=True), server_default=func.now())

class Note(Base):
    __tablename__='notes'
    id=Column(Integer, primary_key=True)
    title=Column(String, nullable=False, index=True)
    note_type=Column(String, default='note')
    content=Column(Text, default='')
    tags=Column(String, default='', index=True)
    created_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)

class Decision(Base):
    __tablename__='decisions'
    id=Column(Integer, primary_key=True)
    title=Column(String, nullable=False)
    decision=Column(Text, nullable=False)
    rationale=Column(Text, default='')
    consequences=Column(Text, default='')
    review_date=Column(Date, nullable=True)
    project_id=Column(Integer, ForeignKey('projects.id'), nullable=True)
    project=relationship('Project', back_populates='decisions')
    created_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)

class WeeklyReviewSnapshot(Base):
    __tablename__='weekly_review_snapshots'
    id=Column(Integer, primary_key=True)
    title=Column(String, nullable=False)
    completed_work=Column(Text, default='')
    blockers=Column(Text, default='')
    evidence_generated=Column(Text, default='')
    recommended_next_actions=Column(Text, default='')
    notes=Column(Text, default='')
    created_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)

class ActivityLog(Base):
    __tablename__='activity_logs'
    id=Column(Integer, primary_key=True)
    action=Column(String, nullable=False, index=True)
    entity_type=Column(String, nullable=False, index=True)
    entity_id=Column(Integer, nullable=True)
    summary=Column(Text, default='')
    created_at=Column(DateTime(timezone=True), server_default=func.now(), index=True)

class Setting(Base):
    __tablename__='settings'
    id=Column(Integer, primary_key=True)
    key=Column(String, nullable=False, unique=True, index=True)
    value=Column(Text, default='')
    updated_at=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
