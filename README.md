# 🛡️ DataGuard - Enterprise PII Scrubber API

**The AI Firewall. Sanitize data before it hits ChatGPT. 100% On-Premise.**

DataGuard is a high-performance API that scrubs Personally Identifiable Information (PII) and metadata from text and files. Built for enterprise compliance with **zero external API calls** - all processing happens locally for maximum security.

## 🚀 Features

### Text Scrubbing
- ✉️ **Email addresses** → `[EMAIL]`
- 💳 **Credit card numbers** (Luhn validated) → `[CREDIT_CARD]`
- 🔢 **Social Security Numbers** → `[SSN]`
- 🌐 **IPv4 & IPv6 addresses** → `[IP_ADDRESS]`
- 🔑 **AWS API keys** → `[AWS_KEY]`

### File Cleaning
- 📷 **Images**: Removes EXIF/XMP metadata (JPEG, PNG, GIF, BMP, WEBP)
- 📄 **PDFs**: Strips author, creator, producer metadata

## 💡 Why DataGuard?

- **🔒 100% Local Processing**: No data ever leaves your infrastructure
- **⚡ High Performance**: Built with FastAPI and async processing
- **🐳 Docker Ready**: Production-ready container included
- **📊 Detailed Reporting**: Get redaction counts and breakdowns
- **🎯 Enterprise Grade**: Luhn algorithm validation for credit cards
- **🔓 Open Source**: Free to use and modify

## 📦 Quick Start

### Using Docker (Recommended)

```bash
# Build the image
docker build -t dataguard .

# Run the container
docker run -p 8000:8000 dataguard

# API is now available at http://localhost:8000
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```

### Scrub Text
```bash
POST /scrub/text
Content-Type: application/json

{
  "text": "Contact me at john@example.com. My card is 4532-1488-0343-6467."
}
```

**Response:**
```json
{
  "clean_text": "Contact me at [EMAIL]. My card is [CREDIT_CARD].",
  "redactions_count": 2,
  "details": {
    "email": 1,
    "credit_card": 1,
    "ssn": 0,
    "ipv4": 0,
    "ipv6": 0,
    "aws_key": 0
  }
}
```

### Scrub File
```bash
POST /scrub/file
Content-Type: multipart/form-data

file: [your_image.jpg or document.pdf]
```

Returns the cleaned file as a download stream.

## 🌐 Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
DataGuard/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI routes and app config
│   ├── scrubber.py      # Text PII detection & redaction
│   └── cleaner.py       # File metadata stripping
├── Dockerfile           # Production container
├── requirements.txt     # Python dependencies
└── README.md
```

## 🎯 Use Cases

- **LLM Input Sanitization**: Clean prompts before sending to ChatGPT/Claude
- **Compliance Automation**: Ensure GDPR/CCPA compliance automatically
- **Document Sharing**: Strip metadata before sharing files externally
- **Data Pipeline Protection**: Add as middleware in your data flow
- **Developer Tools**: Integrate into CI/CD for automated data sanitization

## 🔒 Security Features

- ✅ Zero external API calls
- ✅ No data persistence
- ✅ Runs in isolated container
- ✅ Non-root user in Docker
- ✅ Minimal attack surface (python-slim base)

## 📊 Performance

- **Async Processing**: FastAPI + Uvicorn
- **Multi-worker**: 4 workers by default in Docker
- **Optimized Regex**: Pre-compiled patterns
- **Streaming Response**: Efficient file handling

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn with async workers
- **Text Processing**: Python `re` module + Luhn algorithm
- **Image Processing**: Pillow 10.2.0
- **PDF Processing**: PyPDF2 3.0.1
- **Validation**: Pydantic 2.5.3

## � Deployment

DataGuard can be deployed anywhere Docker runs:

```bash
# Docker
docker build -t dataguard .
docker run -p 8000:8000 dataguard

# Docker Compose
docker-compose up -d
```

Cloud platforms: AWS ECS, Google Cloud Run, Azure Container Instances, Fly.io, Railway, Render, etc.

## 📝 License

MIT License - Free to use, modify, and distribute.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**DataGuard - Local PII scrubbing for secure AI applications.**
