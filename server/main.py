from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import aiofiles
import aiosqlite
import os
import shutil
import time
import random
from pathlib import Path
from typing import List, Optional
import magic
from datetime import datetime
import json

app = FastAPI(
    title="Medical Documents API",
    description="Secure API for managing medical documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("server/uploads")
DATABASE_PATH = "server/medical_documents.db"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = ["application/pdf"]

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Database initialization
async def init_database():
    """Initialize the SQLite database with documents table"""
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

async def get_database():
    """Get database connection"""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

def validate_pdf_file(file: UploadFile) -> bool:
    """Validate that the uploaded file is a PDF"""
    # Check file extension
    if not file.filename.lower().endswith('.pdf'):
        return False
    
    # Check MIME type from the file content
    try:
        # Read first few bytes to check magic number
        file.file.seek(0)
        header = file.file.read(1024)
        file.file.seek(0)  # Reset file pointer
        
        # PDF files start with %PDF
        if header.startswith(b'%PDF'):
            return True
        
        return False
    except Exception:
        return False

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent conflicts"""
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    name, ext = os.path.splitext(original_filename)
    return f"{timestamp}-{random_suffix}-{name}{ext}"

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()
    print("🏥 Medical Documents API started successfully")
    print(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/documents/upload")
async def upload_document(
    document: UploadFile = File(...),
    db: aiosqlite.Connection = Depends(get_database)
):
    """Upload a PDF document"""
    try:
        # Validate file type
        if not validate_pdf_file(document):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Check file size
        document.file.seek(0, 2)  # Seek to end
        file_size = document.file.tell()
        document.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10MB limit"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file not allowed"
            )
        
        # Generate unique filename
        unique_filename = generate_unique_filename(document.filename)
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await document.read()
            await f.write(content)
        
        # Save metadata to database
        created_at = datetime.now().isoformat()
        cursor = await db.execute("""
            INSERT INTO documents (filename, original_name, filepath, filesize, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (unique_filename, document.filename, str(file_path), file_size, created_at))
        
        await db.commit()
        
        # Get the inserted document
        doc_cursor = await db.execute(
            "SELECT * FROM documents WHERE id = ?", 
            (cursor.lastrowid,)
        )
        doc_row = await doc_cursor.fetchone()
        
        if not doc_row:
            raise HTTPException(status_code=500, detail="Failed to retrieve uploaded document")
        
        return {
            "message": "Document uploaded successfully",
            "document": {
                "id": doc_row["id"],
                "filename": doc_row["original_name"],
                "filesize": doc_row["filesize"],
                "created_at": doc_row["created_at"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        # Clean up file if it was created
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail="Internal server error during upload"
        )

@app.get("/api/documents")
async def get_documents(db: aiosqlite.Connection = Depends(get_database)):
    """Get all documents metadata"""
    try:
        cursor = await db.execute("""
            SELECT id, original_name as filename, filesize, created_at
            FROM documents
            ORDER BY created_at DESC
        """)
        rows = await cursor.fetchall()
        
        documents = []
        for row in rows:
            documents.append({
                "id": row["id"],
                "filename": row["filename"],
                "filesize": row["filesize"],
                "created_at": row["created_at"]
            })
        
        return {"documents": documents}
        
    except Exception as e:
        print(f"Get documents error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/documents/{document_id}")
async def download_document(
    document_id: int,
    db: aiosqlite.Connection = Depends(get_database)
):
    """Download a specific document"""
    try:
        cursor = await db.execute(
            "SELECT * FROM documents WHERE id = ?", 
            (document_id,)
        )
        doc_row = await cursor.fetchone()
        
        if not doc_row:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        file_path = Path(doc_row["filepath"])
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found on disk"
            )
        
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=doc_row["original_name"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Download error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during download"
        )

@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: aiosqlite.Connection = Depends(get_database)
):
    """Delete a document"""
    try:
        # Get document info
        cursor = await db.execute(
            "SELECT * FROM documents WHERE id = ?", 
            (document_id,)
        )
        doc_row = await cursor.fetchone()
        
        if not doc_row:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        # Delete file from disk
        file_path = Path(doc_row["filepath"])
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        delete_cursor = await db.execute(
            "DELETE FROM documents WHERE id = ?", 
            (document_id,)
        )
        await db.commit()
        
        if delete_cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during deletion"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)