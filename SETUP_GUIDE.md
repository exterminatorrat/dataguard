# 🛠️ DataGuard Setup Guide

Complete deployment instructions for DataGuard Enterprise License.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Testing & Validation](#testing--validation)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🏠 Local Development Setup

### Prerequisites
- Python 3.11 or higher
- pip package manager
- (Optional) Docker for containerized testing

### Installation Steps

```bash
# 1. Navigate to project directory
cd DataGuard

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Locally

```bash
# Health check
curl http://localhost:8000/health

# Test text scrubbing
curl -X POST http://localhost:8000/scrub/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Email me at test@example.com or call 555-1234. Card: 4532-1488-0343-6467"}'

# Test file scrubbing (requires a test image)
curl -X POST http://localhost:8000/scrub/file \
  -F "file=@test_image.jpg" \
  --output cleaned_image.jpg
```

---

## 🐳 Docker Deployment

### Build the Image

```bash
# Build the Docker image
docker build -t dataguard:latest .

# Verify the build
docker images | grep dataguard
```

### Run the Container

```bash
# Run in foreground (for testing)
docker run -p 8000:8000 dataguard:latest

# Run in background (production)
docker run -d \
  --name dataguard \
  -p 8000:8000 \
  --restart unless-stopped \
  dataguard:latest

# Check logs
docker logs dataguard

# Check status
docker ps | grep dataguard
```

### Docker Compose (Recommended for Production)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  dataguard:
    build: .
    image: dataguard:latest
    container_name: dataguard
    ports:
      - "8000:8000"
    restart: unless-stopped
    environment:
      - WORKERS=4
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

Run with:
```bash
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### AWS ECS Deployment

#### 1. Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name dataguard

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag dataguard:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/dataguard:latest

# Push to ECR
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/dataguard:latest
```

#### 2. Create ECS Task Definition

```json
{
  "family": "dataguard",
  "containerDefinitions": [
    {
      "name": "dataguard",
      "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/dataguard:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 10
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512"
}
```

#### 3. Create ECS Service

```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name dataguard \
  --task-definition dataguard \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/your-project/dataguard

# Deploy to Cloud Run
gcloud run deploy dataguard \
  --image gcr.io/your-project/dataguard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10
```

### Fly.io (Easiest)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch --name dataguard

# Deploy
fly deploy

# Scale
fly scale count 2

# View status
fly status
```

### Railway

```bash
# Install Railway CLI
npm install -g railway

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# View URL
railway open
```

---

## ✅ Testing & Validation

### Automated Test Suite

Create `test.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000"

echo "Testing DataGuard API..."

# Test 1: Health check
echo "1. Health check..."
curl -s $API_URL/health | grep -q "OK" && echo "✅ Health check passed" || echo "❌ Health check failed"

# Test 2: Text scrubbing
echo "2. Text scrubbing..."
RESPONSE=$(curl -s -X POST $API_URL/scrub/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Email: test@example.com, SSN: 123-45-6789"}')

echo $RESPONSE | grep -q "\[EMAIL\]" && echo "✅ Email redaction passed" || echo "❌ Email redaction failed"
echo $RESPONSE | grep -q "\[SSN\]" && echo "✅ SSN redaction passed" || echo "❌ SSN redaction failed"

# Test 3: Credit card validation
echo "3. Credit card validation..."
RESPONSE=$(curl -s -X POST $API_URL/scrub/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Card: 4532-1488-0343-6467"}')

echo $RESPONSE | grep -q "\[CREDIT_CARD\]" && echo "✅ Credit card redaction passed" || echo "❌ Credit card redaction failed"

echo "Testing complete!"
```

Run with:
```bash
chmod +x test.sh
./test.sh
```

---

## ⚙️ Production Configuration

### Environment Variables

Create `.env` file:

```bash
# Server Configuration
WORKERS=4
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=info

# CORS (if needed)
CORS_ORIGINS=["https://yourdomain.com"]
```

### Update `main.py` for Production

Add CORS middleware if needed:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/dataguard`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for large file uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        
        # Increase upload size
        client_max_body_size 50M;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/dataguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

---

## 📊 Monitoring & Maintenance

### Health Monitoring Script

Create `monitor.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000"
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

while true; do
    if ! curl -s -f $API_URL/health > /dev/null; then
        echo "DataGuard is DOWN!"
        
        # Send alert (Slack example)
        curl -X POST $WEBHOOK_URL \
            -H 'Content-Type: application/json' \
            -d '{"text": "🚨 DataGuard API is DOWN!"}'
        
        # Restart container
        docker restart dataguard
    fi
    
    sleep 60
done
```

Run in background:
```bash
nohup ./monitor.sh &
```

### Log Rotation

Create `/etc/logrotate.d/dataguard`:

```
/var/log/dataguard/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Prometheus Metrics (Optional)

Add to `requirements.txt`:
```
prometheus-fastapi-instrumentator==6.1.0
```

Update `main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🔒 Security Hardening

### 1. Rate Limiting

Add to `requirements.txt`:
```
slowapi==0.1.9
```

Update `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/scrub/text")
@limiter.limit("100/minute")
async def scrub_text(request: Request, data: TextScrubRequest):
    # ... existing code
```

### 2. API Key Authentication

```python
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
```

### 3. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 🆘 Troubleshooting

### Issue: Container won't start

```bash
# Check logs
docker logs dataguard

# Check if port is in use
lsof -i :8000

# Rebuild image
docker build --no-cache -t dataguard:latest .
```

### Issue: High memory usage

```bash
# Reduce worker count in Dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### Issue: Slow file processing

```bash
# Increase timeout in nginx
proxy_read_timeout 600;

# Increase Docker memory limit
docker run -m 1g dataguard:latest
```

---

## 📞 Support

For enterprise support or custom integrations:
- Email: [your-email@example.com]
- Documentation: [GitHub repo]

---

**You're all set! DataGuard is now protecting your data pipeline. 🛡️**
