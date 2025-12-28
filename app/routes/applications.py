from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.models import Application, ApplicationHistory, Job, Stage, User
from app.dependencies import role_required
from app.workflow import ApplicationWorkflow
from app.database import get_db
from app.email_tasks import send_email

router = APIRouter(tags=["applications"])


# =========================
# APPLY FOR JOB (CANDIDATE)
# =========================
@router.post("/apply/{job_id}")
def apply_job(
    job_id: int,
    background_tasks: BackgroundTasks,
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
    db.flush()  # ensures application.id is available

    # 4️⃣ Audit trail
    history = ApplicationHistory(
        application_id=application.id,
        previous_stage=None,
        new_stage=Stage.Applied,
        changed_by=user.id
    )
    db.add(history)

    # 5️⃣ Commit once (atomic)
    db.commit()
    db.refresh(application)

    # 6️⃣ NON-BLOCKING EMAIL
    background_tasks.add_task(
        send_email,
        user.email,
        "Application Submitted",
        f"You have successfully applied for '{job.title}'."
    )

    return {
        "message": "Application submitted successfully",
        "application_id": application.id,
        "stage": application.stage.value
    }


# =========================
# VIEW MY APPLICATIONS
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
    background_tasks: BackgroundTasks,
    user=Depends(role_required("recruiter")),
    db: Session = Depends(get_db)
):
    # 1️⃣ Fetch application
    application = db.query(Application).filter(Application.id == id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 2️⃣ Fetch related job
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 3️⃣ 🔐 COMPANY OWNERSHIP CHECK (CRITICAL FIX)
    if job.company_id != user.company_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to manage this application"
        )

    # 4️⃣ Workflow transition
    wf = ApplicationWorkflow(application.stage.value)
    if not hasattr(wf, action):
        raise HTTPException(status_code=400, detail="Invalid action")

    previous_stage = application.stage
    getattr(wf, action)()

    try:
        application.stage = Stage(wf.state)

        history = ApplicationHistory(
            application_id=application.id,
            previous_stage=previous_stage,
            new_stage=Stage(wf.state),
            changed_by=user.id
        )

        db.add(history)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Stage update failed")

    # 5️⃣ Async email (non-blocking)
    background_tasks.add_task(
        send_email,
        application.candidate.email,
        "Application Status Updated",
        f"New stage: {wf.state}"
    )

    return {"stage": wf.state}
