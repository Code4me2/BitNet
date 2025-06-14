#!/usr/bin/env python3
"""
Quick test to compare standard vs optimized inference performance
"""
import subprocess
import time
import re
import os

def run_test(script, prompt, use_env=False):
    """Run a single test and extract performance metrics"""
    cmd = ["python3", script, "-p", prompt, "-n", "50", "-temp", "0"]
    
    env = os.environ.copy()
    if use_env:
        env['OMP_NUM_THREADS'] = '12'
        env['MKL_NUM_THREADS'] = '12'
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    duration = time.time() - start
    
    # Extract tokens/sec
    output = result.stdout + result.stderr
    pattern = r'(\d+\.?\d*)\s*tokens per second'
    matches = re.findall(pattern, output)
    
    tokens_per_sec = float(matches[-1]) if matches else 0
    
    return {
        'duration': duration,
        'tokens_per_sec': tokens_per_sec
    }

def main():
    print("🔬 BitNet Optimization Comparison Test")
    print("=" * 50)
    
    prompt = "Explain the importance of CPU optimization for AI inference"
    
    # Test 1: Standard run_inference.py without env vars
    print("\n1. Standard run_inference.py (default 2 threads):")
    result1 = run_test("run_inference.py", prompt, use_env=False)
    print(f"   Duration: {result1['duration']:.2f}s")
    print(f"   Performance: {result1['tokens_per_sec']:.1f} tokens/sec")
    
    # Test 2: Standard run_inference.py with env vars
    print("\n2. Standard run_inference.py with OMP_NUM_THREADS=12:")
    result2 = run_test("run_inference.py", prompt, use_env=True)
    print(f"   Duration: {result2['duration']:.2f}s")
    print(f"   Performance: {result2['tokens_per_sec']:.1f} tokens/sec")
    
    # Test 3: Optimized script
    print("\n3. Optimized run_inference_optimized.py:")
    result3 = run_test("run_inference_optimized.py", prompt, use_env=False)
    print(f"   Duration: {result3['duration']:.2f}s")
    print(f"   Performance: {result3['tokens_per_sec']:.1f} tokens/sec")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    
    if result1['tokens_per_sec'] > 0:
        improvement2 = (result2['tokens_per_sec'] / result1['tokens_per_sec'] - 1) * 100
        improvement3 = (result3['tokens_per_sec'] / result1['tokens_per_sec'] - 1) * 100
        
        print(f"\nPerformance improvements over baseline:")
        print(f"  With env vars: +{improvement2:.1f}%")
        print(f"  With optimized script: +{improvement3:.1f}%")
    
    print(f"\nOptimal configuration achieves: {max(result1['tokens_per_sec'], result2['tokens_per_sec'], result3['tokens_per_sec']):.1f} tokens/sec")

if __name__ == "__main__":
    main()