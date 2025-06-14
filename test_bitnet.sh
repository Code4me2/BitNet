#!/bin/bash
#
# Quick BitNet Testing Script
# Run various tests to verify your implementation
#

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 BitNet Quick Test Suite${NC}"
echo "=========================="

# Function to run test
run_test() {
    local test_name=$1
    local test_cmd=$2
    echo -n "• $test_name: "
    
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Basic tests
echo
echo "1. Basic Checks:"
run_test "Model file exists" "[ -f models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf ]"
run_test "Binary exists" "[ -f build/bin/llama-cli ]"
run_test "Python scripts exist" "[ -f python/benchmarks/run_inference.py ]"

# Functionality tests
echo
echo "2. Functionality Tests:"
run_test "Basic inference" "python3 python/benchmarks/run_inference.py -p 'Hello' -n 5"
run_test "Thread auto-detection" "python3 python/benchmarks/run_inference.py -p 'Test' -n 5 -t 0"

# Performance test
echo
echo "3. Performance Test:"
echo -n "• Tokens per second: "
PERF=$(python3 python/benchmarks/run_inference.py -p "Performance test" -n 30 2>&1 | grep -o '[0-9.]*\s*tokens per second' | grep -o '^[0-9.]*' | tail -1)
if [ ! -z "$PERF" ]; then
    echo -e "${GREEN}${PERF} tok/s${NC}"
    
    # Check if performance is in expected range
    if (( $(echo "$PERF > 10" | bc -l) )); then
        echo -e "  ${GREEN}✓ Performance is good!${NC}"
    else
        echo -e "  ${YELLOW}⚠ Performance is below expected${NC}"
    fi
else
    echo -e "${RED}Could not measure${NC}"
fi

# Advanced tests
echo
echo "4. Advanced Features:"
run_test "Chat script exists" "[ -f python/chat/chat.py ]"
run_test "Benchmark script exists" "[ -f python/benchmarks/benchmark.py ]"
run_test "Parallel inference script" "[ -f parallel_inference.py ]"

# Summary
echo
echo "=========================="
echo -e "${BLUE}Test Summary${NC}"
echo

# Provide recommendations based on results
echo "📋 Recommended tests to run manually:"
echo
echo "1. Interactive chat test:"
echo "   python3 python/chat/chat.py"
echo
echo "2. Thread optimization test:"
echo "   python3 thread_demo.py"
echo
echo "3. Parallel processing demo:"
echo "   python3 parallel_inference.py"
echo
echo "4. Full benchmark suite:"
echo "   python3 python/benchmarks/benchmark.py"
echo
echo "For detailed testing guide, see: TEST_IMPLEMENTATION.md"