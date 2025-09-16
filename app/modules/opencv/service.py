import os
import shutil
import time
from fastapi import HTTPException,status,Depends,UploadFile
from .frames_extraction import frameExtractionService
from app.utils.logger import api_logger as logger

class OpencvService:
    def __init__(self):
        pass

    async def process_frames(self, file:UploadFile):
        frames_dir = None
        video_path = None
        try:
            logger.info("processing of video frams start")
            timestamp = int(time.time() * 1000)
            video_filename = f"{timestamp}_{file.filename}"
            video_path = f"/tmp/{video_filename}"
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            frames_dir = f"/tmp/frames_{timestamp}_{os.path.splitext(file.filename)[0]}"
            os.makedirs(frames_dir, exist_ok=True)

            unique_frames = await frameExtractionService.extract_unique_frames(video_path, frames_dir)
            results = []
            for frames in unique_frames:
                data = await frameExtractionService.handle_frames(frames)
                results.append(data)
            return {"results": results}
        except Exception as e:
            logger.error(f"failed to process frams: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"failed to process frams: {e}")
        finally:
            if frames_dir and os.path.exists(frames_dir):
                shutil.rmtree(frames_dir)
                logger.info(f"Cleaned up frames folder: {frames_dir}")
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Deleted temporary video file: {video_path}")
            
opencvService = OpencvService()
