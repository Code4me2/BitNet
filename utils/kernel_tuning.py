#!/usr/bin/env python3
"""
BitNet Kernel Tuning Script
Automatically finds optimal kernel parameters for your hardware

This tool tests different kernel configurations to find the best
performance for your specific CPU architecture.
"""

import os
import sys
import time
import json
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Dict

class KernelTuner:
    def __init__(self, model_path: str, verbose: bool = False):
        self.model_path = model_path
        self.verbose = verbose
        self.base_dir = Path(__file__).parent.parent
        self.build_dir = self.base_dir / "build"
        self.original_kernel_config = None
        self.results = []
        
        # Detect architecture
        self.arch = subprocess.check_output(['uname', '-m']).decode().strip()
        self.is_arm = 'arm' in self.arch or 'aarch64' in self.arch
        
        # Model configurations
        self.model_configs = {
            "bitnet_b1_58-3B": {
                "kernels": [[3200, 8640], [3200, 3200], [8640, 3200]],
                "default_arm": {"BM": [160, 320, 320], "BK": [64, 128, 64], "bm": [32, 64, 32]},
                "default_x86": {"BM": [160, 320, 320], "BK": [96, 96, 96], "bm": [32, 32, 32]}
            }
        }
        
    def backup_current_config(self):
        """Backup current kernel configuration"""
        config_path = self.base_dir / "include" / "kernel_config.ini"
        if config_path.exists():
            self.original_kernel_config = config_path.read_text()
            
    def restore_original_config(self):
        """Restore original kernel configuration"""
        if self.original_kernel_config:
            config_path = self.base_dir / "include" / "kernel_config.ini"
            config_path.write_text(self.original_kernel_config)
            
    def generate_test_configs(self) -> List[Dict]:
        """Generate test configurations based on hardware"""
        configs = []
        
        if self.is_arm:
            # ARM configurations
            bm_values = [32, 64]
            BM_values = [128, 160, 256, 320]
            BK_values = [64, 96, 128]
        else:
            # x86 configurations - optimized for AVX2
            bm_values = [32]
            BM_values = [128, 160, 256, 320]
            BK_values = [64, 96, 128, 192]
            
        # Generate combinations
        for BM in BM_values:
            for BK in BK_values:
                for bm in bm_values:
                    # Check constraints
                    if BM % bm == 0:
                        if self.is_arm and BK % 32 == 0:
                            configs.append({
                                "BM": [BM] * 3,
                                "BK": [BK] * 3,
                                "bm": [bm] * 3
                            })
                        elif not self.is_arm and BK % 32 == 0:
                            configs.append({
                                "BM": [BM] * 3,
                                "BK": [BK] * 3,
                                "bm": [bm] * 3
                            })
                            
        return configs[:10]  # Limit to top 10 configs for quick tuning
        
    def run_codegen(self, config: Dict) -> bool:
        """Run codegen with specific configuration"""
        try:
            if self.is_arm:
                script = "utils/codegen_tl1.py"
            else:
                script = "utils/codegen_tl2.py"
                
            cmd = [
                sys.executable, script,
                "--model", "bitnet_b1_58-3B",
                "--BM", ",".join(map(str, config["BM"])),
                "--BK", ",".join(map(str, config["BK"])),
                "--bm", ",".join(map(str, config["bm"]))
            ]
            
            if self.verbose:
                print(f"Running: {' '.join(cmd)}")
                
            result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            if self.verbose:
                print(f"Codegen failed: {e}")
            return False
            
    def rebuild_bitnet(self) -> bool:
        """Rebuild BitNet with new kernels"""
        try:
            cmd = ["bash", "rebuild_bitnet.sh"]
            result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            if self.verbose:
                print(f"Build failed: {e}")
            return False
            
    def benchmark_config(self, config: Dict) -> Dict:
        """Benchmark a specific configuration"""
        print(f"\nTesting config: BM={config['BM'][0]}, BK={config['BK'][0]}, bm={config['bm'][0]}")
        
        # Generate new kernels
        if not self.run_codegen(config):
            return {"config": config, "status": "codegen_failed", "tokens_per_second": 0}
            
        # Rebuild
        print("  Building...")
        if not self.rebuild_bitnet():
            return {"config": config, "status": "build_failed", "tokens_per_second": 0}
            
        # Run benchmark
        print("  Benchmarking...")
        try:
            cmd = [
                str(self.build_dir / "bin" / "llama-bench"),
                "-m", self.model_path,
                "-p", "512",  # Prompt length
                "-n", "128",  # Generation length
                "-r", "3"     # Repetitions
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if self.verbose and result.stdout:
                print(f"  Benchmark output:\n{result.stdout}")
            
            # Parse output for tokens/second
            tokens_per_second = 0
            for line in result.stdout.split('\n'):
                # Look for benchmark table rows with t/s values
                if '|' in line and 'tg' in line and '±' in line:
                    try:
                        # Extract t/s value from table format
                        parts = line.split('|')
                        if len(parts) >= 7:
                            tps_part = parts[-1].strip()  # Last column contains t/s
                            tps_value = tps_part.split('±')[0].strip()
                            tokens_per_second = float(tps_value)
                            break
                    except:
                        pass
                        
            return {
                "config": config,
                "status": "success",
                "tokens_per_second": tokens_per_second
            }
            
        except subprocess.TimeoutExpired:
            return {"config": config, "status": "timeout", "tokens_per_second": 0}
        except Exception as e:
            return {"config": config, "status": f"error: {str(e)}", "tokens_per_second": 0}
            
    def run_tuning(self):
        """Run the full tuning process"""
        print("BitNet Kernel Tuning")
        print("=" * 50)
        print(f"Model: {self.model_path}")
        print(f"Architecture: {self.arch}")
        print(f"Tuning mode: {'ARM/TL1' if self.is_arm else 'x86/TL2'}")
        print()
        
        # Backup current config
        self.backup_current_config()
        
        # Generate test configurations
        configs = self.generate_test_configs()
        print(f"Testing {len(configs)} configurations...")
        
        # Test each configuration
        try:
            for i, config in enumerate(configs, 1):
                print(f"\n[{i}/{len(configs)}]", end='')
                result = self.benchmark_config(config)
                self.results.append(result)
                
                if result["status"] == "success":
                    print(f"   {result['tokens_per_second']:.2f} tokens/s")
                else:
                    print(f"   {result['status']}")
                    
        except KeyboardInterrupt:
            print("\n\nTuning interrupted by user")
            
        finally:
            # Always restore original config
            print("\nRestoring original configuration...")
            self.restore_original_config()
            self.rebuild_bitnet()
            
        # Show results
        self.show_results()
        
    def show_results(self):
        """Display tuning results"""
        print("\n" + "=" * 50)
        print("TUNING RESULTS")
        print("=" * 50)
        
        # Sort by performance
        successful = [r for r in self.results if r["status"] == "success"]
        successful.sort(key=lambda x: x["tokens_per_second"], reverse=True)
        
        if not successful:
            print("No successful configurations found!")
            return
            
        print("\nTop 5 configurations:")
        print(f"{'Rank':<6} {'BM':<10} {'BK':<10} {'bm':<10} {'Tokens/s':<12}")
        print("-" * 50)
        
        for i, result in enumerate(successful[:5], 1):
            config = result["config"]
            print(f"{i:<6} {config['BM'][0]:<10} {config['BK'][0]:<10} {config['bm'][0]:<10} {result['tokens_per_second']:<12.2f}")
            
        # Save best config
        best = successful[0]
        best_config_path = self.base_dir / "best_kernel_config.json"
        with open(best_config_path, 'w') as f:
            json.dump({
                "config": best["config"],
                "performance": best["tokens_per_second"],
                "arch": self.arch
            }, f, indent=2)
            
        print(f"\nBest configuration saved to: {best_config_path}")
        print("\nTo apply the best configuration permanently, run:")
        print(f"python3 {('utils/codegen_tl1.py' if self.is_arm else 'utils/codegen_tl2.py')} \\")
        print(f"  --model bitnet_b1_58-3B \\")
        print(f"  --BM {','.join(map(str, best['config']['BM']))} \\")
        print(f"  --BK {','.join(map(str, best['config']['BK']))} \\")
        print(f"  --bm {','.join(map(str, best['config']['bm']))}")
        print("bash rebuild_bitnet.sh")

def main():
    parser = argparse.ArgumentParser(description="BitNet Kernel Tuning")
    parser.add_argument("-m", "--model", default="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
                        help="Model path (default: models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode - test fewer configurations")
                        
    args = parser.parse_args()
    
    # Check if model exists
    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = Path(__file__).parent.parent / args.model
        
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        sys.exit(1)
        
    # Check if llama-bench exists
    bench_path = Path(__file__).parent.parent / "build" / "bin" / "llama-bench"
    if not bench_path.exists():
        print("Error: llama-bench not found. Please build BitNet first.")
        print("Run: bash rebuild_bitnet.sh")
        sys.exit(1)
        
    # Run tuning
    tuner = KernelTuner(str(model_path), verbose=args.verbose)
    
    if args.quick:
        # Override with fewer configs for quick mode
        # For 2B4T model with shapes [3200, 8640], [3200, 3200], [8640, 3200]
        # BM must divide 3200 and 8640 evenly
        tuner.generate_test_configs = lambda: [
            {"BM": [160, 160, 160], "BK": [96, 96, 96], "bm": [32, 32, 32]},   # Current default
            {"BM": [160, 160, 160], "BK": [128, 128, 128], "bm": [32, 32, 32]}, # Higher BK
            {"BM": [320, 320, 320], "BK": [96, 96, 96], "bm": [32, 32, 32]},   # Higher BM
            {"BM": [160, 320, 320], "BK": [64, 128, 64], "bm": [32, 32, 32]}   # Mixed config
        ]
        
    tuner.run_tuning()

if __name__ == "__main__":
    main()