# BitNet Kernel Tuning Guide

## Overview

BitNet uses optimized computational kernels for efficient 1-bit LLM inference. The performance of these kernels depends heavily on the specific hardware architecture, cache sizes, and instruction sets available. Kernel tuning allows you to find the optimal configuration for your specific CPU.

## What is Kernel Tuning?

Kernel tuning optimizes three key parameters that control how matrix multiplication is tiled and computed:

- **BM (Block M)**: Controls the row dimension tiling (typical values: 128, 160, 256, 320)
- **BK (Block K)**: Controls the column dimension tiling (typical values: 64, 96, 128, 192)
- **bm (micro-tile m)**: Controls the micro-kernel size (32 for x86, 32 or 64 for ARM)

These parameters affect:
- Cache utilization efficiency
- Memory bandwidth usage
- SIMD instruction throughput
- Overall tokens/second performance

## Quick Start

### 1. Run Quick Tuning (Recommended)

```bash
# Tests 3-4 configurations, takes ~5 minutes
python utils/kernel_tuning.py --quick
```

### 2. Apply Best Configuration

The script will output the best configuration found. Apply it:

```bash
# For x86 CPUs (Intel/AMD)
python utils/codegen_tl2.py --model bitnet_b1_58-3B --BM 320,320,320 --BK 128,128,128 --bm 32,32,32

# For ARM CPUs
python utils/codegen_tl1.py --model bitnet_b1_58-3B --BM 160,320,320 --BK 64,128,64 --bm 32,64,32

# Rebuild with new kernels
bash rebuild_bitnet.sh
```

### 3. Restart Server

```bash
pkill -f llama-server
./build/bin/llama-server -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf --host 0.0.0.0 --port 8081
```

## Full Tuning

For comprehensive optimization (tests 10+ configurations):

```bash
python utils/kernel_tuning.py

# Or with verbose output
python utils/kernel_tuning.py -v
```

## Understanding Results

The tuning output shows:

```
Top 5 configurations:
Rank   BM         BK         bm         Tokens/s    
--------------------------------------------------
1      320        128        32         24.05       
2      160        96         32         19.59       
3      256        96         32         18.43       
```

- **Tokens/s**: Higher is better (measures inference speed)
- **Best configuration**: Saved to `best_kernel_config.json`

## Performance Gains

Typical improvements from kernel tuning:
- **10-30%** performance increase over default configurations
- **Better cache utilization** reducing memory bottlenecks
- **Improved energy efficiency** through optimized compute patterns

## Architecture-Specific Notes

### Intel CPUs
- Modern Intel CPUs (12th gen+) benefit from larger BM values (256-320)
- AVX2/AVX-512 capable CPUs see best results with BK=128 or BK=192
- Intel Ultra series CPUs show 20-25% improvements with tuning

### AMD CPUs
- Zen3+ architectures prefer BM=256, BK=128
- Older Zen architectures may perform better with smaller tiles

### ARM CPUs
- Apple Silicon benefits from mixed configurations (different BM/BK per kernel)
- Raspberry Pi and similar devices need smaller tiles due to cache constraints

## Constraints

The kernel parameters must satisfy:
- **TL1 (ARM)**: M % BM == 0, K % BK == 0, BM % bm == 0, bm ∈ {32, 64}
- **TL2 (x86)**: M % BM == 0, K % BK % 32 == 0, BM % bm == 0, bm = 32

Where M and K are the matrix dimensions from the model architecture.

## Troubleshooting

### "Codegen failed" errors
- Ensure parameters meet the constraints above
- Check that BM divides evenly into model dimensions (3200, 8640)

### No performance improvement
- Try the full tuning mode instead of quick
- Ensure no other processes are using CPU during benchmarking
- Check that the model is using the newly generated kernels

### Build errors after tuning
- Run `bash rebuild_bitnet.sh` to ensure clean build
- Check `include/kernel_config.ini` for valid configuration

## Advanced Usage

### Custom configurations

Create your own test configurations:

```python
from utils.kernel_tuning import KernelTuner

tuner = KernelTuner("models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf")
config = {"BM": [256, 256, 256], "BK": [192, 192, 192], "bm": [32, 32, 32]}
result = tuner.benchmark_config(config)
print(f"Performance: {result['tokens_per_second']} tokens/s")
```

### Automated tuning in CI/CD

```bash
# Run tuning and apply best config automatically
python utils/kernel_tuning.py --quick
BEST_CONFIG=$(python -c "import json; c=json.load(open('best_kernel_config.json')); print(f\"--BM {','.join(map(str,c['config']['BM']))} --BK {','.join(map(str,c['config']['BK']))} --bm {','.join(map(str,c['config']['bm']))}\")")
python utils/codegen_tl2.py --model bitnet_b1_58-3B $BEST_CONFIG
bash rebuild_bitnet.sh
```

## Future Improvements

- Auto-detection of optimal configurations based on CPU model
- Integration with setup_env.py for automatic tuning during setup
- Per-model kernel configurations (2B, 3B, 8B specific)
- GPU kernel tuning support (coming soon)