# BitNet Implementation Testing Guide

## Quick Start Test (2 minutes)

Run these commands in order to verify your implementation:

```bash
# 1. Basic functionality test
python3 run_inference.py -p "Hello, BitNet!" -n 20

# 2. Performance test
python3 thread_demo.py

# 3. Optimization verification
python3 test_optimizations.py
```

## Comprehensive Testing Suite

### 1. **Basic Functionality Tests**

#### Test A: Simple Inference
```bash
# Should complete in ~3 seconds and show ~16-28 tokens/sec
python3 run_inference.py -p "What is 2+2?" -n 10
```

#### Test B: Thread Auto-Detection
```bash
# Should automatically use 12 threads
python3 run_inference.py -p "Explain threading" -n 30
```

### 2. **Performance Benchmarking**

#### Test A: Thread Scaling Analysis
```bash
# Shows performance across different thread counts
python3 thread_demo.py
```
**Expected**: Best performance at 2-4 threads for simple prompts

#### Test B: Comprehensive Benchmark
```bash
# Tests multiple prompts and configurations
python3 benchmark.py
```
**Expected**: Average 16-28 tokens/sec

#### Test C: Optimized vs Standard Comparison
```bash
python3 test_optimizations.py
```
**Expected**: Optimized version should show improvement

### 3. **Parallel Processing Tests**

#### Test A: Quick Parallel Demo
```bash
python3 parallel_inference.py
# Choose option 3
```
**Expected**: 3-4x speedup with parallel processing

#### Test B: Thread Monitoring
```bash
# Install psutil first if needed
pip install psutil

# Run monitoring test
python3 monitor_threads.py
# Choose option 3
```
**Expected**: Shows CPU utilization across cores

### 4. **Model Quality Tests**

#### Test A: Conversational Ability
```bash
python3 chat.py
# Or use the launcher:
./bitnet-chat.sh
```
Test prompts:
- "What is machine learning?"
- "Write a Python function to sort a list"
- "Explain quantum computing simply"

#### Test B: Output Consistency
```bash
# Run same prompt multiple times with temperature 0
for i in {1..3}; do
    echo "Run $i:"
    python3 run_inference.py -p "Define AI" -n 20 -temp 0
    echo "---"
done
```
**Expected**: Identical outputs (deterministic)

### 5. **Stress Tests**

#### Test A: Long Generation
```bash
# Generate 500 tokens
time python3 run_inference.py \
    -p "Write a detailed essay about the future of technology" \
    -n 500 -t 12
```
**Expected**: Completes in 20-30 seconds

#### Test B: Memory Usage
```bash
# Monitor memory during inference
python3 -c "
import subprocess
import psutil
import threading
import time

def monitor_memory():
    while monitoring:
        mem = psutil.Process().memory_info().rss / 1024 / 1024
        print(f'Memory: {mem:.1f} MB', end='\r')
        time.sleep(0.5)

monitoring = True
t = threading.Thread(target=monitor_memory)
t.start()

# Run inference
subprocess.run(['python3', 'run_inference.py', '-p', 'Test prompt', '-n', '100'])

monitoring = False
t.join()
"
```
**Expected**: ~1.5-2GB memory usage

### 6. **Integration Tests**

#### Test A: Custom Script Integration
```bash
# Create a test script
cat > integration_test.py << 'EOF'
import subprocess
import json

# Test programmatic usage
def run_inference(prompt, tokens=50):
    cmd = ["python3", "run_inference.py", "-p", prompt, "-n", str(tokens)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

# Test different types of prompts
test_cases = [
    ("Simple math", "What is 15 * 8?"),
    ("Code generation", "Write a Python hello world"),
    ("Creative", "Write a haiku about computers"),
    ("Technical", "Explain REST APIs")
]

print("🧪 Integration Test Results")
print("=" * 50)

for category, prompt in test_cases:
    print(f"\n{category}:")
    output = run_inference(prompt, 30)
    print(output[:100] + "..." if len(output) > 100 else output)
    
print("\n✅ All integration tests completed!")
EOF

python3 integration_test.py
```

### 7. **Error Handling Tests**

#### Test A: Invalid Model Path
```bash
python3 run_inference.py -m "nonexistent.gguf" -p "Test" 2>&1 | grep -i error
```
**Expected**: Clear error message

#### Test B: Resource Limits
```bash
# Test with minimal threads
OMP_NUM_THREADS=1 python3 run_inference.py -p "Test" -n 10 -t 1
```
**Expected**: Still works, just slower

## Automated Test Suite

Create and run this comprehensive test script:

```bash
cat > run_all_tests.sh << 'EOF'
#!/bin/bash
echo "🧪 BitNet Comprehensive Test Suite"
echo "=================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Function to run test
run_test() {
    local test_name=$1
    local test_cmd=$2
    echo -n "Testing $test_name... "
    
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
}

# Run tests
run_test "Basic inference" "python3 run_inference.py -p 'Hello' -n 10"
run_test "Thread detection" "python3 run_inference.py -p 'Test' -n 10 -t 0"
run_test "Optimized script" "python3 run_inference_optimized.py -p 'Test' -n 10"
run_test "Model loading" "python3 test_model_loading.py"
run_test "Performance check" "python3 test_performance.py"
run_test "Output quality" "python3 test_output_quality.py"

# Summary
echo ""
echo "Test Summary:"
echo "============="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed! BitNet is working correctly.${NC}"
else
    echo -e "\n${RED}⚠️  Some tests failed. Check the implementation.${NC}"
fi
EOF

chmod +x run_all_tests.sh
./run_all_tests.sh
```

## Performance Validation Checklist

- [ ] Achieves 16-28 tokens/sec on average
- [ ] Thread auto-detection works (uses 12 threads)
- [ ] Parallel processing shows speedup
- [ ] Memory usage stays under 2GB
- [ ] Output quality is coherent
- [ ] No errors during normal operation
- [ ] Chat interface works smoothly

## Quick Diagnostic

If you want a single command to verify everything:

```bash
echo "🔍 BitNet Quick Diagnostic" && \
echo "========================" && \
echo -n "Model exists: " && \
[ -f models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf ] && echo "✓" || echo "✗" && \
echo -n "Binary exists: " && \
[ -f build/bin/llama-cli ] && echo "✓" || echo "✗" && \
echo -n "Inference works: " && \
python3 run_inference.py -p "Test" -n 5 >/dev/null 2>&1 && echo "✓" || echo "✗" && \
echo -n "Performance: " && \
python3 -c "import subprocess, re; \
r = subprocess.run(['python3', 'run_inference.py', '-p', 'Test', '-n', '20'], \
capture_output=True, text=True); \
m = re.search(r'(\d+\.?\d*)\s*tokens per second', r.stderr); \
print(f'{float(m.group(1)):.1f} tok/s ✓' if m else '? tok/s ✗')"
```

This will quickly show if your implementation is working correctly!