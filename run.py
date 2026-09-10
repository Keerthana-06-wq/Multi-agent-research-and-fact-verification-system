import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print("=" * 70)
    print("  VERITAS - Multi-Agent Research and Fact Verification System")
    print("=" * 70)
    print(f"  [>] Server starting on http://{settings.HOST}:{settings.PORT}")
    print(f"  [>] Web Interface:    http://{settings.HOST}:{settings.PORT}/")
    print(f"  [>] Interactive API:  http://{settings.HOST}:{settings.PORT}/docs")
    print("  [>] 'Verify First, Answer Second' Engine is ready.")
    print("=" * 70)
    uvicorn.run(
        "backend.api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
