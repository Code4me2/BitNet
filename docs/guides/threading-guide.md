# BitNet Threading Guide

## Overview

This guide explains how to maximize CPU utilization with BitNet inference, particularly for multi-core systems. BitNet's optimized kernels have unique threading characteristics that differ from traditional models.

## Key Concepts

### BitNet Threading Characteristics
- **Memory-bound**: BitNet is primarily limited by memory bandwidth, not compute
- **Cache efficiency**: Fewer threads can mean better cache utilization
- **Kernel optimization**: Different kernels (I2_S, TL1, TL2) have different threading behaviors

### Important Finding
**For BitNet, running multiple parallel processes often outperforms a single heavily-threaded process.**

## Quick Start

### Single Inference (Auto-optimized)
```bash
# Automatically detects and uses optimal threads
python3 run_inference.py -p "Your prompt here" -n 100

# Or explicitly set threads
python3 run_inference.py -p "Your prompt here" -n 100 -t 4
```

### Parallel Processing (Multiple Prompts)
```bash
# Process multiple prompts simultaneously
python3 parallel_inference.py

# Or use manual parallel execution
for i in {1..6}; do
    OMP_NUM_THREADS=2 python3 run_inference.py -p "Prompt $i" -n 50 &
done
wait
```

## Configuration Strategies

### Recommended Configurations by Use Case

| Use Case | Configuration | Threads/Process | Example |
|----------|--------------|-----------------|---------|
| Single simple prompt | Low thread count | 2-4 | `python3 run_inference.py -p "prompt" -t 4` |
| Single complex prompt | High thread count | 8-12 | `python3 run_inference.py -p "prompt" -t 12` |
| Multiple prompts | Parallel processes | 2-4 each | `6 processes × 2 threads` |
| Real-time server | Balanced | 3-4 each | `4 processes × 3 threads` |

### Why Fewer Threads Can Be Better

1. **Cache Efficiency**: BitNet's 1-bit operations are extremely cache-friendly
2. **Memory Bandwidth**: The bottleneck is memory access, not computation
3. **Kernel Design**: Optimized kernels may saturate memory bandwidth with fewer threads

## Implementation Examples

### 1. Parallel Batch Processing
```python
#!/usr/bin/env python3
import concurrent.futures
import subprocess
import os

def process_prompt(prompt, threads=2):
    """Process a single prompt with specified threads"""
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(threads)
    
    cmd = ["python3", "run_inference.py", "-p", prompt, "-n", "50", "-t", str(threads)]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.stdout

# Process multiple prompts in parallel
prompts = ["What is AI?", "Explain quantum computing", "Describe photosynthesis"]
with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(lambda p: process_prompt(p, 2), prompts))
```

### 2. Thread Pool Server
```python
#!/usr/bin/env python3
import asyncio
from concurrent.futures import ThreadPoolExecutor

class BitNetServer:
    def __init__(self, max_workers=3, threads_per_worker=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.threads_per_worker = threads_per_worker
        
    async def handle_request(self, prompt):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, 
            self.generate, 
            prompt
        )
        return result
```

### 3. Finding Optimal Thread Count
```bash
#!/bin/bash
# Test different thread configurations
for threads in 1 2 4 6 8 10 12; do
    echo -n "Testing $threads threads: "
    time OMP_NUM_THREADS=$threads python3 run_inference.py \
        -p "Test prompt" -n 100 -t $threads > /dev/null 2>&1
done
```

## Environment Optimization

### Essential Environment Variables
```bash
# Thread count
export OMP_NUM_THREADS=4

# Thread binding for consistent performance
export OMP_PROC_BIND=true
export OMP_PLACES=cores

# Active wait policy for lower latency
export OMP_WAIT_POLICY=active
```

### CPU Affinity (Advanced)
```bash
# Pin to specific cores
taskset -c 0-5 python3 run_inference.py -p "Process 1" -t 6 &
taskset -c 6-11 python3 run_inference.py -p "Process 2" -t 6 &
```

## Performance Tips

### 1. Start with Fewer Threads
- Test with 2-4 threads first
- Increase only if you see performance gains
- Monitor actual CPU utilization

### 2. Use Parallel Processes for Batch Work
- Instead of 1 process with 12 threads, try 6 processes with 2 threads
- This often provides better total throughput

### 3. Monitor and Adjust
```bash
# Real-time monitoring
htop  # Watch CPU usage per core

# Detailed thread analysis
pidstat -t -p $(pgrep python3) 1
```

### 4. Consider Prompt Complexity
- Simple prompts: 2-4 threads
- Complex/long prompts: 6-12 threads
- Adjust based on your specific workload

## Example Configurations

### For 12-Core System
```bash
# Option 1: Maximum single-task performance
OMP_NUM_THREADS=12 python3 run_inference.py -p "Complex prompt" -n 500

# Option 2: Balanced parallel processing (recommended)
# 3 processes × 4 threads each
for i in {1..3}; do
    OMP_NUM_THREADS=4 python3 run_inference.py -p "Prompt $i" &
done

# Option 3: High concurrency for small tasks
# 6 processes × 2 threads each
for i in {1..6}; do
    OMP_NUM_THREADS=2 python3 run_inference.py -p "Task $i" -n 20 &
done
```

## Troubleshooting

### Issue: High CPU usage but slow inference
- **Cause**: Thread contention or poor cache utilization
- **Solution**: Reduce thread count

### Issue: Low CPU usage
- **Cause**: Memory bandwidth saturation
- **Solution**: This is normal for BitNet; it's memory-bound

### Issue: Inconsistent performance
- **Cause**: Thread migration or thermal throttling
- **Solution**: Use `OMP_PROC_BIND=true` and monitor temperatures

## Summary

For optimal BitNet performance:
1. **Test different thread counts** - More threads isn't always better
2. **Use parallel processes** - Often better than single multi-threaded process
3. **Monitor actual performance** - Use real metrics, not just CPU usage
4. **Adjust to your workload** - Simple vs complex prompts need different configs

Remember: BitNet's 1-bit design means traditional multi-threading wisdom may not apply. Always benchmark your specific use case.