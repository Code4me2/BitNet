#!/bin/bash
#
# BitNet Chat Launcher
# Easy-to-use script to start the BitNet chat interface
#

# Set thread optimization for 12-core CPU
export OMP_NUM_THREADS=12
export MKL_NUM_THREADS=12

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🤖 BitNet B1.58 2B4T Chat Interface${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "python/benchmarks/run_inference.py" ]; then
    echo -e "${RED}❌ Error: run_inference.py not found!${NC}"
    echo "Please run this script from the BitNet directory."
    exit 1
fi

# Check if model exists
MODEL_PATH="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${RED}❌ Error: Model file not found!${NC}"
    echo "Expected location: $MODEL_PATH"
    echo ""
    echo "Please run the setup process first:"
    echo "  python3 setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s"
    exit 1
fi

# System info
echo -e "${GREEN}✓ Model found:${NC} $(basename $MODEL_PATH)"
echo -e "${GREEN}✓ CPU threads:${NC} $OMP_NUM_THREADS"
echo -e "${GREEN}✓ System:${NC} $(uname -s) $(uname -m)"
echo ""

# Launch chat
echo -e "${BLUE}Starting chat interface...${NC}"
echo ""

# Run the chat interface
python3 python/chat/chat.py

# Exit message
echo ""
echo -e "${BLUE}Thanks for using BitNet Chat!${NC}"