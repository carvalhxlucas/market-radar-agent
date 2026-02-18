"""Main API entry point (legacy - use api/app.py)."""
from api.app import create_app
from config.settings import Settings

app = create_app()
settings = Settings()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
