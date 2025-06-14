#!/usr/bin/env python3
"""
Thread monitoring utility for BitNet inference
Shows real-time CPU and thread utilization
"""
import psutil
import subprocess
import threading
import time
import os
from datetime import datetime
import signal
import sys

class ThreadMonitor:
    def __init__(self):
        self.monitoring = False
        self.stats = []
        self.inference_process = None
        
    def get_cpu_stats(self):
        """Get current CPU utilization per core"""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_freq = psutil.cpu_freq(percpu=True)
        
        return {
            "timestamp": datetime.now(),
            "cpu_percent": cpu_percent,
            "cpu_freq": cpu_freq if cpu_freq else [],
            "total_percent": psutil.cpu_percent(interval=0.1),
            "thread_count": threading.active_count()
        }
    
    def monitor_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring:
            stats = self.get_cpu_stats()
            self.stats.append(stats)
            
            # Display real-time stats
            os.system('clear' if os.name == 'posix' else 'cls')
            self.display_stats(stats)
            
            time.sleep(1)
    
    def display_stats(self, stats):
        """Display current stats in a nice format"""
        print("🔍 BitNet Thread Monitor")
        print("=" * 60)
        print(f"Time: {stats['timestamp'].strftime('%H:%M:%S')}")
        print(f"Overall CPU: {stats['total_percent']:.1f}%")
        print(f"Active Python threads: {stats['thread_count']}")
        print("\nPer-Core Usage:")
        print("-" * 60)
        
        # Display as a bar chart
        for i, percent in enumerate(stats['cpu_percent']):
            bar_length = int(percent / 2)  # Scale to 50 chars
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"Core {i:2d}: [{bar}] {percent:5.1f}%")
        
        print("-" * 60)
        print("Press Ctrl+C to stop monitoring")
    
    def run_inference_with_monitoring(self, prompt, max_tokens=100, threads=12):
        """Run inference while monitoring thread usage"""
        print(f"Starting inference with {threads} threads...")
        print("Monitoring will begin in 2 seconds...")
        time.sleep(2)
        
        # Start monitoring in background
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.start()
        
        # Run inference
        env = os.environ.copy()
        env['OMP_NUM_THREADS'] = str(threads)
        
        cmd = [
            "python3", "run_inference.py",
            "-p", prompt,
            "-n", str(max_tokens),
            "-t", str(threads)
        ]
        
        try:
            self.inference_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Wait for completion
            stdout, stderr = self.inference_process.communicate()
            
        finally:
            # Stop monitoring
            self.monitoring = False
            monitor_thread.join()
            
        return stdout.decode('utf-8')
    
    def analyze_stats(self):
        """Analyze collected statistics"""
        if not self.stats:
            print("No statistics collected")
            return
        
        print("\n📊 Thread Utilization Analysis")
        print("=" * 60)
        
        # Calculate averages per core
        num_cores = len(self.stats[0]['cpu_percent'])
        core_averages = [0] * num_cores
        
        for stat in self.stats:
            for i, percent in enumerate(stat['cpu_percent']):
                core_averages[i] += percent
        
        for i in range(num_cores):
            core_averages[i] /= len(self.stats)
        
        # Find statistics
        max_total = max(stat['total_percent'] for stat in self.stats)
        avg_total = sum(stat['total_percent'] for stat in self.stats) / len(self.stats)
        
        print(f"Duration: {len(self.stats)} seconds")
        print(f"Peak CPU usage: {max_total:.1f}%")
        print(f"Average CPU usage: {avg_total:.1f}%")
        print(f"\nAverage usage per core:")
        
        for i, avg in enumerate(core_averages):
            print(f"  Core {i}: {avg:.1f}%")
        
        # Identify thread distribution
        high_usage_cores = [i for i, avg in enumerate(core_averages) if avg > 50]
        print(f"\nHigh usage cores (>50%): {high_usage_cores}")
        print(f"Thread efficiency: {len(high_usage_cores)}/{num_cores} cores heavily utilized")

def benchmark_thread_configs():
    """Benchmark different thread configurations"""
    monitor = ThreadMonitor()
    configs = [2, 4, 6, 8, 10, 12]
    
    print("🧪 Benchmarking Thread Configurations")
    print("=" * 60)
    
    prompt = "Explain the concept of parallel computing and how multiple CPU cores work together"
    
    for num_threads in configs:
        print(f"\n📌 Testing with {num_threads} threads...")
        
        start_time = time.time()
        output = monitor.run_inference_with_monitoring(
            prompt=prompt,
            max_tokens=100,
            threads=num_threads
        )
        duration = time.time() - start_time
        
        monitor.analyze_stats()
        print(f"Inference time: {duration:.2f}s")
        
        # Reset stats for next run
        monitor.stats = []
        
        # Brief pause between tests
        time.sleep(3)

def live_monitoring_demo():
    """Live monitoring demonstration"""
    monitor = ThreadMonitor()
    
    print("🎯 Live Thread Monitoring Demo")
    print("=" * 60)
    print("This will run inference while showing real-time CPU usage")
    print()
    
    prompt = input("Enter prompt (or press Enter for default): ").strip()
    if not prompt:
        prompt = "Write a detailed explanation of how modern CPUs handle parallel processing"
    
    threads = input("Number of threads to use [1-12] (default 12): ").strip()
    threads = int(threads) if threads.isdigit() else 12
    threads = max(1, min(12, threads))
    
    print(f"\nRunning inference with {threads} threads...")
    print("Watch the CPU usage per core!")
    
    output = monitor.run_inference_with_monitoring(
        prompt=prompt,
        max_tokens=200,
        threads=threads
    )
    
    print("\n" + "=" * 60)
    print("Inference completed!")
    monitor.analyze_stats()
    
    print("\nGenerated text:")
    print("-" * 60)
    print(output[:500] + "..." if len(output) > 500 else output)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nMonitoring stopped.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        print("Error: psutil not installed")
        print("Install with: pip install psutil")
        sys.exit(1)
    
    print("🖥️  BitNet Thread Monitor")
    print(f"System: {psutil.cpu_count(logical=False)} cores, "
          f"{psutil.cpu_count(logical=True)} threads")
    print()
    
    print("Select mode:")
    print("1. Live monitoring demo")
    print("2. Benchmark thread configurations")
    print("3. Quick monitoring test")
    
    choice = input("Choice [1-3]: ").strip()
    
    if choice == "1":
        live_monitoring_demo()
    elif choice == "2":
        benchmark_thread_configs()
    else:
        # Quick test
        monitor = ThreadMonitor()
        print("\n🚀 Quick Monitoring Test")
        output = monitor.run_inference_with_monitoring(
            "What are the advantages of multi-threading?",
            max_tokens=50,
            threads=12
        )
        monitor.analyze_stats()