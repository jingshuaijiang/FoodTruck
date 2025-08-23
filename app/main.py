from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import search, health
from app.dataloader.food_truck_loader import data_loader
import asyncio
import threading
import time

# Create FastAPI app
app = FastAPI(
    title="SF Food Truck API",
    description="A unified search API for San Francisco food truck permits",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routers
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(health.router, prefix="/api", tags=["Health"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["Frontend"])
async def read_index():
    """Serve the main page"""
    return FileResponse("app/static/index.html")

def periodic_data_reload():
    """Background task to reload data every minute"""
    while True:
        try:
            time.sleep(60)  # Wait 60 seconds
            data_loader.reload_data()
        except Exception as e:
            print(f"Error in periodic data reload: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize data service on startup"""
    data_loader.load_data()
    # Start the background task for periodic reloading in a separate thread
    reload_thread = threading.Thread(target=periodic_data_reload, daemon=True)
    reload_thread.start()
    print("Background data reload task started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
