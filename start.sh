#!/bin/bash
# DataGuard Quick Start Script

echo "🛡️  DataGuard - Starting API Server..."
echo ""

# Start the server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

echo "Server starting with PID: $SERVER_PID"
echo "Waiting for server to be ready..."
sleep 3

# Test if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Server is running!"
    echo ""
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "📖 ReDoc: http://localhost:8000/redoc"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo ""
    echo "Running test suite..."
    echo ""
    python3 test_api.py
    echo ""
    echo "To stop the server: kill $SERVER_PID"
    echo "Server PID saved to .server_pid"
    echo $SERVER_PID > .server_pid
else
    echo "❌ Server failed to start. Check server.log for details."
    cat server.log
    kill $SERVER_PID 2>/dev/null
    exit 1
fi
