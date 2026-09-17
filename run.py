import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"==================================================")
    print(f"  FinNews AI - Financial News Simplifier")
    print(f"  Starting server on http://{settings.host}:{settings.port}")
    print(f"  API Docs available at http://{settings.host}:{settings.port}/docs")
    print(f"==================================================")
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
