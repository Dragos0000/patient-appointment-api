from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.entrypoints.patient_api import router as patient_router
from src.entrypoints.appointment_api import router as appointment_router
from src.models.api_responses import APIErrorResponse, APIError
from src.adapters.database.init_db import create_tables
import src.adapters.database.tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Patient Appointment API",
    description="API for managing patients and appointments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(patient_router)
app.include_router(appointment_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Creating database tables...")
    await create_tables()
    logger.info("Database tables created successfully!")


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "message": "Patient Appointment API is running"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = APIErrorResponse(
        error=APIError(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details=None  # Don't expose internal error details in production
        )
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.entrypoints.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
