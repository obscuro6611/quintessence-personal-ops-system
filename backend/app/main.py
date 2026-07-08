from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path
import shutil, uuid, json, csv, zipfile, os, subprocess, sys
from datetime import datetime
from typing import Type
from .config import settings
from .database import Base, engine, get_db
from . import models, schemas
from .auth import authenticate, create_token, current_user

Base.metadata.create_all(bind=engine)
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
Path('backups').mkdir(exist_ok=True)
Path('exports').mkdir(exist_ok=True)

app = FastAPI(title='Quintessence API', version='0.2.0')
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(',')], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def sqlite_safe_migrate():
    # Adds Phase 2 columns if the user already has a Phase 1 SQLite database.
    if not settings.DATABASE_URL.startswith('sqlite'):
        return
    column_specs = [
        ('evidence_items','star_story_draft','TEXT DEFAULT ""'),
        ('evidence_items','evidence_score','FLOAT DEFAULT 0'),
        ('evidence_items','completeness_notes','TEXT DEFAULT ""'),
    ]
    with engine.begin() as conn:
        for table, col, spec in column_specs:
            existing = [r[1] for r in conn.execute(text(f'PRAGMA table_info({table})')).fetchall()]
            if col not in existing:
                conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {col} {spec}'))

sqlite_safe_migrate()

def log_activity(db: Session, action: str, entity_type: str, entity_id=None, summary: str=''):
    db.add(models.ActivityLog(action=action, entity_type=entity_type, entity_id=entity_id, summary=summary[:1000]))
    db.commit()

def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

@app.post('/auth/login', response_model=schemas.Token)
def login(payload: schemas.LoginIn):
    if not authenticate(payload.username, payload.password):
        raise HTTPException(status_code=401, detail='Invalid username or password')
    return schemas.Token(access_token=create_token(payload.username))

def generic_list(model: Type[Base], db: Session):
    return db.query(model).order_by(model.id.desc()).all()

