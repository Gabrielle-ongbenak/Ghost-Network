from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, SessionLocal, Base
from app.routers import (
    ingest_router,
    listings_router,
    graph_router,
    networks_router,
    stats_router
)
from app.services.seed_loader import load_seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created
    print("FastAPI Startup: Checking database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database schema verified.")
        if settings.AUTO_SEED:
            db = SessionLocal()
            try:
                from app.models.listing import Listing
                if db.query(Listing).count() == 0:
                    print("Database empty. Auto-seeding listings...")
                    load_seed_data(db)
                    print("Auto-seeding complete.")
            finally:
                db.close()
    except Exception as e:
        print(f"Warning on startup initialization: {e}")

    yield

    # Shutdown
    print("FastAPI Shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Pan-African Job-Scam Network Detection API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers under /api
app.include_router(ingest_router, prefix=settings.API_PREFIX)
app.include_router(listings_router, prefix=settings.API_PREFIX)
app.include_router(graph_router, prefix=settings.API_PREFIX)
app.include_router(networks_router, prefix=settings.API_PREFIX)
app.include_router(stats_router, prefix=settings.API_PREFIX)

@app.get("/", tags=["Health"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "healthy"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
