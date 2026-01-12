"""
DataGuard API
Enterprise-grade PII scrubber with zero external dependencies.
All processing happens locally for maximum security.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import io
from typing import Dict

from app.scrubber import scrubber
from app.cleaner import cleaner


# Pydantic models
class TextScrubRequest(BaseModel):
    text: str = Field(..., description="Text to scrub for PII")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Contact me at john.doe@example.com or call 555-123-4567. My SSN is 123-45-6789."
            }
        }


class TextScrubResponse(BaseModel):
    clean_text: str = Field(..., description="Text with PII redacted")
    redactions_count: int = Field(..., description="Total number of redactions made")
    details: Dict[str, int] = Field(..., description="Breakdown of redactions by type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clean_text": "Contact me at [EMAIL] or call 555-123-4567. My SSN is [SSN].",
                "redactions_count": 2,
                "details": {
                    "email": 1,
                    "ssn": 1,
                    "credit_card": 0,
                    "ipv4": 0,
                    "ipv6": 0,
                    "aws_key": 0
                }
            }
        }


# Initialize FastAPI app
app = FastAPI(
    title="DataGuard API",
    description="High-performance PII scrubber with local processing. Zero external API calls.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns 200 OK if service is running.
    """
    return {"status": "OK", "service": "DataGuard", "version": "1.0.0"}


@app.post("/scrub/text", response_model=TextScrubResponse, tags=["Scrubbing"])
async def scrub_text(request: TextScrubRequest):
    """
    Scrub PII from text input.
    
    Detects and redacts:
    - Email addresses
    - Credit card numbers (validated with Luhn algorithm)
    - Social Security Numbers (SSN)
    - IPv4 and IPv6 addresses
    - AWS API keys
    
    All processing is done locally with zero external API calls.
    """
    try:
        clean_text, redaction_info = scrubber.scrub_text(request.text)
        
        return TextScrubResponse(
            clean_text=clean_text,
            redactions_count=redaction_info['total'],
            details=redaction_info['details']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrubbing failed: {str(e)}")


@app.post("/scrub/file", tags=["Scrubbing"])
async def scrub_file(file: UploadFile = File(...)):
    """
    Remove metadata from uploaded files.
    
    Supported file types:
    - Images: JPEG, PNG, GIF, BMP, WEBP (removes EXIF/XMP data)
    - PDFs: Removes author, creator, producer metadata
    
    Returns the cleaned file as a download stream.
    All processing is done locally with zero external API calls.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Get content type
        content_type = file.content_type or "application/octet-stream"
        
        # Clean the file
        clean_bytes = cleaner.clean_file(file_bytes, content_type)
        
        # Prepare filename
        original_filename = file.filename or "cleaned_file"
        clean_filename = f"clean_{original_filename}"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(clean_bytes),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={clean_filename}",
                "X-Redactions": "metadata_removed"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File cleaning failed: {str(e)}")


@app.get("/", tags=["Info"])
async def root():
    """
    API information endpoint.
    """
    return {
        "service": "DataGuard",
        "tagline": "Enterprise PII Scrubber - 100% Local Processing",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "scrub_text": "/scrub/text",
            "scrub_file": "/scrub/file",
            "docs": "/docs"
        },
        "features": [
            "Email redaction",
            "Credit card detection (Luhn validated)",
            "SSN scrubbing",
            "IP address removal",
            "AWS key detection",
            "Image metadata stripping (EXIF/XMP)",
            "PDF metadata removal"
        ],
        "security": "Zero external API calls - All processing local"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
