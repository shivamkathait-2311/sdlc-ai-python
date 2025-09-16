import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Project Metadata
    PROJECT_NAME: str = "SDLC Ai"
    PROJECT_VERSION: str = "1.0.0"
   
    
settings = Settings()