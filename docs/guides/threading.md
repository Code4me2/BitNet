# BitNet 12-Core Threading Utilization Guide

## Overview

Your Intel Core Ultra 7 155U has 12 threads (6 physical cores with hyperthreading). Here's how to maximize their utilization for BitNet inference.

## Current Threading Implementation

The optimizations already implemented:
- Auto-detection of 12 threads in `run_inference.py`
- Environment variables set automatically (OMP_NUM_THREADS=12)
- Thread affinity enabled (OMP_PROC_BIND=true)

## 1. Single Inference Optimization

### Basic Usage (Already Optimized)
```bash
# Automatically uses 12 threads
python3 run_inference.py -p "Your prompt here" -n 100

# Or explicitly set threads
python3 run_inference.py -p "Your prompt here" -n 100 -t 12
```

### With Environment Setup
```bash
# Source the environment for persistent settings
source bitnet-env.sh
python3 run_inference.py -p "Your prompt" -n 100
```

## 2. Parallel Inference (Multiple Prompts)

### Batch Processing Script
Create a script to process multiple prompts in parallel:

```python
#!/usr/bin/env python3
# parallel_inference.py
import concurrent.futures
import subprocess
import time
import os
from typing import List, Dict

def run_single_inference(prompt: str, max_tokens: int = 50) -> Dict:
    """Run inference on a single prompt"""
    start_time = time.time()
    
    # Use fewer threads per process when running in parallel
    threads_per_process = 4  # 12 threads / 3 parallel processes
    
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(threads_per_process)
    
    cmd = [
        "python3", "run_inference.py",
        "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
        "-p", prompt,
        "-n", str(max_tokens),
        "-t", str(threads_per_process)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    return {
        "prompt": prompt,
        "output": result.stdout,
        "time": time.time() - start_time,
        "success": result.returncode == 0
    }

def parallel_inference(prompts: List[str], max_workers: int = 3):
    """Process multiple prompts in parallel"""
    print(f"Processing {len(prompts)} prompts with {max_workers} workers...")
    
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_prompt = {executor.submit(run_single_inference, prompt): prompt 
                           for prompt in prompts}
        
        for future in concurrent.futures.as_completed(future_to_prompt):
            result = future.result()
            results.append(result)
            print(f"✓ Completed: {result['prompt'][:50]}... ({result['time']:.2f}s)")
    
    return results

# Example usage
if __name__ == "__main__":
    prompts = [
        "What is machine learning?",
        "Explain quantum computing",
        "How does photosynthesis work?",
        "What are the benefits of exercise?",
        "Describe the water cycle",
        "What is artificial intelligence?"
    ]
    
    # Process 3 prompts simultaneously, each using 4 threads
    results = parallel_inference(prompts, max_workers=3)
    
    print("\nResults Summary:")
    total_time = sum(r['time'] for r in results)
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per prompt: {total_time/len(prompts):.2f}s")
```

## 3. Streaming Server with Thread Pool

### Multi-Client Server
```python
#!/usr/bin/env python3
# threaded_server.py
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor
import json

class BitNetServer:
    def __init__(self, max_workers=3, threads_per_worker=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.threads_per_worker = threads_per_worker
        
    def generate(self, prompt, max_tokens=100):
        """Generate text using BitNet"""
        env = os.environ.copy()
        env['OMP_NUM_THREADS'] = str(self.threads_per_worker)
        
        cmd = [
            "python3", "run_inference.py",
            "-p", prompt,
            "-n", str(max_tokens),
            "-t", str(self.threads_per_worker)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.stdout
    
    async def handle_request(self, prompt):
        """Handle async request"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self.generate, prompt)
        return result

# Example: Handle multiple concurrent requests
async def main():
    server = BitNetServer(max_workers=3, threads_per_worker=4)
    
    # Simulate concurrent requests
    prompts = ["Tell me about AI", "What is Python?", "Explain clouds"]
    tasks = [server.handle_request(p) for p in prompts]
    
    results = await asyncio.gather(*tasks)
    for i, result in enumerate(results):
        print(f"Result {i+1}: {result[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. Thread Configuration Strategies

### Strategy 1: Maximum Throughput (Single Process)
```bash
# Use all 12 threads for one inference
export OMP_NUM_THREADS=12
python3 run_inference.py -p "Long complex prompt" -n 500
```

### Strategy 2: Balanced Parallel Processing
```bash
# 3 processes × 4 threads each
# Process 1
OMP_NUM_THREADS=4 python3 run_inference.py -p "Prompt 1" &
# Process 2  
OMP_NUM_THREADS=4 python3 run_inference.py -p "Prompt 2" &
# Process 3
OMP_NUM_THREADS=4 python3 run_inference.py -p "Prompt 3" &
wait
```

### Strategy 3: High Concurrency
```bash
# 6 processes × 2 threads each (for many small tasks)
for i in {1..6}; do
    OMP_NUM_THREADS=2 python3 run_inference.py -p "Task $i" -n 20 &
done
wait
```

## 5. CPU Affinity Optimization

### Pin Threads to Specific Cores
```bash
# Use taskset to pin to specific CPU cores
# Cores 0-5 for process 1, cores 6-11 for process 2
taskset -c 0-5 python3 run_inference.py -p "Process 1" -t 6 &
taskset -c 6-11 python3 run_inference.py -p "Process 2" -t 6 &
wait
```

### NUMA-Aware Execution (if applicable)
```bash
# Check NUMA topology
numactl --hardware

