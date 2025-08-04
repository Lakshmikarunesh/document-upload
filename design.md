# Medical Documents Management System - Design Document

## 1. Overview

A full-stack web application designed for secure management of medical documents in a single-user environment. The system allows users to upload, view, download, and delete PDF medical documents with a focus on security, usability, and reliability.

## 2. Tech Stack Justifications

### Frontend: React.js
- **Developer Experience**: Modern component-based architecture with excellent tooling
- **Ecosystem**: Rich ecosystem with extensive libraries and community support  
- **Performance**: Virtual DOM and efficient re-rendering for smooth user interactions
- **Maintainability**: Component isolation and reusability reduce technical debt
- **Medical Context**: Proven in healthcare applications requiring reliability and user trust

### Backend: Node.js with Express
### Backend: Python 3.8+ with FastAPI
- **Modern Async Framework**: FastAPI provides excellent performance with native async/await support
- **Automatic API Documentation**: Built-in interactive Swagger UI and ReDoc documentation
- **Type Safety**: Pydantic models with full type hints ensure robust data validation
- **High Performance**: Comparable to Node.js performance with async operations
- **Medical Ecosystem**: Rich Python ecosystem for healthcare applications and compliance
- **Developer Experience**: Outstanding IDE support with type hints and auto-completion
- **Standards Compliant**: Built on OpenAPI and JSON Schema standards

### Database: SQLite
- **Simplicity**: Zero-configuration, embedded database perfect for single-user scenarios
- **Reliability**: ACID-compliant with excellent data integrity guarantees
- **Performance**: Fast read/write operations for metadata storage
- **Portability**: Single file database simplifies backup and migration
- **Medical Context**: Suitable for personal health record management

### Why Not Alternatives?
- **PostgreSQL**: Overkill for single-user scenario, requires additional infrastructure
- **MongoDB**: Document structure unnecessary for simple metadata storage
- **MySQL**: Additional complexity without benefits for this use case

## 3. Scaling Considerations (1000+ Users)

### Database Migration Path
1. **Phase 1 (1-10 users)**: Continue with SQLite
2. **Phase 2 (10-100 users)**: Migrate to PostgreSQL with connection pooling
3. **Phase 3 (100-1000+ users)**: Add read replicas and implement caching

### Infrastructure Evolution
- **File Storage**: Migrate from local storage to cloud storage (AWS S3, Azure Blob)
- **Authentication**: Implement user authentication and role-based access control
- **Load Balancing**: Add load balancer for multiple application instances
- **Monitoring**: Implement comprehensive logging and monitoring systems
- **Compliance**: Add HIPAA compliance features for medical data protection

### Performance Optimizations
- **Caching**: Redis for session management and frequently accessed data
- **CDN**: Content delivery network for static assets
- **Database Optimization**: Implement proper indexing and query optimization
- **File Processing**: Background job queue for large file operations

## 4. Architecture Overview

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   React Client  │ ◄──────────────► │  Express Server │
│                 │                  │                 │
│ - File Upload   │                  │ - API Routes    │
│ - Document List │                  │ - File Handling │
│ - Download/Del  │                  │ - Validation    │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
┌─────────────────┐                  ┌─────────────────┐
│  File System    │                  │  SQLite DB      │
│                 │                  │                 │
│ - /uploads      │                  │ - documents     │
│ - PDF Storage   │                  │ - metadata      │
└─────────────────┘                  └─────────────────┘
```

### Data Flow Description

#### Document Upload Flow
1. **Client**: User selects PDF file through drag-and-drop or file picker
2. **Validation**: Client validates file type (PDF) and size (10MB limit)
3. **Upload**: FormData sent via POST to `/api/documents/upload`
4. **Server Processing**:
   - Multer middleware handles multipart form data
   - File validation (MIME type, size limits)
   - Generate unique filename to prevent conflicts
   - Store file in `/uploads` directory
   - Insert metadata into SQLite database
5. **Response**: Return document metadata to client
6. **UI Update**: Client refreshes document list

#### Document Download Flow
1. **Client**: User clicks download button
2. **Request**: GET request to `/api/documents/:id`
3. **Server Processing**:
   - Validate document exists in database
   - Check file exists on filesystem
   - Set appropriate headers (Content-Type, Content-Disposition)
   - Stream file to client
4. **Client**: Browser handles file download

#### Document Deletion Flow
1. **Client**: User confirms deletion in modal dialog
2. **Request**: DELETE request to `/api/documents/:id`
3. **Server Processing**:
   - Validate document exists
   - Delete file from filesystem
   - Remove metadata from database
   - Return success confirmation
4. **UI Update**: Client removes document from list

## 5. API Specification

### Base URL
```
http://localhost:3001/api
```

### Endpoints

#### 1. Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data

Body:
- document: File (PDF only, max 10MB)

Response 201 (Success):
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 1,
    "filename": "medical-report.pdf",
    "filesize": 1024000,
    "created_at": "2025-01-08T12:00:00Z"
  }
}

Response 400 (Error):
{
  "error": "Only PDF files are allowed"
}
```

