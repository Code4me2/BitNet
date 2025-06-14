# test_performance.py
import subprocess
import re
import sys
import os

def test_performance():
    """Verify performance meets expectations"""
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = '12'
    
    result = subprocess.run([
        "python3", "run_inference.py",
        "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
        "-p", "Count from 1 to 10",
        "-n", "50"
    ], capture_output=True, text=True, env=env)
    
    # Extract tokens/sec from output
    output = result.stdout + result.stderr
    match = re.search(r'(\d+\.?\d*)\s*tokens per second', output)
    if match:
        tokens_per_sec = float(match.group(1))
        print(f"✅ Performance: {tokens_per_sec:.1f} tokens/sec")
        
        # Expected: 15-50 tokens/sec on 12-core Intel
        if tokens_per_sec >= 10:
            print("✅ Performance validation: PASSED")
            return True
        else:
            print(f"⚠️  Performance below expected (got {tokens_per_sec:.1f}, expected >10)")
    else:
        print("❌ Could not measure performance")
    
    return False

if __name__ == "__main__":
    sys.exit(0 if test_performance() else 1)