# Run with NUMA optimization
numactl --cpunodebind=0 --membind=0 python3 run_inference.py -p "Prompt"
```

## 6. Monitoring Thread Utilization

### Real-time CPU Monitoring
```bash
# Watch CPU usage per core
htop  # Press F2 > Display options > Show custom thread names

# Or use mpstat
watch -n 1 'mpstat -P ALL 1 1'
```

### Thread Performance Analysis
```bash
# Create monitoring script
cat > monitor_inference.sh << 'EOF'
#!/bin/bash
# Start monitoring
pidstat -t -p ALL 1 > cpu_stats.log &
PIDSTAT_PID=$!

# Run inference
python3 run_inference.py -p "Test prompt for monitoring" -n 100

# Stop monitoring
kill $PIDSTAT_PID

# Analyze results
echo "Thread utilization summary:"
grep "Average" cpu_stats.log
EOF

chmod +x monitor_inference.sh
./monitor_inference.sh
```

## 7. Advanced: Thread Pool Manager

```python
#!/usr/bin/env python3
# thread_pool_manager.py
import os
import threading
import queue
import subprocess
from dataclasses import dataclass
from typing import List

@dataclass
class InferenceTask:
    id: int
    prompt: str
    max_tokens: int = 50
    threads: int = 4

class ThreadPoolManager:
    def __init__(self, num_workers=3, threads_per_worker=4):
        self.num_workers = num_workers
        self.threads_per_worker = threads_per_worker
        self.task_queue = queue.Queue()
        self.results = {}
        self.workers = []
        
    def worker(self, worker_id):
        """Worker thread function"""
        while True:
            task = self.task_queue.get()
            if task is None:
                break
                
            print(f"Worker {worker_id} processing task {task.id}")
            
            env = os.environ.copy()
            env['OMP_NUM_THREADS'] = str(self.threads_per_worker)
            
            cmd = [
                "python3", "run_inference.py",
                "-p", task.prompt,
                "-n", str(task.max_tokens),
                "-t", str(self.threads_per_worker)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            self.results[task.id] = result.stdout
            
            self.task_queue.task_done()
    
    def start(self):
        """Start worker threads"""
        for i in range(self.num_workers):
            t = threading.Thread(target=self.worker, args=(i,))
            t.start()
            self.workers.append(t)
    
    def add_task(self, task: InferenceTask):
        """Add task to queue"""
        self.task_queue.put(task)
    
    def wait_completion(self):
        """Wait for all tasks to complete"""
        self.task_queue.join()
    
    def stop(self):
        """Stop all workers"""
        for _ in range(self.num_workers):
            self.task_queue.put(None)
        for t in self.workers:
            t.join()

# Example usage
if __name__ == "__main__":
    manager = ThreadPoolManager(num_workers=3, threads_per_worker=4)
    manager.start()
    
    # Add tasks
    tasks = [
        InferenceTask(1, "What is deep learning?", 50),
        InferenceTask(2, "Explain neural networks", 50),
        InferenceTask(3, "What is backpropagation?", 50),
        InferenceTask(4, "Describe gradient descent", 50),
        InferenceTask(5, "What are transformers?", 50),
        InferenceTask(6, "Explain attention mechanism", 50),
    ]
    
    for task in tasks:
        manager.add_task(task)
    
    manager.wait_completion()
    manager.stop()
    
    print("\nAll tasks completed!")
    for task_id, result in manager.results.items():
        print(f"Task {task_id}: {result[:50]}...")
```

## 8. Performance Tuning Tips

### 1. Thread Configuration by Workload

| Workload Type | Configuration | Threads/Process | Processes |
|--------------|---------------|-----------------|-----------|
| Single Large Prompt | Max Throughput | 12 | 1 |
| Multiple Medium Prompts | Balanced | 4 | 3 |
| Many Small Prompts | High Concurrency | 2 | 6 |
| Real-time Server | Low Latency | 3 | 4 |

### 2. Environment Variables for Fine-Tuning

```bash
# Thread binding
export OMP_PROC_BIND=true
export OMP_PLACES=cores

# Thread scheduling
export OMP_SCHEDULE="dynamic,1"
export OMP_WAIT_POLICY=active

# Memory allocation
export OMP_ALLOCATOR=omp_high_bw_mem_alloc
```

### 3. Benchmark Different Configurations

```bash
# Test script for finding optimal configuration
cat > test_threading_configs.sh << 'EOF'
#!/bin/bash

echo "Testing different thread configurations..."

for threads in 1 2 4 6 8 10 12; do
    echo -n "Threads: $threads - "
    start=$(date +%s.%N)
    
    OMP_NUM_THREADS=$threads python3 run_inference.py \
        -p "Benchmark prompt for testing thread performance" \
        -n 100 -t $threads > /dev/null 2>&1
    
    end=$(date +%s.%N)
    duration=$(echo "$end - $start" | bc)
    echo "Time: ${duration}s"
done
EOF

chmod +x test_threading_configs.sh
./test_threading_configs.sh
```

## Summary

To fully utilize your 12 cores:

1. **Single Task**: Use all 12 threads for maximum speed
2. **Parallel Tasks**: Divide threads among processes (e.g., 3×4 or 6×2)
3. **Server Mode**: Use thread pools for handling concurrent requests
4. **Monitor Performance**: Use htop/pidstat to verify thread utilization
5. **Tune Configuration**: Adjust based on your specific workload

The key is matching the threading strategy to your use case - whether you need maximum throughput for single queries or better concurrency for multiple requests.