from fastapi import APIRouter, Depends, UploadFile, File
from .service import opencvService

router = APIRouter(prefix="/api/v1/opencv", tags=["opencv"])

@router.post("/process/frames")
async def process_frams(file: UploadFile = File(...)):
    return await opencvService.process_frames(file)