import os, re, subprocess
from PIL import Image
import imagehash
import pytesseract
import cv2

from fastapi import HTTPException,status,Depends
from app.utils.logger import api_logger as logger

class FrameExtractionService:
    def __init__(self):
        pass

    async def extract_unique_frames(self, video_path, frames_dir):
        try:
            logger.info("extracting the unique frames")

            os.makedirs(frames_dir, exist_ok=True)

            # Run FFmpeg and capture stderr logs
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", "select=gt(scene\\,0.3),scale=1280:-1,showinfo",
                "-vsync", "vfr",
                os.path.join(frames_dir, "frame-%04d.png")
            ]
            result = subprocess.run(ffmpeg_cmd, stderr=subprocess.PIPE, text=True, check=True)

            # Parse timestamps from FFmpeg stderr
            timestamps = []
            for line in result.stderr.splitlines():
                match = re.search(r"pts_time:(\d+\.\d+)", line)
                if match:
                    timestamps.append(float(match.group(1)))

            # Deduplicate using perceptual hash
            unique_frames = []
            seen_hashes = []

            frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(".png")])

            for idx, file in enumerate(frame_files):
                file_path = os.path.join(frames_dir, file)

                img = Image.open(file_path)
                h = imagehash.phash(img, hash_size=16)
                img.close()

                if any(h - sh < 5 for sh in seen_hashes):
                    os.remove(file_path)
                else:
                    seen_hashes.append(h)
                    unique_frames.append({
                        "frame": file_path,
                        "time": timestamps[idx] if idx < len(timestamps) else None
                    })

            return unique_frames
        
        except Exception as e:
            raise Exception(f"failed to make unique frames: {e}")

    async def extract_text(self,frame_path):
        img = cv2.imread(frame_path)
        text = pytesseract.image_to_string(img)
        return text.splitlines()
    
    async def handle_frames(self,frames):
        try:
            logger.info("handle frames start")
            text_items = await self.extract_text(frames["frame"])
            ui_boxes = await self.detect_ui_elements(frames["frame"])

            return {
                "time": frames["time"],
                "ocrText": text_items,
                "uiBoxes": ui_boxes
            }
        except Exception as e:
            raise Exception(f"Failed to process frames: {e}")
          
    async def detect_ui_elements(self,frame_path):
        try:
            img = cv2.imread(frame_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # Find contours (shapes)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            ui_elements = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 20:  # filter small noise
                    roi = img[y:y+h, x:x+w]                      # region of interest in BGR
                    mean_color = cv2.mean(roi)[:3]               # (B, G, R)
                    color_rgb = tuple(int(c) for c in mean_color[::-1])  # convert to RGB
                    ui_elements.append({
                        "x": x, 
                        "y": y, 
                        "width": w, 
                        "height": h,
                        "color": {
                            "r": color_rgb[0],
                            "g": color_rgb[1],
                            "b": color_rgb[2]
                        }
                        })
            return ui_elements
        except Exception as e:
            raise HTTPException(f"failed to detect ui elements: {e}")



frameExtractionService = FrameExtractionService()