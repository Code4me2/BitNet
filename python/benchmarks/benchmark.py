#!/usr/bin/env python3
import subprocess
import time
import statistics
import os
import re

def run_benchmark(prompt, num_runs=5):
    times = []
    tokens_per_sec = []
    
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...", end='', flush=True)
        start = time.time()
        
        # Set environment variables
        env = os.environ.copy()
        # Using 10 threads for optimal performance
        env['OMP_NUM_THREADS'] = '10'
        
        result = subprocess.run([
            "python3", "run_inference.py",
            "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
            "-p", prompt,
            "-n", "100",
            "-temp", "0"
        ], capture_output=True, text=True, env=env)
        
        end = time.time()
        duration = end - start
        times.append(duration)
        
        # Parse output for tokens/sec
        output = result.stdout + result.stderr
        
        # Look for performance metrics in the output
        # Pattern matches lines like: "llama_perf_context_print:   eval time = 1234.56 ms / 100 tokens ( 12.34 ms per token, 81.23 tokens per second)"
        pattern = r'(\d+\.?\d*)\s*tokens per second'
        matches = re.findall(pattern, output)
        
        if matches:
            tps = float(matches[-1])  # Get the last match (eval performance)
            tokens_per_sec.append(tps)
            print(f" {tps:.1f} tokens/sec")
        else:
            print(" (no performance data)")
    
    return {
        "avg_time": statistics.mean(times) if times else 0,
        "std_time": statistics.stdev(times) if len(times) > 1 else 0,
        "avg_tokens_per_sec": statistics.mean(tokens_per_sec) if tokens_per_sec else 0,
        "std_tokens_per_sec": statistics.stdev(tokens_per_sec) if len(tokens_per_sec) > 1 else 0,
        "runs": num_runs
    }

# Run benchmarks
print("BitNet B1.58 2B4T Performance Benchmark")
print("=" * 50)
print(f"CPU: Intel 12-core")
print(f"Threads: {os.environ.get('OMP_NUM_THREADS', '10')}")
print("=" * 50)

prompts = [
    ("Simple question", "What is the capital of France?"),
    ("Technical explanation", "Explain the theory of relativity in simple terms"),
    ("Code generation", "Write a Python function to sort a list of numbers"),
    ("Creative writing", "Write a short story about a robot learning to paint")
]

all_results = []

for prompt_type, prompt in prompts:
    print(f"\nBenchmarking: {prompt_type}")
    print(f"Prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    print("-" * 40)
    
    results = run_benchmark(prompt, num_runs=3)
    all_results.append((prompt_type, results))
    
    print(f"\nResults:")
    print(f"Average time: {results['avg_time']:.2f}s ± {results['std_time']:.2f}s")
    print(f"Average tokens/sec: {results['avg_tokens_per_sec']:.1f} ± {results['std_tokens_per_sec']:.1f}")

# Summary
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)

total_avg_tps = statistics.mean([r[1]['avg_tokens_per_sec'] for r in all_results if r[1]['avg_tokens_per_sec'] > 0])
print(f"\nOverall average performance: {total_avg_tps:.1f} tokens/sec")

print("\nPerformance by task:")
for prompt_type, results in all_results:
    if results['avg_tokens_per_sec'] > 0:
        print(f"  {prompt_type:20s}: {results['avg_tokens_per_sec']:6.1f} tokens/sec")

print("\n✅ Benchmark completed!")