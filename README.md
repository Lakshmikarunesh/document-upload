# Medical Documents Management System

A full-stack web application for securely managing medical documents. Upload, view, download, and delete your PDF medical documents with a clean, professional interface.

## 🏥 Features

- **Secure PDF Upload**: Drag-and-drop or click to upload PDF documents
- **Document Management**: View, download, and delete your medical documents
- **File Validation**: Only PDF files up to 10MB are accepted
- **Real-time Feedback**: Toast notifications for all operations
- **Responsive Design**: Works perfectly on desktop and tablet devices
- **Professional UI**: Clean, medical-themed interface with smooth animations

## 🚀 Technology Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS  
- **Backend**: Python 3.8+ + FastAPI + Uvicorn
- **Database**: SQLite (with aiosqlite for async operations)
- **Icons**: Lucide React
- **Build Tool**: Vite

## 📋 Prerequisites

- Node.js (version 16 or higher) for frontend
- Python 3.8+ for backend
- npm or yarn package manager

## 🛠️ Installation & Setup

1. **Clone or download the project**

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Install Python backend dependencies**:
   ```bash
   pip install fastapi uvicorn aiofiles aiosqlite python-multipart python-magic
   # Or install from requirements.txt:
   # pip install -r requirements.txt
   ```

4. **Set up the database and uploads directory**:
   ```bash
   npm run setup
   ```

5. **Start the development servers**:
   ```bash
   npm run dev
   ```

This will start both the frontend (http://localhost:5173) and FastAPI backend (http://localhost:3001) servers concurrently.

### Alternative: Start servers separately

**Frontend**:
```bash
npm run dev:frontend
```

**Backend**:
```bash
npm run dev:backend
# Or directly:
python -m uvicorn server.main:app --reload --port 3001
```

## 📁 Project Structure

```
medical-documents-app/
├── src/                    # React frontend code
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Tailwind CSS imports
├── server/                # FastAPI backend code
│   ├── main.py            # Main FastAPI application
│   ├── setup.py           # Database initialization script
│   └── uploads/           # PDF file storage directory
├── requirements.txt       # Python dependencies
├── design.md              # Architecture documentation
└── README.md             # This file
```

## 🔌 API Documentation

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

### Base URL
```
http://localhost:3001/api
```

### Endpoints

#### Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data

curl -X POST http://localhost:3001/api/documents/upload \
  -F "document=@/path/to/your/document.pdf"
```

**Response (201)**:
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 1,
    "filename": "medical-report.pdf",
    "filesize": 1024000,
    "created_at": "2025-01-08T12:00:00Z"
  }
}
```

#### Get All Documents
```http
GET /documents

curl http://localhost:3001/api/documents
```

**Response (200)**:
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "medical-report.pdf",
      "filesize": 1024000,
      "created_at": "2025-01-08T12:00:00Z"
    }
  ]
}
```

#### Download Document
```http
GET /documents/:id

curl http://localhost:3001/api/documents/1 --output document.pdf
```

**Response**: Binary PDF file with appropriate headers

#### Delete Document
```http
DELETE /documents/:id

curl -X DELETE http://localhost:3001/api/documents/1
```

**Response (200)**:
```json
{
  "message": "Document deleted successfully"
}
```

#### Health Check
```http
GET /health

curl http://localhost:3001/api/health
```

**Response (200)**:
```json
{
  "status": "OK",
  "timestamp": "2025-01-08T12:00:00Z"
}
```

## 📊 Database Schema

The SQLite database contains a single `documents` table:

```sql
CREATE TABLE documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,           -- Storage filename
  original_name TEXT NOT NULL,      -- Original upload name
  filepath TEXT NOT NULL,           -- Full file path
  filesize INTEGER NOT NULL,        -- Size in bytes
  created_at DATETIME NOT NULL      -- Upload timestamp
);
```

## 🔒 Security Features

- **File Type Validation**: Only PDF files are accepted
- **File Size Limits**: Maximum 10MB per file
- **Secure File Storage**: Files stored outside web root
- **Input Sanitization**: All inputs are validated and sanitized
- **Security Headers**: Helmet middleware for security headers
- **CORS Protection**: Controlled cross-origin resource sharing

## 🧪 Testing the API

### Using curl

**Upload a document**:
```bash
curl -X POST http://localhost:3001/api/documents/upload \
  -F "document=@./sample-medical-report.pdf" \
  -v
```

**List all documents**:
```bash
curl http://localhost:3001/api/documents | jq
```

**Download a document**:
```bash
curl http://localhost:3001/api/documents/1 \
  -o downloaded-document.pdf \
  -H "Accept: application/pdf"
```

**Delete a document**:
```bash
curl -X DELETE http://localhost:3001/api/documents/1 -v
```

### Using Postman

1. **Upload Document**:
   - Method: POST
   - URL: `http://localhost:3001/api/documents/upload`
   - Body: form-data
   - Key: `document` (File type)
   - Value: Select your PDF file

2. **Get Documents**:
   - Method: GET
   - URL: `http://localhost:3001/api/documents`

3. **Download Document**:
   - Method: GET
   - URL: `http://localhost:3001/api/documents/1`
   - Save response as file

4. **Delete Document**:
   - Method: DELETE
   - URL: `http://localhost:3001/api/documents/1`

## 🚀 Deployment

For production deployment:

1. **Build the frontend**:
   ```bash
   npm run build
   ```

2. **Configure environment variables**:
   ```bash
   export NODE_ENV=production
   export PORT=3001
   ```

3. **Start the production server**:
   ```bash
   node server/index.js
   ```

## 🔧 Configuration

### Python Backend Configuration

Edit `server/main.py` to modify settings:

```python
# File upload limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # Change this value (in bytes)

# Allowed MIME types
ALLOWED_MIME_TYPES = ["application/pdf"]  # Add more types if needed
```

### File Upload Limits

The FastAPI backend validates file size and type:
- Maximum file size: 10MB
- Allowed file types: PDF only
- Files are validated by both extension and magic number


### Allowed File Types

Currently only PDF files are allowed. To modify, edit the validation in `server/main.py`:

```python
def validate_pdf_file(file: UploadFile) -> bool:
    # Modify this function to allow other file types
    if not file.filename.lower().endswith('.pdf'):
        return False
    # Add additional validation logic here
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Python/FastAPI Issues**:
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python version (requires 3.8+)
python --version
```

**Port already in use**:
```bash
# Kill process using port 3001
lsof -ti:3001 | xargs kill -9

# Or for FastAPI specifically
pkill -f "uvicorn.*3001"
```

**Database locked error**:
```bash
# Remove database file and reinitialize
rm server/medical_documents.db
python server/setup.py
```

**Upload directory permissions**:
```bash
# Ensure uploads directory has proper permissions
chmod 755 server/uploads
```

### Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check server logs for error messages
4. Ensure all dependencies are properly installed

## 🔮 Future Enhancements

- User authentication and multi-user support
- Document categorization and tagging
- Full-text search within PDF documents
- Cloud storage integration (AWS S3, Google Cloud)
- HIPAA compliance features
- Mobile application
- Document versioning
- Automated backups