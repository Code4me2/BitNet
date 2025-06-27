# BitNet Inference Setup Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- GCC/Clang compiler
- CMake 3.14 or higher
- At least 4GB RAM (for 2B model)
- ~20GB free disk space (for model and build files)

## Working Setup Process

### Step 1: Clone Repository
```bash
git clone https://github.com/Code4me2/bitnet-inference.git
cd bitnet-inference/BitNet
```

### Step 2: Download Model and Build
```bash
# This downloads the model and builds BitNet for your specific CPU
python3 setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
```

This process will:
1. Download the BitNet model from HuggingFace (~3.4GB)
2. Generate CPU-specific optimized kernels
3. Compile the BitNet C++ code
4. Create the `build/bin/` directory with executables

⚠️ **Note**: This process can take 15-30 minutes and requires significant disk space.

### Step 3: Start the Server
```bash
# Basic start
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 --port 8081

# Or run in background
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 --port 8081 > server.log 2>&1 &
```

### Step 4: Test the Server
```bash
# Health check
curl http://localhost:8081/health

# Test inference
curl -X POST http://localhost:8081/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is BitNet?", "n_predict": 50}'
```

## Alternative Setup Methods

### Manual Model Download
If `setup_env.py` fails to download the model:
```bash
cd BitNet
mkdir -p models/BitNet-b1.58-2B-4T

# Download the GGUF model directly
wget -O models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  https://huggingface.co/microsoft/BitNet-b1.58-2B-4T-gguf/resolve/main/ggml-model-i2_s.gguf

# Then build only (without download)
python3 setup_env.py --build-only
```

### Pre-existing Build
If you already have BitNet built:
```bash
cd BitNet
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 --port 8081
```

## Interactive Chat

After starting the server, you can use the chat interface:
```bash
cd BitNet && ./bitnet-chat.sh
```

## API Usage

### Text Completion
```bash
curl -X POST http://localhost:8081/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "n_predict": 50,
    "temperature": 0.7
  }'
```

### Chat Completion
```bash
curl -X POST http://localhost:8081/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is BitNet?"}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }'
```

## Common Issues and Solutions

### Build Failures

**"CMake not found"**
```bash
# Ubuntu/Debian
sudo apt-get install cmake build-essential

# macOS
brew install cmake
```

**"Python dependencies missing"**
```bash
pip3 install -r requirements.txt
```

**"Out of disk space"**
- The build process needs ~20GB space
- Clear build cache: `rm -rf 3rdparty/llama.cpp/build`
- Model files alone need ~3-4GB per model

### Server Issues

**Server won't start**
```bash
# Check if port is in use
lsof -i :8081

# Kill existing processes
pkill -f llama-server

# Try a different port
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 --port 8082
```

**"Model not found" error**
```bash
# Check model path
ls -la models/BitNet-b1.58-2B-4T/

# Should see:
# ggml-model-i2_s.gguf (~3.4GB)
```

### Performance Issues

**Slow inference**
```bash
# Run kernel tuning for your CPU
python3 utils/kernel_tuning.py --quick

# Use optimal thread count
export OMP_NUM_THREADS=$(nproc)
```

## Performance Optimization

### Kernel Tuning
For optimal performance on your specific hardware:
```bash
cd BitNet

# Quick tuning (5 minutes)
python3 utils/kernel_tuning.py --quick

# Full tuning (15+ minutes)
python3 utils/kernel_tuning.py
```

### Optimized Server Start
```bash
# Set thread count to match your CPU
export OMP_NUM_THREADS=$(nproc)

# Run with optimized settings
./build/bin/llama-server \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 \
  --port 8081 \
  --threads $(nproc) \
  --ctx-size 4096 \
  --batch-size 512
```

## N8N Integration

If you're using N8N with Docker:
- N8N in Docker → BitNet on host: `http://host.docker.internal:8081`
- Both on host: `http://localhost:8081`

### Configuration in N8N
1. Add a BitNet node to your workflow
2. Set Server Mode: External Server
3. Set Server URL based on your setup
4. Use default model: BitNet b1.58 2B

## Docker Status

⚠️ **Important**: The Docker build is currently non-functional because:
1. BitNet generates CPU-specific optimized code during compilation
2. The build process is architecture-dependent
3. Docker images built on one CPU type won't work on another

For containerization, you would need to:
1. Build BitNet locally first
2. Create a runtime-only container with your pre-built binaries

See [DOCKER_STATUS.md](./DOCKER_STATUS.md) for more details.

## Verification Steps

After setup, verify everything works:

1. **Check executables exist:**
   ```bash
   ls -la build/bin/llama-server
   ```

2. **Check model exists:**
   ```bash
   ls -la models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf
   ```

3. **Test server:**
   ```bash
   ./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
     --host 0.0.0.0 --port 8081 &
   sleep 5
   curl http://localhost:8081/health
   ```

## Next Steps

1. Run benchmarks: `cd .. && ./scripts/benchmark.sh`
2. Try the chat interface: `./bitnet-chat.sh`
3. Optimize for your hardware with kernel tuning
4. Integrate with your applications via the API