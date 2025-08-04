import asyncio
import aiosqlite
from pathlib import Path

DATABASE_PATH = "server/medical_documents.db"
UPLOAD_DIR = Path("server/uploads")

async def setup_database():
    """Initialize the database and create necessary directories"""
    try:
        print("🚀 Setting up Medical Documents Application...")
        
        # Create uploads directory
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        print("📁 Created uploads directory")
        
        # Initialize database
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    filesize INTEGER NOT NULL,
                    created_at DATETIME NOT NULL
                )
            """)
            await db.commit()
            print("📊 Database initialized successfully")
        
        print("✅ Setup completed successfully!")
        print("")
        print("Run the following commands to start the application:")
        print("1. Frontend: npm run dev:frontend")
        print("2. Backend: python -m uvicorn server.main:app --reload --port 3001")
        print("   Or: npm run dev:backend")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(setup_database())