#!/usr/bin/env python3
"""
Parallel inference example for BitNet using multi-core threading
Demonstrates how to process multiple prompts efficiently
"""
import concurrent.futures
import subprocess
import time
import os
import json
from typing import List, Dict
import multiprocessing

def run_single_inference(args) -> Dict:
    """Run inference on a single prompt"""
    prompt, max_tokens, threads_per_process = args
    start_time = time.time()
    
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = str(threads_per_process)
    env['OMP_PROC_BIND'] = 'true'
    env['OMP_PLACES'] = 'cores'
    
    cmd = [
        "python3", "run_inference.py",
        "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
        "-p", prompt,
        "-n", str(max_tokens),
        "-t", str(threads_per_process),
        "-temp", "0.7"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
        # Extract just the generated text (after the prompt)
        output = result.stdout
        if prompt in output:
            output = output.split(prompt, 1)[1].strip()
        
        return {
            "prompt": prompt,
            "output": output[:200],  # Truncate for display
            "time": time.time() - start_time,
            "success": result.returncode == 0,
            "threads": threads_per_process
        }
    except subprocess.TimeoutExpired:
        return {
            "prompt": prompt,
            "output": "Timeout",
            "time": 60.0,
            "success": False,
            "threads": threads_per_process
        }

def parallel_inference(prompts: List[str], max_tokens: int = 50, strategy: str = "balanced"):
    """
    Process multiple prompts in parallel using different strategies
    
    Strategies:
    - "balanced": 3 workers × 4 threads (good for medium prompts)
    - "concurrent": 6 workers × 2 threads (good for many small prompts)
    - "power": 2 workers × 6 threads (good for complex prompts)
    """
    
    strategies = {
        "balanced": (3, 4),    # 3 processes, 4 threads each
        "concurrent": (6, 2),  # 6 processes, 2 threads each
        "power": (2, 6),       # 2 processes, 6 threads each
    }
    
    max_workers, threads_per_worker = strategies.get(strategy, (3, 4))
    total_threads = max_workers * threads_per_worker
    
    print(f"🚀 Parallel Inference Configuration")
    print(f"   Strategy: {strategy}")
    print(f"   Workers: {max_workers}")
    print(f"   Threads per worker: {threads_per_worker}")
    print(f"   Total threads used: {total_threads}/10")  # Using 10 threads for optimal performance
    print(f"   Processing {len(prompts)} prompts...")
    print("-" * 50)
    
    # Prepare arguments for parallel execution
    args_list = [(prompt, max_tokens, threads_per_worker) for prompt in prompts]
    
    results = []
    start_time = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_prompt = {executor.submit(run_single_inference, args): args[0] 
                           for args in args_list}
        
        # Process completed tasks
        for i, future in enumerate(concurrent.futures.as_completed(future_to_prompt)):
            result = future.result()
            results.append(result)
            
            status = "✓" if result['success'] else "✗"
            print(f"{status} [{i+1}/{len(prompts)}] {result['prompt'][:40]}... "
                  f"({result['time']:.2f}s)")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = sum(1 for r in results if r['success'])
    avg_time = sum(r['time'] for r in results) / len(results)
    
    print("-" * 50)
    print(f"✅ Completed {successful}/{len(prompts)} prompts")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"⚡ Average time per prompt: {avg_time:.2f}s")
    print(f"🔄 Parallel speedup: {avg_time * len(prompts) / total_time:.2f}x")
    
    return results

def benchmark_strategies():
    """Benchmark different threading strategies"""
    test_prompts = [
        "What is the theory of relativity?",
        "Explain quantum mechanics in simple terms",
        "How does machine learning work?",
        "What are the benefits of renewable energy?",
        "Describe the process of photosynthesis",
        "What is blockchain technology?"
    ]
    
    print("🔬 Benchmarking Threading Strategies")
    print("=" * 50)
    
    results = {}
    
    for strategy in ["balanced", "concurrent", "power"]:
        print(f"\n📊 Testing '{strategy}' strategy:")
        strategy_results = parallel_inference(test_prompts, max_tokens=30, strategy=strategy)
        
        # Store timing results
        results[strategy] = {
            "total_time": sum(r['time'] for r in strategy_results),
            "avg_time": sum(r['time'] for r in strategy_results) / len(strategy_results),
            "success_rate": sum(1 for r in strategy_results if r['success']) / len(strategy_results)
        }
        
        time.sleep(2)  # Brief pause between strategies
    
    # Show comparison
    print("\n" + "=" * 50)
    print("📈 Strategy Comparison:")
    print("-" * 50)
    print(f"{'Strategy':<12} {'Avg Time':>10} {'Total Time':>12} {'Success Rate':>12}")
    print("-" * 50)
    
    for strategy, metrics in results.items():
        print(f"{strategy:<12} {metrics['avg_time']:>9.2f}s "
              f"{metrics['total_time']:>11.2f}s {metrics['success_rate']:>11.0%}")
    
    # Find best strategy
    best_strategy = min(results.items(), key=lambda x: x[1]['avg_time'])[0]
    print(f"\n🏆 Best strategy for this workload: {best_strategy}")

def interactive_demo():
    """Interactive demonstration of parallel inference"""
    print("\n🎮 Interactive Parallel Inference Demo")
    print("=" * 50)
    
    # Get user inputs
    prompts = []
    print("Enter your prompts (empty line to finish):")
    while True:
        prompt = input(f"Prompt {len(prompts)+1}: ").strip()
        if not prompt:
            break
        prompts.append(prompt)
    
    if not prompts:
        print("No prompts entered. Using defaults.")
        prompts = [
            "What is artificial intelligence?",
            "How do computers work?",
            "What is the internet?"
        ]
    
    # Choose strategy
    print("\nSelect threading strategy:")
    print("1. Balanced (3×4 threads) - Default")
    print("2. Concurrent (6×2 threads) - Many small tasks")
    print("3. Power (2×6 threads) - Complex tasks")
    
    choice = input("Choice [1-3]: ").strip()
    strategy_map = {"1": "balanced", "2": "concurrent", "3": "power"}
    strategy = strategy_map.get(choice, "balanced")
    
    # Run inference
    print(f"\nRunning parallel inference with '{strategy}' strategy...")
    results = parallel_inference(prompts, max_tokens=50, strategy=strategy)
    
    # Show results
    print("\n📝 Results:")
    print("=" * 50)
    for i, result in enumerate(results):
        print(f"\nPrompt {i+1}: {result['prompt']}")
        print(f"Response: {result['output']}")
        print(f"Time: {result['time']:.2f}s (using {result['threads']} threads)")

if __name__ == "__main__":
    # Check CPU info
    cpu_count = multiprocessing.cpu_count()
    print(f"🖥️  System has {cpu_count} CPU threads available")
    
    # Menu
    print("\nSelect mode:")
    print("1. Run benchmark of threading strategies")
    print("2. Interactive parallel inference")
    print("3. Quick parallel demo")
    
    mode = input("Choice [1-3]: ").strip()
    
    if mode == "1":
        benchmark_strategies()
    elif mode == "2":
        interactive_demo()
    else:
        # Quick demo
        print("\n🚀 Quick Parallel Demo")
        demo_prompts = [
            "What is Python programming?",
            "Explain cloud computing",
            "What are neural networks?",
            "How does GPS work?",
            "What is cryptocurrency?",
            "Describe machine learning"
        ]
        parallel_inference(demo_prompts, max_tokens=40, strategy="balanced")