def generic_create(model: Type[Base], payload, db: Session, entity_name: str):
    obj = model(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    log_activity(db, 'created', entity_name, obj.id, getattr(obj, 'title', getattr(obj, 'name', entity_name)))
    return obj

def generic_delete(model: Type[Base], item_id: int, db: Session, entity_name: str):
    obj = db.get(model, item_id)
    if not obj: raise HTTPException(status_code=404, detail='Not found')
    db.delete(obj); db.commit()
    log_activity(db, 'deleted', entity_name, item_id, f'Deleted {entity_name} #{item_id}')
    return {'deleted': item_id}

@app.get('/health')
def health(): return {'status':'ok','app':'Quintessence','version':'0.2.0'}

@app.get('/dashboard', dependencies=[Depends(current_user)])
def dashboard(db: Session=Depends(get_db)):
    return {
        'active_projects': db.query(models.Project).filter(models.Project.status!='complete').count(),
        'active_fgas': db.query(models.FGA).filter(models.FGA.completed==False).count(),
        'opportunities': db.query(models.Opportunity).filter(models.Opportunity.status.notin_(['rejected','offer'])).count(),
        'evidence_generated': db.query(models.EvidenceItem).count(),
        'recent_decisions': db.query(models.Decision).order_by(models.Decision.created_at.desc()).limit(5).all(),
        'recent_evidence': db.query(models.EvidenceItem).order_by(models.EvidenceItem.created_at.desc()).limit(5).all(),
        'blocked_tasks': db.query(models.Task).filter(models.Task.status=='blocked').all(),
        'activity': db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(8).all(),
    }

@app.post('/projects', response_model=schemas.ProjectOut, dependencies=[Depends(current_user)])
def create_project(payload: schemas.ProjectCreate, db: Session=Depends(get_db)): return generic_create(models.Project, payload, db, 'project')
@app.get('/projects', response_model=list[schemas.ProjectOut], dependencies=[Depends(current_user)])
def list_projects(db: Session=Depends(get_db)): return generic_list(models.Project, db)
@app.delete('/projects/{item_id}', dependencies=[Depends(current_user)])
def delete_project(item_id:int, db: Session=Depends(get_db)): return generic_delete(models.Project, item_id, db, 'project')

@app.post('/tasks', response_model=schemas.TaskOut, dependencies=[Depends(current_user)])
def create_task(payload: schemas.TaskCreate, db: Session=Depends(get_db)): return generic_create(models.Task, payload, db, 'task')
@app.get('/tasks', response_model=list[schemas.TaskOut], dependencies=[Depends(current_user)])
def list_tasks(db: Session=Depends(get_db)): return generic_list(models.Task, db)
@app.delete('/tasks/{item_id}', dependencies=[Depends(current_user)])
def delete_task(item_id:int, db: Session=Depends(get_db)): return generic_delete(models.Task, item_id, db, 'task')

@app.post('/opportunities', response_model=schemas.OpportunityOut, dependencies=[Depends(current_user)])
def create_opp(payload: schemas.OpportunityCreate, db: Session=Depends(get_db)): return generic_create(models.Opportunity, payload, db, 'opportunity')
@app.get('/opportunities', response_model=list[schemas.OpportunityOut], dependencies=[Depends(current_user)])
def list_opps(db: Session=Depends(get_db)): return generic_list(models.Opportunity, db)
@app.delete('/opportunities/{item_id}', dependencies=[Depends(current_user)])
def delete_opp(item_id:int, db: Session=Depends(get_db)): return generic_delete(models.Opportunity, item_id, db, 'opportunity')

@app.post('/capabilities', response_model=schemas.CapabilityOut, dependencies=[Depends(current_user)])
def create_cap(payload: schemas.CapabilityCreate, db: Session=Depends(get_db)):
    obj = generic_create(models.Capability, payload, db, 'capability')
    db.add(models.CapabilityHistory(capability_id=obj.id, score=obj.score, note='Initial capability score'))
    db.commit()
    return obj
@app.get('/capabilities', response_model=list[schemas.CapabilityOut], dependencies=[Depends(current_user)])
def list_caps(db: Session=Depends(get_db)): return generic_list(models.Capability, db)
@app.delete('/capabilities/{item_id}', dependencies=[Depends(current_user)])
def delete_cap(item_id:int, db: Session=Depends(get_db)): return generic_delete(models.Capability, item_id, db, 'capability')

@app.get('/capabilities/progress', dependencies=[Depends(current_user)])
def capability_progress(db: Session=Depends(get_db)):
    caps = db.query(models.Capability).order_by(models.Capability.score.desc()).all()
    return [{
        'id': c.id,
        'name': c.name,
        'score': c.score,
        'evidence_count': len(c.evidence),
        'fga_count': len(c.fgas),
        'coverage': min(100, round((len(c.evidence)*18)+(len(c.fgas)*10)+(c.score*0.45), 1)),
        'history': db.query(models.CapabilityHistory).filter(models.CapabilityHistory.capability_id==c.id).order_by(models.CapabilityHistory.created_at.desc()).limit(10).all()
    } for c in caps]

@app.post('/fgas', response_model=schemas.FGAOut, dependencies=[Depends(current_user)])
def create_fga(payload: schemas.FGACreate, db: Session=Depends(get_db)): return generic_create(models.FGA, payload, db, 'fga')
@app.get('/fgas', response_model=list[schemas.FGAOut], dependencies=[Depends(current_user)])
def list_fgas(db: Session=Depends(get_db)): return generic_list(models.FGA, db)
@app.delete('/fgas/{item_id}', dependencies=[Depends(current_user)])
def delete_fga(item_id:int, db: Session=Depends(get_db)): return generic_delete(models.FGA, item_id, db, 'fga')

def score_evidence(title, summary, tags, file_path=None):
    score = 20
    notes=[]
    if summary and len(summary) > 80: score += 25
    else: notes.append('Add a fuller summary with context and result.')
    if tags: score += 10
    else: notes.append('Add tags for search and grouping.')
    if file_path: score += 20
    else: notes.append('Attach a file if a concrete artifact exists.')
    if any(x in (summary or '').lower() for x in ['result','impact','improved','reduced','increased','delivered','built','created']): score += 15
    else: notes.append('Add impact/result language.')
    if any(ch.isdigit() for ch in (summary or '')): score += 10
    else: notes.append('Add a number or measurable outcome when available.')
    return min(score,100), ' '.join(notes) or 'Evidence is reasonably complete.'

def draft_resume_bullet(title, summary):
    basis = summary or 'a captured operational artifact'
    return f"Created {title}, converting work into reusable evidence by documenting context, actions, and outcomes around {basis[:140]}".strip()

def draft_story(title, summary):
    return f"Situation: A meaningful work item needed to become durable evidence. Task: Capture {title} with reusable context. Action: Documented the artifact, summary, tags, and linkage points. Result: {summary or 'The item is now available for capability tracking, portfolio preparation, resume bullets, and interview stories.'}"

def draft_star(title, summary):
    result = summary or 'The work is now traceable as evidence inside Quintessence.'
    return f"Situation: {title} represented progress worth preserving.\nTask: Turn the work into clear evidence.\nAction: Captured the artifact, context, tags, and relationship links.\nResult: {result}"

@app.post('/evidence', response_model=schemas.EvidenceOut, dependencies=[Depends(current_user)])
def create_evidence(payload: schemas.EvidenceCreate, db: Session=Depends(get_db)):
    data = payload.model_dump(exclude={'capability_ids','project_ids','task_ids','fga_ids','opportunity_ids'})
    if not data.get('resume_bullet_draft'): data['resume_bullet_draft'] = draft_resume_bullet(data['title'], data.get('summary',''))
    if not data.get('interview_story_draft'): data['interview_story_draft'] = draft_story(data['title'], data.get('summary',''))
    if not data.get('star_story_draft'): data['star_story_draft'] = draft_star(data['title'], data.get('summary',''))
    data['evidence_score'], data['completeness_notes'] = score_evidence(data['title'], data.get('summary',''), data.get('tags',''))
    obj = models.EvidenceItem(**data)
    obj.capabilities = db.query(models.Capability).filter(models.Capability.id.in_(payload.capability_ids)).all() if payload.capability_ids else []
    obj.projects = db.query(models.Project).filter(models.Project.id.in_(payload.project_ids)).all() if payload.project_ids else []
    obj.tasks = db.query(models.Task).filter(models.Task.id.in_(payload.task_ids)).all() if payload.task_ids else []
    obj.fgas = db.query(models.FGA).filter(models.FGA.id.in_(payload.fga_ids)).all() if payload.fga_ids else []
    obj.opportunities = db.query(models.Opportunity).filter(models.Opportunity.id.in_(payload.opportunity_ids)).all() if payload.opportunity_ids else []
    db.add(obj); db.commit(); db.refresh(obj)
    log_activity(db, 'created', 'evidence', obj.id, obj.title)
    return obj

@app.post('/evidence/upload', response_model=schemas.EvidenceOut, dependencies=[Depends(current_user)])
def upload_evidence(title: str=Form(...), summary: str=Form(''), evidence_type: str=Form('artifact'), tags: str=Form(''), file: UploadFile=File(...), db: Session=Depends(get_db)):
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest = Path(settings.STORAGE_DIR) / safe_name
    with dest.open('wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    score, notes = score_evidence(title, summary, tags, str(dest))
    obj = models.EvidenceItem(title=title, summary=summary, evidence_type=evidence_type, tags=tags, file_path=str(dest), resume_bullet_draft=draft_resume_bullet(title, summary), interview_story_draft=draft_story(title, summary), star_story_draft=draft_star(title, summary), evidence_score=score, completeness_notes=notes)
    db.add(obj); db.commit(); db.refresh(obj)
    log_activity(db, 'uploaded', 'evidence', obj.id, obj.title)
    return obj

@app.get('/evidence', response_model=list[schemas.EvidenceOut], dependencies=[Depends(current_user)])
def list_evidence(db: Session=Depends(get_db)): return db.query(models.EvidenceItem).order_by(models.EvidenceItem.created_at.desc()).all()
@app.delete('/evidence/{item_id}', dependencies=[Depends(current_user)])
def delete_evidence(item_id:int, db: Session=Depends(get_db)): return generic_delete(models.EvidenceItem, item_id, db, 'evidence')

@app.post('/evidence/{item_id}/links', response_model=schemas.EvidenceOut, dependencies=[Depends(current_user)])
def update_evidence_links(item_id:int, payload: schemas.EvidenceLinksIn, db: Session=Depends(get_db)):
    obj = db.get(models.EvidenceItem, item_id)
    if not obj: raise HTTPException(status_code=404, detail='Evidence not found')
    obj.capabilities = db.query(models.Capability).filter(models.Capability.id.in_(payload.capability_ids)).all() if payload.capability_ids else []
    obj.projects = db.query(models.Project).filter(models.Project.id.in_(payload.project_ids)).all() if payload.project_ids else []
    obj.tasks = db.query(models.Task).filter(models.Task.id.in_(payload.task_ids)).all() if payload.task_ids else []
    obj.fgas = db.query(models.FGA).filter(models.FGA.id.in_(payload.fga_ids)).all() if payload.fga_ids else []
    obj.opportunities = db.query(models.Opportunity).filter(models.Opportunity.id.in_(payload.opportunity_ids)).all() if payload.opportunity_ids else []
    db.commit(); db.refresh(obj)
    log_activity(db, 'linked', 'evidence', obj.id, obj.title)
    return obj

@app.get('/evidence/bank/resume', dependencies=[Depends(current_user)])
def resume_bullet_bank(db: Session=Depends(get_db)):
    items = db.query(models.EvidenceItem).order_by(models.EvidenceItem.evidence_score.desc()).all()
    return [{'id': e.id, 'title': e.title, 'score': e.evidence_score, 'resume_bullet': e.resume_bullet_draft, 'star_story': e.star_story_draft} for e in items]

@app.post('/ai-items', response_model=schemas.AIItemOut, dependencies=[Depends(current_user)])
def create_ai(payload: schemas.AIItemCreate, db: Session=Depends(get_db)): return generic_create(models.AIItem, payload, db, 'ai_item')
@app.get('/ai-items', response_model=list[schemas.AIItemOut], dependencies=[Depends(current_user)])
def list_ai(db: Session=Depends(get_db)): return generic_list(models.AIItem, db)

@app.post('/notes', response_model=schemas.NoteOut, dependencies=[Depends(current_user)])
def create_note(payload: schemas.NoteCreate, db: Session=Depends(get_db)): return generic_create(models.Note, payload, db, 'note')
@app.get('/notes', response_model=list[schemas.NoteOut], dependencies=[Depends(current_user)])
def list_notes(db: Session=Depends(get_db)): return generic_list(models.Note, db)

@app.post('/decisions', response_model=schemas.DecisionOut, dependencies=[Depends(current_user)])
def create_decision(payload: schemas.DecisionCreate, db: Session=Depends(get_db)): return generic_create(models.Decision, payload, db, 'decision')
@app.get('/decisions', response_model=list[schemas.DecisionOut], dependencies=[Depends(current_user)])
def list_decisions(db: Session=Depends(get_db)): return generic_list(models.Decision, db)

def compute_weekly_review(db: Session):
    completed = db.query(models.Task).filter(models.Task.status=='complete').all()
    blockers = db.query(models.Task).filter(models.Task.status=='blocked').all()
    evidence = db.query(models.EvidenceItem).order_by(models.EvidenceItem.created_at.desc()).limit(10).all()
    recs=[]
    if blockers: recs.append('Resolve or re-scope blocked tasks before adding new commitments.')
    if evidence: recs.append('Convert recent evidence into resume bullets and interview stories.')
    if db.query(models.FGA).filter(models.FGA.completed==False).count(): recs.append('Choose one active FGA as the weekly growth focus.')
    if db.query(models.EvidenceItem).filter(models.EvidenceItem.evidence_score < 60).count(): recs.append('Improve low-scoring evidence with richer context, outcomes, tags, or artifacts.')
    return {'completed_work': completed, 'blockers': blockers, 'evidence_generated': evidence, 'recommended_next_actions': recs}

@app.get('/weekly-review', dependencies=[Depends(current_user)])
def weekly_review(db: Session=Depends(get_db)):
    return compute_weekly_review(db)

@app.post('/weekly-review/save', response_model=schemas.WeeklyReviewSnapshotOut, dependencies=[Depends(current_user)])
def save_weekly_review(payload: schemas.WeeklyReviewSnapshotCreate, db: Session=Depends(get_db)):
    review = compute_weekly_review(db)
    snap = models.WeeklyReviewSnapshot(
        title=payload.title,
        completed_work=json.dumps([model_to_dict(x) for x in review['completed_work']], default=str),
        blockers=json.dumps([model_to_dict(x) for x in review['blockers']], default=str),
        evidence_generated=json.dumps([model_to_dict(x) for x in review['evidence_generated']], default=str),
        recommended_next_actions=json.dumps(review['recommended_next_actions'], default=str),
        notes=payload.notes
    )
    db.add(snap); db.commit(); db.refresh(snap)
    log_activity(db, 'saved', 'weekly_review', snap.id, snap.title)
    return snap

@app.get('/weekly-reviews', response_model=list[schemas.WeeklyReviewSnapshotOut], dependencies=[Depends(current_user)])
def list_weekly_reviews(db: Session=Depends(get_db)):
    return db.query(models.WeeklyReviewSnapshot).order_by(models.WeeklyReviewSnapshot.created_at.desc()).all()

@app.get('/activity', response_model=list[schemas.ActivityLogOut], dependencies=[Depends(current_user)])
def activity(db: Session=Depends(get_db)):
    return db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(200).all()

@app.get('/search', response_model=list[schemas.SearchResult], dependencies=[Depends(current_user)])
def search(q: str, db: Session=Depends(get_db)):
    ql = f'%{q.lower()}%'
    results=[]
    def add(module, rows, title_field, summary_field=''):
        for r in rows:
            results.append({'module': module, 'id': r.id, 'title': getattr(r,title_field,''), 'summary': getattr(r,summary_field,'') if summary_field else '', 'created_at': str(getattr(r,'created_at','') or '')})
    add('Projects', db.query(models.Project).filter((models.Project.name.ilike(ql)) | (models.Project.objective.ilike(ql))).limit(20).all(), 'name', 'objective')
    add('Tasks', db.query(models.Task).filter((models.Task.title.ilike(ql)) | (models.Task.description.ilike(ql))).limit(20).all(), 'title', 'description')
    add('Career', db.query(models.Opportunity).filter((models.Opportunity.company.ilike(ql)) | (models.Opportunity.role.ilike(ql)) | (models.Opportunity.notes.ilike(ql))).limit(20).all(), 'role', 'notes')
    add('Capabilities', db.query(models.Capability).filter((models.Capability.name.ilike(ql)) | (models.Capability.description.ilike(ql))).limit(20).all(), 'name', 'description')
    add('FGAs', db.query(models.FGA).filter((models.FGA.name.ilike(ql)) | (models.FGA.goal.ilike(ql))).limit(20).all(), 'name', 'goal')
    add('Evidence', db.query(models.EvidenceItem).filter((models.EvidenceItem.title.ilike(ql)) | (models.EvidenceItem.summary.ilike(ql)) | (models.EvidenceItem.tags.ilike(ql))).limit(20).all(), 'title', 'summary')
    add('Knowledge Vault', db.query(models.Note).filter((models.Note.title.ilike(ql)) | (models.Note.content.ilike(ql)) | (models.Note.tags.ilike(ql))).limit(20).all(), 'title', 'content')
    add('Decisions', db.query(models.Decision).filter((models.Decision.title.ilike(ql)) | (models.Decision.decision.ilike(ql)) | (models.Decision.rationale.ilike(ql))).limit(20).all(), 'title', 'decision')
    return results[:100]

@app.get('/settings', response_model=list[schemas.SettingOut], dependencies=[Depends(current_user)])
def list_settings(db: Session=Depends(get_db)):
    defaults = {'theme':'observatory','default_module':'Mission Control','backup_dir':'./backups','storage_dir':settings.STORAGE_DIR,'local_only':'true'}
    for k,v in defaults.items():
        if not db.query(models.Setting).filter(models.Setting.key==k).first():
            db.add(models.Setting(key=k,value=v))
    db.commit()
    return db.query(models.Setting).order_by(models.Setting.key).all()

@app.put('/settings/{key}', response_model=schemas.SettingOut, dependencies=[Depends(current_user)])
def update_setting(key:str, payload: schemas.SettingIn, db: Session=Depends(get_db)):
    item = db.query(models.Setting).filter(models.Setting.key==key).first()
    if not item:
        item = models.Setting(key=key, value=payload.value); db.add(item)
    else:
        item.value = payload.value
    db.commit(); db.refresh(item)
    log_activity(db, 'updated', 'setting', item.id, key)
    return item

@app.post('/backup/create', dependencies=[Depends(current_user)])
def create_backup(db: Session=Depends(get_db)):
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = Path('backups') / f'quintessence_backup_{stamp}.zip'
    db_path = Path(settings.DATABASE_URL.replace('sqlite:///','')) if settings.DATABASE_URL.startswith('sqlite') else None
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        if db_path and db_path.exists(): z.write(db_path, f'data/{db_path.name}')
        storage = Path(settings.STORAGE_DIR)
        if storage.exists():
            for p in storage.rglob('*'):
                if p.is_file(): z.write(p, f'storage/{p.relative_to(storage)}')
    log_activity(db, 'created', 'backup', None, str(dest))
    return {'backup': str(dest), 'created_at': stamp}

@app.get('/backup/list', dependencies=[Depends(current_user)])
def list_backups():
    return [{'name':p.name,'path':str(p),'size':p.stat().st_size,'modified':datetime.fromtimestamp(p.stat().st_mtime).isoformat()} for p in sorted(Path('backups').glob('*.zip'), reverse=True)]

@app.post('/export/create', dependencies=[Depends(current_user)])
def create_export(db: Session=Depends(get_db)):
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = Path('exports') / f'quintessence_export_{stamp}'
    folder.mkdir(parents=True, exist_ok=True)
    models_to_export = [('projects',models.Project),('tasks',models.Task),('opportunities',models.Opportunity),('capabilities',models.Capability),('fgas',models.FGA),('evidence',models.EvidenceItem),('ai_items',models.AIItem),('notes',models.Note),('decisions',models.Decision),('activity',models.ActivityLog)]
    for name, model in models_to_export:
        rows=[model_to_dict(x) for x in db.query(model).all()]
        (folder/f'{name}.json').write_text(json.dumps(rows, indent=2, default=str), encoding='utf-8')
        with (folder/f'{name}.csv').open('w', newline='', encoding='utf-8') as f:
            if rows:
                writer=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader(); writer.writerows(rows)
    bullets = '\n'.join([f'- {e.resume_bullet_draft}' for e in db.query(models.EvidenceItem).all() if e.resume_bullet_draft])
    (folder/'resume_bullets.md').write_text('# Resume Bullet Bank\n\n'+bullets, encoding='utf-8')
    zip_path = Path('exports') / f'quintessence_export_{stamp}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in folder.rglob('*'):
            z.write(p, p.relative_to(folder.parent))
    log_activity(db, 'created', 'export', None, str(zip_path))
    return {'export': str(zip_path), 'created_at': stamp}

@app.get('/local/paths', dependencies=[Depends(current_user)])
def local_paths():
    return {'data_dir': str(Path('data').resolve()), 'storage_dir': str(Path(settings.STORAGE_DIR).resolve()), 'backups_dir': str(Path('backups').resolve()), 'exports_dir': str(Path('exports').resolve())}

@app.on_event('startup')
def seed():
    db = next(get_db())
    try:
        if db.query(models.Project).count() == 0:
            cap1=models.Capability(name='AI Workflow Design', description='Designing useful AI-assisted workflows.', score=65, growth_history='Initial MVP seed.')
            cap2=models.Capability(name='Operations Execution', description='Turning plans into tracked progress.', score=70)
            project=models.Project(name='Quintessence Phase 1 MVP', objective='Build a runnable personal operations system.', status='active', priority='high')
            task=models.Task(title='Manufacture Phase 1 runnable MVP', status='in_progress', priority='high', project=project)
            fga=models.FGA(name='Evidence Engine MVP', goal='Create evidence linking and draft generation.', capability=cap1)
            opp=models.Opportunity(company='Example Company', role='Operations / AI Workflow Role', status='found', capability_fit=75, evidence_fit=50)
            ev=models.EvidenceItem(title='Quintessence build brief', evidence_type='document', summary='Product intent and architecture brief captured.', tags='quintessence,architecture,evidence', resume_bullet_draft='Designed a personal operations system architecture connecting projects, capabilities, evidence, and decisions.', interview_story_draft='Situation: personal work was fragmented. Action: designed Quintessence MVP. Result: clearer execution and evidence workflow.', star_story_draft='Situation: Work was fragmented.\nTask: Design a local personal operating system.\nAction: Built Quintessence MVP.\nResult: A working local operational system exists.', evidence_score=80, completeness_notes='Strong seed evidence.')
            ev.capabilities=[cap1,cap2]; ev.projects=[project]; ev.fgas=[fga]; ev.opportunities=[opp]
            dec=models.Decision(title='Phase 1 scope', decision='Build Option C runnable MVP first.', rationale='Large enough to validate the architecture without waiting for the full product.', consequences='Advanced AI integration deferred to a later phase.')
            note=models.Note(title='Quintessence principle', note_type='architecture', content='Everything has a home. Progress must be visible. Evidence should be reusable.', tags='principles')
            ai=models.AIItem(title='Weekly Review Prompt', item_type='prompt', model='storage-first', content='Summarize completed work, blockers, evidence generated, and recommended next actions.')
            db.add_all([cap1,cap2,project,task,fga,opp,ev,dec,note,ai]); db.commit()
            db.add_all([models.CapabilityHistory(capability_id=cap1.id, score=65, note='Seed score'), models.CapabilityHistory(capability_id=cap2.id, score=70, note='Seed score')]); db.commit()
    finally:
        db.close()
