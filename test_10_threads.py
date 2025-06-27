#!/usr/bin/env python3
import subprocess
import time
import re
import os
import statistics

def test_performance(threads=10):
    """Test performance with specified thread count"""
    print(f"🧪 Testing BitNet with {threads} threads configuration")
    print("=" * 60)
    
    # Set environment to use 10 threads
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(threads)
    env['MKL_NUM_THREADS'] = str(threads)
    
    prompts = [
        "What is the capital of France?",
        "Explain machine learning in simple terms",
        "Write a Python function to reverse a string",
    ]
    
    all_results = []
    
    for prompt in prompts:
        print(f"\nTesting: '{prompt[:40]}...'")
        results = []
        
        for run in range(3):
            cmd = [
                'build/bin/llama-cli',
                '-m', 'models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf',
                '-p', prompt,
                '-n', '50',
                '--temp', '0',
                '-t', str(threads)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            output = result.stdout + result.stderr
            
            # Extract eval performance
            eval_match = re.search(r'eval time.*?(\d+\.?\d*)\s*tokens per second', output)
            if eval_match:
                tps = float(eval_match.group(1))
                results.append(tps)
                print(f"  Run {run+1}: {tps:.2f} tok/s")
        
        if results:
            avg = statistics.mean(results)
            all_results.append(avg)
            print(f"  Average: {avg:.2f} tok/s")
    
    if all_results:
        overall = statistics.mean(all_results)
        print(f"\n{'='*60}")
        print(f"✅ Overall average with {threads} threads: {overall:.2f} tok/s")
        return overall
    return 0

def main():
    # Test with 10 threads (new configuration)
    perf_10 = test_performance(10)
    
    print("\n" + "="*60)
    
    # Compare with 12 threads (old configuration)
    print("\n📊 Comparing with old 12-thread configuration...")
    perf_12 = test_performance(12)
    
    # Summary
    print("\n" + "="*60)
    print("🎯 CONFIGURATION COMPARISON")
    print("="*60)
    print(f"10 threads (NEW): {perf_10:.2f} tok/s")
    print(f"12 threads (OLD): {perf_12:.2f} tok/s")
    
    if perf_10 > perf_12:
        improvement = ((perf_10 - perf_12) / perf_12) * 100
        print(f"\n✅ 10-thread configuration is {improvement:.1f}% faster!")
    else:
        print(f"\n❌ 12-thread configuration performed better")
    
    # Test that the Python scripts use correct configuration
    print("\n" + "="*60)
    print("🔍 Verifying Python script configurations...")
    
    # Check benchmark.py
    result = subprocess.run(['grep', 'OMP_NUM_THREADS', 'python/benchmarks/benchmark.py'], 
                          capture_output=True, text=True)
    if '10' in result.stdout:
        print("✅ benchmark.py correctly set to 10 threads")
    else:
        print("❌ benchmark.py not using 10 threads")
    
    # Check chat.py
    result = subprocess.run(['grep', 'OMP_NUM_THREADS', 'python/chat/chat.py'], 
                          capture_output=True, text=True)
    if '10' in result.stdout:
        print("✅ chat.py correctly set to 10 threads")
    else:
        print("❌ chat.py not using 10 threads")

if __name__ == "__main__":
    main()