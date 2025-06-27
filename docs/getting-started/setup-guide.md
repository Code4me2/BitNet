# BitNet Setup Guide

## Current Working Configuration

### 1. BitNet Server Status
- **Status**: ✅ Running
- **Port**: 8081 (changed to avoid conflict with web services)
- **Model**: BitNet-b1.58-2B-4T (2.4B parameters)
- **Location**: `/home/manzanita/coding/bitnet-inference/BitNet/`
- **Kernel Configuration**: Optimized for Intel Ultra 7 (23% performance improvement)
  - BM: 320, BK: 128, bm: 32

### 2. Start BitNet Server

```bash
cd /home/manzanita/coding/bitnet-inference/BitNet
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf --host 0.0.0.0 --port 8081
```

Or run in background:
```bash
cd /home/manzanita/coding/bitnet-inference/BitNet
(./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf --host 0.0.0.0 --port 8081 > bitnet-server.log 2>&1 &)
```

### 3. Test BitNet Server

Health check:
```bash
curl http://localhost:8081/health
# Expected: {"status":"ok"}
```

Completion test:
```bash
curl -X POST http://localhost:8081/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "n_predict": 50,
    "temperature": 0.7
  }'
```

Chat test:
```bash
echo '{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is BitNet?"}
  ],
  "temperature": 0.7,
  "max_tokens": 50
}' | curl -X POST http://localhost:8081/chat/completions \
  -H "Content-Type: application/json" \
  -d @-
```

### 4. N8N Integration

#### Start N8N Services
```bash
cd /home/manzanita/coding/data-compose
docker compose up -d
```

#### Access Points
- N8N Interface: http://localhost:5678
- Web Interface: http://localhost:8080

#### BitNet Node Configuration in N8N
1. In N8N, add a BitNet node to your workflow
2. Configure:
   - **Server Mode**: External Server
   - **Server URL**: `http://host.docker.internal:8081`
   - **Model**: BitNet b1.58 2B (default)

### 5. Important Notes

#### Port Configuration
- BitNet server runs on port 8081 to avoid conflicts
- Web interface uses the standard port 8080
- This separation allows both services to run simultaneously

#### Docker Networking
- From N8N container, access BitNet using: `http://host.docker.internal:8081`
- This allows Docker containers to access host services

#### Multiple Server Instances
- Check for running instances: `ps aux | grep llama-server`
- Kill duplicates: `pkill -f llama-server`

### 6. Performance Optimization

#### Kernel Tuning (NEW)
BitNet now includes kernel tuning for hardware-specific optimization:

```bash
# Quick tuning (5 minutes, tests 3-4 configurations)
python utils/kernel_tuning.py --quick

# Full tuning (15+ minutes, tests 10+ configurations)
python utils/kernel_tuning.py

# Apply best configuration permanently
python utils/codegen_tl2.py --model bitnet_b1_58-3B --BM 320,320,320 --BK 128,128,128 --bm 32,32,32
bash rebuild_bitnet.sh
```

Current optimized configuration achieves **~24 tokens/s** (23% improvement over default).

#### Runtime Settings
For optimal performance:
```bash
# Set thread count to match your CPU cores
export OMP_NUM_THREADS=6

# Run with optimized settings
./build/bin/llama-server \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  --host 0.0.0.0 \
  --port 8081 \
  --threads 6 \
  --threads-batch 6 \
  --ctx-size 4096 \
  --batch-size 512
```

### 7. Troubleshooting

#### Server won't start
- Check if port is in use: `lsof -i :8081`
- Kill existing processes: `pkill -f llama-server`

#### N8N can't connect
- Ensure BitNet server is running
- Use `http://host.docker.internal:8081` in N8N node
- Check Docker networking: `docker network ls`

#### Model loading errors
- Verify model path exists
- Check file permissions
- Ensure sufficient RAM (needs ~1.5GB)

### 8. Next Steps

1. Create N8N workflows using the BitNet node
2. Test different models (download 3B or Large models)
3. Optimize performance with kernel tuning
4. Set up production deployment with systemd service