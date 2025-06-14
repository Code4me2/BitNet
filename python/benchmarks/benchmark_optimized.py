#!/usr/bin/env python3
"""
Optimized benchmark script that tests different thread configurations
and performance settings for BitNet on WSL
"""
import subprocess
import time
import statistics
import os
import re
import json
from datetime import datetime

def run_single_benchmark(prompt, threads, num_tokens=100, performance_mode=False):
    """Run a single benchmark with specified settings"""
    # Set environment variables
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(threads)
    env['MKL_NUM_THREADS'] = str(threads)
    env['OPENBLAS_NUM_THREADS'] = str(threads)
    env['OMP_PROC_BIND'] = 'true'
    env['OMP_PLACES'] = 'cores'
    
    cmd = [
        "python3", "run_inference_optimized.py",
        "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
        "-p", prompt,
        "-n", str(num_tokens),
        "-temp", "0",
        "-t", str(threads)
    ]
    
    if performance_mode:
        cmd.append("--performance-mode")
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    end = time.time()
    duration = end - start
    
    # Parse output for tokens/sec
    output = result.stdout + result.stderr
    pattern = r'(\d+\.?\d*)\s*tokens per second'
    matches = re.findall(pattern, output)
    
    tokens_per_sec = float(matches[-1]) if matches else 0
    
    return {
        'duration': duration,
        'tokens_per_sec': tokens_per_sec,
        'output': output
    }

def test_thread_scaling():
    """Test performance with different thread counts"""
    print("🔬 Testing thread scaling performance")
    print("=" * 60)
    
    thread_counts = [1, 2, 4, 6, 8, 10, 12]
    prompt = "Explain quantum computing in simple terms"
    results = {}
    
    for threads in thread_counts:
        print(f"\nTesting with {threads} threads...")
        runs = []
        
        for i in range(3):
            print(f"  Run {i+1}/3...", end='', flush=True)
            result = run_single_benchmark(prompt, threads, num_tokens=50)
            runs.append(result['tokens_per_sec'])
            print(f" {result['tokens_per_sec']:.1f} tokens/sec")
        
        avg_tps = statistics.mean(runs)
        std_tps = statistics.stdev(runs) if len(runs) > 1 else 0
        
        results[threads] = {
            'avg': avg_tps,
            'std': std_tps,
            'runs': runs
        }
    
    # Find optimal thread count
    best_threads = max(results.keys(), key=lambda x: results[x]['avg'])
    
    print(f"\n✅ Optimal thread count: {best_threads} threads")
    print(f"   Performance: {results[best_threads]['avg']:.1f} tokens/sec")
    
    return results, best_threads

def test_performance_modes(optimal_threads):
    """Test different performance modes"""
    print("\n🚀 Testing performance modes")
    print("=" * 60)
    
    prompts = [
        ("Simple", "What is 2+2?"),
        ("Medium", "Explain the water cycle"),
        ("Complex", "Write a Python function to implement binary search")
    ]
    
    modes = [
        ("Standard", False),
        ("Performance", True)
    ]
    
    results = {}
    
    for mode_name, perf_mode in modes:
        print(f"\n{mode_name} mode:")
        mode_results = []
        
        for prompt_type, prompt in prompts:
            print(f"  {prompt_type}: ", end='', flush=True)
            result = run_single_benchmark(prompt, optimal_threads, 
                                        num_tokens=50, 
                                        performance_mode=perf_mode)
            tps = result['tokens_per_sec']
            mode_results.append(tps)
            print(f"{tps:.1f} tokens/sec")
        
        results[mode_name] = {
            'avg': statistics.mean(mode_results),
            'results': mode_results
        }
    
    return results

def save_results(thread_results, perf_results, optimal_threads):
    """Save benchmark results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{timestamp}.json"
    
    data = {
        'timestamp': timestamp,
        'system': {
            'platform': os.uname().sysname if hasattr(os, 'uname') else 'Unknown',
            'cpu_count': os.cpu_count(),
            'optimal_threads': optimal_threads
        },
        'thread_scaling': thread_results,
        'performance_modes': perf_results
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")

def main():
    print("🤖 BitNet B1.58 2B4T Optimized Benchmark Suite")
    print("=" * 60)
    print("System Info:")
    print(f"  CPU cores: {os.cpu_count()}")
    print(f"  Platform: {os.uname().sysname if hasattr(os, 'uname') else 'Unknown'}")
    print("=" * 60)
    
    # Test thread scaling
    thread_results, optimal_threads = test_thread_scaling()
    
    # Test performance modes with optimal threads
    perf_results = test_performance_modes(optimal_threads)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    
    print("\nThread Scaling Results:")
    for threads in sorted(thread_results.keys()):
        result = thread_results[threads]
        print(f"  {threads:2d} threads: {result['avg']:6.1f} ± {result['std']:4.1f} tokens/sec")
    
    print(f"\nPerformance Mode Comparison (using {optimal_threads} threads):")
    for mode, result in perf_results.items():
        print(f"  {mode:12s}: {result['avg']:6.1f} tokens/sec")
    
    # Save results
    save_results(thread_results, perf_results, optimal_threads)
    
    print("\n✅ Benchmark completed!")

if __name__ == "__main__":
    main()