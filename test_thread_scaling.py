#!/usr/bin/env python3
import subprocess
import time
import re
import os
import statistics

def test_threads(thread_count, prompt="Explain quantum computing", num_tokens=50):
    """Test performance with specific thread count"""
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(thread_count)
    
    cmd = [
        'build/bin/llama-cli',
        '-m', 'models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf',
        '-p', prompt,
        '-n', str(num_tokens),
        '--temp', '0',
        '-t', str(thread_count)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    output = result.stdout + result.stderr
    
    # Extract eval performance
    eval_match = re.search(r'eval time.*?(\d+\.?\d*)\s*tokens per second', output)
    if eval_match:
        return float(eval_match.group(1))
    return 0

def main():
    print("🔧 BitNet Thread Scaling Test")
    print("=" * 50)
    
    thread_counts = [1, 2, 4, 6, 8, 10, 12]
    results = {}
    
    print("Testing different thread configurations...")
    print("-" * 50)
    
    for threads in thread_counts:
        print(f"Testing {threads:2d} threads: ", end='', flush=True)
        
        # Run 2 tests per thread count
        runs = []
        for _ in range(2):
            tps = test_threads(threads)
            if tps > 0:
                runs.append(tps)
        
        if runs:
            avg = statistics.mean(runs)
            results[threads] = avg
            print(f"{avg:6.2f} tok/s")
        else:
            print("Failed")
    
    # Find optimal
    if results:
        best_threads = max(results.keys(), key=lambda x: results[x])
        print("\n" + "=" * 50)
        print("📊 Results:")
        print("-" * 50)
        for t in sorted(results.keys()):
            bar = "█" * int(results[t] / 2)
            print(f"{t:2d} threads: {results[t]:6.2f} tok/s {bar}")
        
        print(f"\n✅ Best performance: {best_threads} threads @ {results[best_threads]:.2f} tok/s")

if __name__ == "__main__":
    main()