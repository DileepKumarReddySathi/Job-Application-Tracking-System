from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import Application, ApplicationHistory, Job, Stage,User
from app.dependencies import role_required
from app.workflow import ApplicationWorkflow
from app.database import get_db
from app.email_tasks import send_email

router = APIRouter()


# =========================
# APPLY FOR JOB (CANDIDATE)
# =========================
@router.post("/apply/{job_id}")
def apply_job(
    job_id: int,
    user=Depends(role_required("candidate")),
    db: Session = Depends(get_db)
):
    # 1️⃣ Check job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2️⃣ Prevent duplicate application
    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.candidate_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    # 3️⃣ Create application
    application = Application(
        job_id=job_id,
        candidate_id=user.id,
        stage=Stage.Applied
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # 4️⃣ Save history
    history = ApplicationHistory(
        application_id=application.id,
        previous_stage=None,
        new_stage=Stage.Applied,
        changed_by=user.id
    )
    db.add(history)
    db.commit()

    # 5️⃣ Send email (SYNC – no Redis)
    send_email(
        user.email,
        "Application Submitted",
        f"You applied for {job.title}"
    )

    return {
        "message": "Application submitted successfully",
        "application_id": application.id
    }
# =========================
@router.get("/applications/me")
def my_applications(
    user=Depends(role_required("candidate")),
    db: Session = Depends(get_db)
):
    applications = (
        db.query(Application)
        .filter(Application.candidate_id == user.id)
        .all()
    )

    return [
        {
            "application_id": app.id,
            "job_id": app.job_id,
            "stage": app.stage.value,
            "applied_at": app.created_at
        }
        for app in applications
    ]


# =========================
# CHANGE APPLICATION STAGE
# =========================
@router.put("/applications/{id}/stage")
def change_stage(
    id: int,
    action: str,
    user=Depends(role_required("recruiter")),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Workflow
    wf = ApplicationWorkflow(app.stage.value)
    if not hasattr(wf, action):
        raise HTTPException(status_code=400, detail="Invalid action")

    getattr(wf, action)()

    # Save history
    history = ApplicationHistory(
        application_id=id,
        previous_stage=app.stage,
        new_stage=Stage(wf.state),  # convert string to Enum
        changed_by=user.id
    )

    app.stage = Stage(wf.state)
    db.add(history)
    db.commit()

    # Send email to actual candidate
    candidate = db.query(User).filter(User.id == app.candidate_id).first()
    send_email(
        candidate.email,
        "Application Stage Updated",
        f"New stage: {wf.state}"
    )

    return {"stage": wf.state}

