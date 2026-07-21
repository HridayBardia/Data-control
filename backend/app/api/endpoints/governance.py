from fastapi import APIRouter
from pydantic import BaseModel
from app.governance.classifier import data_classifier
from app.governance.lineage import lineage_tracker

router = APIRouter()

class ScanRequest(BaseModel):
    content: str

class LineageRequest(BaseModel):
    document_id: str
    connector_type: str
    classification: str

@router.post("/scan")
def scan_content(req: ScanRequest):
    return data_classifier.scan_and_classify(req.content)

@router.post("/lineage")
def generate_lineage(req: LineageRequest):
    return lineage_tracker.generate_lineage_trace(req.document_id, req.connector_type, req.classification)
