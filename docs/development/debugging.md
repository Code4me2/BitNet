# BitNet Inference Debugging Guide

## Project Structure

```
bitnet-inference/
├── BitNet/                  # Core BitNet implementation
│   ├── build/bin/          # Compiled executables
│   ├── models/             # Model files
│   ├── python/             # Python scripts
│   └── CLAUDE.md           # Quick reference for debugging
├── docker-compose.yml      # Docker configuration
├── scripts/                # Helper scripts
└── docs/                   # Documentation
```

## Key Executables

All executables are in `BitNet/build/bin/`:
- `llama-server` - Main inference server
- `llama-cli` - Command line interface
- `llama-bench` - Performance benchmarking
- `llama-gguf` - GGUF file inspector

## Common Issues and Solutions

### 1. Server Won't Start

**Check if port is in use:**
```bash
lsof -i :8081
# or
ss -tlnp | grep 8081
```

**Kill existing processes:**
```bash
pkill -f llama-server
```

**Start with debug logging:**
```bash
cd BitNet
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 --port 8081 --log-verbose > server_debug.log 2>&1
```

### 2. Model Loading Issues

**Verify model exists:**
```bash
ls -la BitNet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf
```

**Check model integrity:**
```bash
cd BitNet
./build/bin/llama-gguf models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf r
```

**Test model with CLI:**
```bash
cd BitNet
./build/bin/llama-cli -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  -p "Hello world" -n 10
```

### 3. Performance Issues

**Run benchmark:**
```bash
./scripts/benchmark.sh
```

**Check thread configuration:**
```bash
echo "CPU cores: $(nproc)"
echo "Current threads: $OMP_NUM_THREADS"
```

**Monitor during inference:**
```bash
# In one terminal
htop

# In another terminal
cd BitNet
python3 python/benchmarks/run_inference.py -p "Test" -n 100
```

**Run kernel tuning:**
```bash
cd BitNet
python3 utils/kernel_tuning.py --quick
```

### 4. API/Connection Issues

**Test health endpoint:**
```bash
curl -v http://localhost:8081/health
```

**Test with minimal request:**
```bash
curl -X POST http://localhost:8081/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hi", "n_predict": 5}'
```

**Check server logs:**
```bash
tail -f BitNet/server*.log
```

### 5. Docker Issues

**Check container status:**
```bash
docker-compose ps
docker logs bitnet-server
```

**Rebuild container:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Access container shell:**
```bash
docker exec -it bitnet-server bash
```

## Debugging Commands

### System Information
```bash
# Hardware info
lscpu
free -h
df -h

# Process info
ps aux | grep llama
top -p $(pgrep llama-server)
```

### Model Inspection
```bash
cd BitNet

# View model metadata
./build/bin/llama-gguf models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf r

# List tensor names
./build/bin/llama-gguf models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf r | grep tensor
```

### Performance Testing
```bash
cd BitNet

# Quick performance test
time python3 python/benchmarks/run_inference.py -p "Test" -n 50

# Detailed benchmark
python3 python/benchmarks/benchmark.py

# Thread scaling test
for t in 1 2 4 8; do
    echo "Testing with $t threads"
    OMP_NUM_THREADS=$t python3 python/benchmarks/run_inference.py -p "Test" -n 50 -t $t
done
```

## Log Files

Key log files to check:
- `BitNet/server*.log` - Server logs
- `BitNet/logs/*.log` - Various operation logs
- `docker-compose logs` - Docker container logs

## Environment Variables

Important environment variables:
```bash
# Threading
export OMP_NUM_THREADS=$(nproc)
export MKL_NUM_THREADS=$(nproc)

# Debugging
export LLAMA_LOG_LEVEL=debug
export LLAMA_LOG_PREFIX=1

# Performance
export BITNET_KERNEL=i2_s  # or tl1, tl2
```

## Quick Diagnostic Script

Create `diagnose.sh`:
```bash
#!/bin/bash
echo "=== BitNet Diagnostic ==="
echo "Date: $(date)"
echo ""

echo "1. System Info"
echo "CPU: $(lscpu | grep 'Model name' | cut -d: -f2 | xargs)"
echo "Cores: $(nproc)"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
echo ""

echo "2. File Check"
cd BitNet
echo -n "Server binary: "
[ -f build/bin/llama-server ] && echo "✓" || echo "✗"
echo -n "Model file: "
[ -f models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf ] && echo "✓" || echo "✗"
echo ""

echo "3. Process Check"
echo -n "Server running: "
pgrep -f llama-server > /dev/null && echo "✓" || echo "✗"
echo ""

echo "4. Port Check"
echo -n "Port 8081: "
lsof -i :8081 > /dev/null 2>&1 && echo "In use" || echo "Free"
echo ""

echo "5. Quick Test"
if pgrep -f llama-server > /dev/null; then
    curl -s http://localhost:8081/health > /dev/null 2>&1 && echo "API: ✓" || echo "API: ✗"
fi
```

## Recovery Steps

If things go wrong:

1. **Stop everything:**
   ```bash
   pkill -f llama-server
   docker-compose down
   ```

2. **Clean logs:**
   ```bash
   rm BitNet/server*.log
   ```

3. **Restart fresh:**
   ```bash
   cd BitNet
   ./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
     --host 0.0.0.0 --port 8081 > server_fresh.log 2>&1 &
   ```

4. **Verify:**
   ```bash
   sleep 5
   curl http://localhost:8081/health
   ```

## Additional Resources

- Check `BitNet/CLAUDE.md` for quick command reference
- See `docs/kernel_tuning.md` for performance optimization
- Review `BitNet/TEST_IMPLEMENTATION.md` for testing procedures

## Getting Help

When reporting issues, include:
1. Output of the diagnostic script
2. Relevant log files
3. Exact commands that failed
4. System specifications