from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import date, datetime

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
class LoginIn(BaseModel):
    username: str
    password: str

class ProjectBase(BaseModel):
    name: str
    objective: str = ''
    status: str = 'active'
    priority: str = 'medium'
    start_date: Optional[date] = None
    target_date: Optional[date] = None
class ProjectCreate(ProjectBase): pass
class ProjectOut(ProjectBase):
    model_config=ConfigDict(from_attributes=True)
    id:int

class TaskBase(BaseModel):
    title: str
    description: str = ''
    status: str = 'backlog'
    priority: str = 'medium'
    due_date: Optional[date]=None
    project_id: Optional[int]=None
class TaskCreate(TaskBase): pass
class TaskOut(TaskBase):
    model_config=ConfigDict(from_attributes=True)
    id:int

class OpportunityBase(BaseModel):
    company:str
    role:str
    salary:str=''
    status:str='found'
    capability_fit:float=0
    evidence_fit:float=0
    resume_fit:float=0
    interview_fit:float=0
    notes:str=''
class OpportunityCreate(OpportunityBase): pass
class OpportunityOut(OpportunityBase):
    model_config=ConfigDict(from_attributes=True)
    id:int

class CapabilityBase(BaseModel):
    name:str
    description:str=''
    score:float=0
    growth_history:str=''
class CapabilityCreate(CapabilityBase): pass
class CapabilityOut(CapabilityBase):
    model_config=ConfigDict(from_attributes=True)
    id:int

class CapabilityHistoryOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    capability_id:int
    score:float
    note:str
    created_at:datetime

class FGABase(BaseModel):
    name:str
    goal:str=''
    outcome:str=''
    completed:bool=False
    evidence_generated:bool=False
    portfolio_value:str=''
    reflection:str=''
    capability_id:Optional[int]=None
class FGACreate(FGABase): pass
class FGAOut(FGABase):
    model_config=ConfigDict(from_attributes=True)
    id:int

class EvidenceBase(BaseModel):
    title:str
    evidence_type:str='artifact'
    summary:str=''
    tags:str=''
    source:str='manual'
    resume_bullet_draft:str=''
    interview_story_draft:str=''
    star_story_draft:str=''
    evidence_score:float=0
    completeness_notes:str=''
class EvidenceCreate(EvidenceBase):
    capability_ids:List[int]=Field(default_factory=list)
    project_ids:List[int]=Field(default_factory=list)
    task_ids:List[int]=Field(default_factory=list)
    fga_ids:List[int]=Field(default_factory=list)
    opportunity_ids:List[int]=Field(default_factory=list)
class EvidenceOut(EvidenceBase):
    model_config=ConfigDict(from_attributes=True)
    id:int
    file_path:Optional[str]=None
    created_at:datetime

class EvidenceLinksIn(BaseModel):
    capability_ids:List[int]=Field(default_factory=list)
    project_ids:List[int]=Field(default_factory=list)
    task_ids:List[int]=Field(default_factory=list)
    fga_ids:List[int]=Field(default_factory=list)
    opportunity_ids:List[int]=Field(default_factory=list)

class AIItemBase(BaseModel):
    title:str
    item_type:str='prompt'
    model:str=''
    content:str=''
    outcome:str=''
    tags:str=''
class AIItemCreate(AIItemBase): pass
class AIItemOut(AIItemBase):
    model_config=ConfigDict(from_attributes=True)
    id:int
    created_at:datetime

class NoteBase(BaseModel):
    title:str
    note_type:str='note'
    content:str=''
    tags:str=''
class NoteCreate(NoteBase): pass
class NoteOut(NoteBase):
    model_config=ConfigDict(from_attributes=True)
    id:int
    created_at:datetime

class DecisionBase(BaseModel):
    title:str
    decision:str
    rationale:str=''
    consequences:str=''
    review_date:Optional[date]=None
    project_id:Optional[int]=None
class DecisionCreate(DecisionBase): pass
class DecisionOut(DecisionBase):
    model_config=ConfigDict(from_attributes=True)
    id:int
    created_at:datetime

class WeeklyReviewSnapshotCreate(BaseModel):
    title:str='Weekly Review'
    notes:str=''
class WeeklyReviewSnapshotOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    title:str
    completed_work:str
    blockers:str
    evidence_generated:str
    recommended_next_actions:str
    notes:str
    created_at:datetime

class ActivityLogOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    action:str
    entity_type:str
    entity_id:Optional[int]
    summary:str
    created_at:datetime

class SettingIn(BaseModel):
    value:str
class SettingOut(BaseModel):
    key:str
    value:str

class SearchResult(BaseModel):
    module:str
    id:int
    title:str
    summary:str=''
    created_at:Optional[str]=None
