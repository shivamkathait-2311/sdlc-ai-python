
import signal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.utils.logger import api_logger as logger
import uvicorn
from app.modules.opencv.routes import router as opencv_router

app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opencv_router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting application...")
    
    # # Initialize database tables (if they don't exist)
    # logger.info("Creating database tables...")
    # Base.metadata.create_all(bind=engine)
    # logger.info("Database tables created")
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Application shutdown initiated")
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    return {
        "message": "Data Pipeline API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs"
    }

# Setup signal handlers for graceful shutdown
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown in development mode"""
    def handle_signal(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown")
        # This will trigger FastAPI's shutdown event
        raise KeyboardInterrupt
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

if __name__ == "__main__":
    # Setup signal handlers for development mode
    setup_signal_handlers()
    logger.info("Starting development server")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  