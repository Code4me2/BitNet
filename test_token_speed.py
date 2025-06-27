#!/usr/bin/env python3
import subprocess
import time
import re
import os
import statistics

def run_benchmark(prompt, num_tokens=100, num_runs=3):
    """Run benchmark and extract tokens/sec from output"""
    print(f"\nPrompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
    print(f"Generating {num_tokens} tokens, {num_runs} runs")
    print("-" * 60)
    
    results = []
    
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}: ", end='', flush=True)
        
        # Set environment variables
        env = os.environ.copy()
        env['OMP_NUM_THREADS'] = '12'
        
        # Run llama-cli directly
        cmd = [
            'build/bin/llama-cli',
            '-m', 'models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf',
            '-p', prompt,
            '-n', str(num_tokens),
            '--temp', '0',
            '-t', '12'
        ]
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        end = time.time()
        
        # Extract performance metrics
        output = result.stdout + result.stderr
        
        # Look for eval time (generation performance)
        eval_match = re.search(r'eval time.*?(\d+\.?\d*)\s*tokens per second', output)
        if eval_match:
            tokens_per_sec = float(eval_match.group(1))
            results.append(tokens_per_sec)
            print(f"{tokens_per_sec:.2f} tok/s")
        else:
            print("No performance data found")
    
    if results:
        avg = statistics.mean(results)
        std = statistics.stdev(results) if len(results) > 1 else 0
        print(f"\nAverage: {avg:.2f} ± {std:.2f} tokens/sec")
        return avg, std
    else:
        print("\nNo performance data collected")
        return 0, 0

def main():
    print("🤖 BitNet B1.58 2B-4T Token Generation Speed Test")
    print("=" * 60)
    print(f"Model: BitNet-b1.58-2B-4T")
    print(f"Threads: 12")
    print("=" * 60)
    
    # Test different prompt types
    test_cases = [
        ("Simple", "What is 2+2?", 50),
        ("Technical", "Explain how a computer works", 100),
        ("Code", "Write a Python function to calculate factorial", 100),
        ("Story", "Once upon a time in a distant galaxy", 150),
    ]
    
    all_results = []
    
    for test_name, prompt, tokens in test_cases:
        print(f"\n📊 Test: {test_name}")
        avg, std = run_benchmark(prompt, tokens, num_runs=3)
        if avg > 0:
            all_results.append((test_name, avg, std))
    
    # Summary
    if all_results:
        print("\n" + "=" * 60)
        print("📈 SUMMARY")
        print("=" * 60)
        print("\nToken generation speed by task:")
        for name, avg, std in all_results:
            print(f"  {name:12s}: {avg:6.2f} ± {std:4.2f} tok/s")
        
        overall_avg = statistics.mean([r[1] for r in all_results])
        print(f"\nOverall average: {overall_avg:.2f} tokens/sec")
    
    print("\n✅ Benchmark completed!")

if __name__ == "__main__":
    main()