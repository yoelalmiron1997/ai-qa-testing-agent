from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.storage.models import APISpecModel
from app.storage.repository import APIRepository
from app.api.v1.schemas import APISpecResponse
from app.agent.qa_agent import qa_agent

router = APIRouter(prefix="/apis", tags=["APIs Spec Management"])

@router.post("/upload", response_model=APISpecResponse)
async def upload_api_spec(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")
        parsed = qa_agent.parse_and_inspect_spec(content, file.filename or "")
        
        repo = APIRepository(db)
        spec = APISpecModel(
            title=parsed.get("title", file.filename),
            version=parsed.get("version", "1.0.0"),
            description=parsed.get("description", ""),
            base_url=parsed.get("base_url"),
            raw_content=content,
            format=parsed.get("format", "json"),
            endpoints_count=parsed.get("endpoints_count", 0),
            parsed_metadata=parsed
        )
        saved_spec = repo.save_spec(spec)
        return saved_spec
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse OpenAPI file: {str(e)}")

@router.get("", response_model=List[APISpecResponse])
def list_api_specs(db: Session = Depends(get_db)):
    repo = APIRepository(db)
    return repo.list_specs()

@router.get("/{spec_id}", response_model=APISpecResponse)
def get_api_spec(spec_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    spec = repo.get_spec(spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="API Specification not found")
    return spec

@router.delete("/{spec_id}")
def delete_api_spec(spec_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    success = repo.delete_spec(spec_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Specification not found")
    return {"message": "API specification deleted successfully"}
