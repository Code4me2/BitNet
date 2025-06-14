#!/usr/bin/env python3
"""
Simple demonstration of thread utilization impact on BitNet performance
"""
import subprocess
import time
import os

def run_with_threads(prompt, num_threads):
    """Run inference with specified number of threads"""
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(num_threads)
    
    start_time = time.time()
    
    cmd = [
        "python3", "run_inference.py",
        "-p", prompt,
        "-n", "50",
        "-t", str(num_threads),
        "-temp", "0"  # Deterministic output
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    duration = time.time() - start_time
    
    # Extract tokens/sec from output
    import re
    tokens_per_sec = 0
    match = re.search(r'(\d+\.?\d*)\s*tokens per second', result.stderr)
    if match:
        tokens_per_sec = float(match.group(1))
    
    return duration, tokens_per_sec

def main():
    print("🧵 BitNet Thread Utilization Demo")
    print("=" * 50)
    print("This demo shows how thread count affects performance")
    print()
    
    prompt = "Explain how CPU cores work together in parallel computing"
    
    # Test different thread counts
    thread_counts = [1, 2, 4, 6, 8, 10, 12]
    results = []
    
    print(f"Testing with prompt: '{prompt[:50]}...'")
    print("-" * 50)
    print(f"{'Threads':>8} | {'Time (s)':>10} | {'Tokens/sec':>12} | {'Speedup':>8}")
    print("-" * 50)
    
    baseline_time = None
    
    for threads in thread_counts:
        print(f"{threads:>8} | ", end="", flush=True)
        
        duration, tps = run_with_threads(prompt, threads)
        
        if baseline_time is None:
            baseline_time = duration
            speedup = 1.0
        else:
            speedup = baseline_time / duration
        
        results.append({
            'threads': threads,
            'time': duration,
            'tokens_per_sec': tps,
            'speedup': speedup
        })
        
        print(f"{duration:>10.2f} | {tps:>12.1f} | {speedup:>7.2f}x")
    
    # Show visual graph
    print("\n📊 Performance Scaling Graph")
    print("-" * 50)
    
    max_tps = max(r['tokens_per_sec'] for r in results)
    
    for r in results:
        bar_length = int((r['tokens_per_sec'] / max_tps) * 40)
        bar = "█" * bar_length
        print(f"{r['threads']:>2} threads: {bar} {r['tokens_per_sec']:.1f} tok/s")
    
    # Find optimal thread count
    best = max(results, key=lambda x: x['tokens_per_sec'])
    print(f"\n✨ Optimal configuration: {best['threads']} threads")
    print(f"   Performance: {best['tokens_per_sec']:.1f} tokens/sec")
    print(f"   Speedup vs 1 thread: {best['speedup']:.2f}x")
    
    # Show efficiency
    efficiency = (best['speedup'] / best['threads']) * 100
    print(f"   Parallel efficiency: {efficiency:.1f}%")
    
    print("\n💡 Key Insights:")
    print("- Performance improves with more threads up to a point")
    print("- Diminishing returns occur due to memory bandwidth limits")
    print("- Optimal thread count depends on prompt complexity")
    print(f"- Your system shows best performance at {best['threads']} threads")

if __name__ == "__main__":
    main()