from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from app.core.config import settings
from app.api.v1.routers import ingest
import time

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Autonomous system for ingesting web pages and extracting links with backlinks",
    version="0.1.0",
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

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info("Incoming request",
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host if request.client else None)
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info("Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception",
                method=request.method,
                url=str(request.url),
                error=str(exc),
                exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}

# Include routers
app.include_router(ingest.router, prefix="/v1/ingest", tags=["ingestion"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Link Ingestor",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


