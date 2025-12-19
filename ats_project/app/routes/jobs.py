from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Job
from app.database import get_db
from app.dependencies import role_required, get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Create a new job (Recruiter only)
@router.post("/")
def create_job(title: str, description: str, db: Session = Depends(get_db), user=Depends(role_required("recruiter"))):
    job = Job(title=title, description=description, status="open", company_id=user.company_id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

# List all jobs (any role)
@router.get("/")
def list_jobs(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    return query.all()

# Update job (Recruiter only)
@router.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(role_required("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if title:
        job.title = title
    if description:
        job.description = description
    if status:
        job.status = status

    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "status": job.status
    }


# Delete job (Recruiter only)
@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user=Depends(role_required("recruiter"))):
    job = db.query(Job).get(job_id)
    if not job or job.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"msg": "Job deleted successfully"}
