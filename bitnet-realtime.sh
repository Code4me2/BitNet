#!/bin/bash
# BitNet Real-time Chat Launcher

echo "🚀 Starting BitNet Real-time Chat..."
echo ""

# Set thread optimization (10 threads found to be optimal)
export OMP_NUM_THREADS=10
export PYTHONUNBUFFERED=1

# Run the chat
python3 chat_realtime.py
