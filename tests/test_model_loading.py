# test_model_loading.py
import subprocess
import sys
import os

def test_model_loading():
    """Test if model loads correctly"""
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = '12'
    
    result = subprocess.run([
        "python3", "run_inference.py",
        "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
        "-p", "Test",
        "-n", "1"
    ], capture_output=True, text=True, env=env)
    
    if result.returncode == 0:
        print("✅ Model loading: PASSED")
        return True
    else:
        print("❌ Model loading: FAILED")
        print(f"Error: {result.stderr}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_model_loading() else 1)