#### 2. Get All Documents
```http
GET /documents

Response 200:
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

#### 3. Download Document
```http
GET /documents/:id

Response 200:
Content-Type: application/pdf
Content-Disposition: attachment; filename="medical-report.pdf"
[Binary PDF Data]

Response 404:
{
  "error": "Document not found"
}
```

#### 4. Delete Document
```http
DELETE /documents/:id

Response 200:
{
  "message": "Document deleted successfully"
}

Response 404:
{
  "error": "Document not found"
}
```

#### 5. Health Check
```http
GET /health

Response 200:
{
  "status": "OK",
  "timestamp": "2025-01-08T12:00:00Z"
}
```

## 6. Database Schema

### Documents Table
```sql
CREATE TABLE documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,           -- Unique filename on disk
  original_name TEXT NOT NULL,      -- Original uploaded filename
  filepath TEXT NOT NULL,           -- Full path to file on disk
  filesize INTEGER NOT NULL,        -- File size in bytes
  created_at DATETIME NOT NULL      -- Upload timestamp
);
```

### Indexes
```sql
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
```

## 7. Security Considerations

### File Upload Security
- **File Type Validation**: Server-side MIME type checking
- **File Size Limits**: 10MB maximum to prevent abuse
- **Filename Sanitization**: Generate unique filenames to prevent path traversal
- **Storage Isolation**: Files stored outside web root directory

### API Security
- **CORS Configuration**: Controlled cross-origin resource sharing
- **Helmet Middleware**: Security headers (CSP, HSTS, etc.)
- **Input Validation**: All inputs validated and sanitized
- **Error Handling**: No sensitive information leaked in error messages

### Future Security Enhancements
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Encryption**: File encryption at rest
- **Audit Logging**: Comprehensive access logging
- **Rate Limiting**: API rate limiting to prevent abuse

## 8. Assumptions & Constraints

### Current Assumptions
- **Single User**: No authentication or multi-user support required
- **PDF Only**: Only PDF files are acceptable medical documents
- **File Size**: 10MB maximum file size for reasonable upload times
- **Local Storage**: Files stored on local filesystem (not cloud)
- **Browser Support**: Modern browsers with HTML5 file API support

### Technical Constraints
- **Storage**: Limited by local disk space
- **Concurrency**: SQLite limitations with concurrent writes
- **Backup**: Manual backup procedures required
- **Security**: Basic security suitable for personal use only

### Business Constraints
- **Compliance**: Not HIPAA compliant in current form
- **Availability**: Single point of failure with local deployment
- **Scalability**: Limited to single server deployment
- **Integration**: No integration with existing medical systems

## 9. Future Enhancements

### Phase 1: Enhanced Security
- User authentication and session management
- Role-based access control
- File encryption at rest
- Audit logging and monitoring

### Phase 2: Advanced Features
- Document categorization and tagging
- Full-text search within PDF documents
- Document versioning and history
- Automated backup and recovery

### Phase 3: Integration & Compliance
- HIPAA compliance features
- Integration with electronic health records (EHR)
- API for third-party medical applications
- Advanced analytics and reporting

### Phase 4: Scale & Performance
- Cloud deployment with high availability
- Advanced caching and performance optimization
- Machine learning for document classification
- Mobile application development