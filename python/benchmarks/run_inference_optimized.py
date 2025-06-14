#!/usr/bin/env python3
"""
Optimized BitNet inference wrapper with automatic performance tuning for WSL
"""
import os
import sys
import signal
import platform
import argparse
import subprocess
import multiprocessing

def get_optimal_thread_count():
    """Determine optimal thread count based on CPU info"""
    # Get physical CPU count
    physical_cores = multiprocessing.cpu_count() // 2  # Assume hyperthreading
    
    # For Intel CPUs with P-cores and E-cores, use total thread count
    # Intel Core Ultra 7 155U has 12 threads total
    return min(multiprocessing.cpu_count(), 12)

def set_performance_env():
    """Set optimal environment variables for performance"""
    optimal_threads = get_optimal_thread_count()
    
    # Set thread-related environment variables
    env_vars = {
        'OMP_NUM_THREADS': str(optimal_threads),
        'MKL_NUM_THREADS': str(optimal_threads),
        'OPENBLAS_NUM_THREADS': str(optimal_threads),
        'VECLIB_MAXIMUM_THREADS': str(optimal_threads),
        'NUMEXPR_NUM_THREADS': str(optimal_threads),
        # Disable CPU frequency scaling warnings
        'TF_CPP_MIN_LOG_LEVEL': '2',
        # Set thread affinity
        'OMP_PROC_BIND': 'true',
        'OMP_PLACES': 'cores'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return optimal_threads

def check_cpu_governor():
    """Check and suggest CPU governor settings (Linux only)"""
    if platform.system() == 'Linux':
        try:
            # Check current governor
            result = subprocess.run(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                current_governor = result.stdout.strip()
                if current_governor != 'performance':
                    print(f"💡 Tip: CPU governor is '{current_governor}'. For best performance, run:")
                    print(f"   sudo cpupower frequency-set -g performance")
                    print()
        except:
            pass  # Ignore if cpufreq not available (common in WSL)

def run_command(command, shell=False):
    """Run a system command and ensure it succeeds."""
    try:
        subprocess.run(command, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command: {e}")
        sys.exit(1)

def run_inference():
    """Run inference with optimized settings"""
    # Set performance environment
    optimal_threads = set_performance_env()
    
    # Override thread count if user specified
    if args.threads > 0:
        optimal_threads = args.threads
        os.environ['OMP_NUM_THREADS'] = str(optimal_threads)
        os.environ['MKL_NUM_THREADS'] = str(optimal_threads)
    
    print(f"🚀 Running BitNet inference with {optimal_threads} threads")
    print(f"📊 Model: {os.path.basename(args.model)}")
    print()
    
    # Check CPU governor
    check_cpu_governor()
    
    build_dir = "build"
    if platform.system() == "Windows":
        main_path = os.path.join(build_dir, "bin", "Release", "llama-cli.exe")
        if not os.path.exists(main_path):
            main_path = os.path.join(build_dir, "bin", "llama-cli")
    else:
        main_path = os.path.join(build_dir, "bin", "llama-cli")
    
    command = [
        f'{main_path}',
        '-m', args.model,
        '-n', str(args.n_predict),
        '-t', str(optimal_threads),
        '-p', args.prompt,
        '-ngl', '0',
        '-c', str(args.ctx_size),
        '--temp', str(args.temperature),
        "-b", "1",
    ]
    
    # Add additional optimization flags
    if args.performance_mode:
        command.extend([
            '--no-mmap',  # Disable memory mapping for better performance
            '--keep', '-1',  # Keep entire model in memory
        ])
    
    if args.conversation:
        command.append("-cnv")
    
    if args.top_k:
        command.extend(['--top-k', str(args.top_k)])
    
    if args.top_p:
        command.extend(['--top-p', str(args.top_p)])
    
    if args.repeat_penalty:
        command.extend(['--repeat-penalty', str(args.repeat_penalty)])
    
    run_command(command)

def signal_handler(sig, frame):
    print("\nCtrl+C pressed, exiting...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Optimized BitNet inference runner')
    parser.add_argument("-m", "--model", type=str, 
                       help="Path to model file", 
                       required=False, 
                       default="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf")
    parser.add_argument("-n", "--n-predict", type=int, 
                       help="Number of tokens to predict", 
                       required=False, default=128)
    parser.add_argument("-p", "--prompt", type=str, 
                       help="Prompt to generate text from", 
                       required=True)
    parser.add_argument("-t", "--threads", type=int, 
                       help="Number of threads (0 = auto-detect)", 
                       required=False, default=0)
    parser.add_argument("-c", "--ctx-size", type=int, 
                       help="Size of the prompt context", 
                       required=False, default=2048)
    parser.add_argument("-temp", "--temperature", type=float, 
                       help="Temperature for text generation", 
                       required=False, default=0.8)
    parser.add_argument("-cnv", "--conversation", action='store_true', 
                       help="Enable conversation mode")
    parser.add_argument("--performance-mode", action='store_true',
                       help="Enable additional performance optimizations")
    parser.add_argument("--top-k", type=int, 
                       help="Top-k sampling parameter")
    parser.add_argument("--top-p", type=float, 
                       help="Top-p sampling parameter")
    parser.add_argument("--repeat-penalty", type=float, 
                       help="Repetition penalty")
    
    args = parser.parse_args()
    run_inference()