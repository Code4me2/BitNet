# test_output_quality.py
import subprocess
import sys
import os

def test_output_quality():
    """Test if model produces coherent output"""
    env = os.environ.copy()
    env['OMP_NUM_THREADS'] = '12'
    
    prompts_and_checks = [
        ("What is 2+2?", ["4", "four"]),
        ("The capital of France is", ["Paris"]),
        ("Python is a", ["programming", "language"])
    ]
    
    all_passed = True
    
    for prompt, expected_words in prompts_and_checks:
        result = subprocess.run([
            "python3", "run_inference.py",
            "-m", "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
            "-p", prompt,
            "-n", "20",
            "-temp", "0"
        ], capture_output=True, text=True, env=env)
        
        output = result.stdout.lower()
        found = any(word.lower() in output for word in expected_words)
        
        if found:
            print(f"✅ Quality test '{prompt}': PASSED")
        else:
            print(f"❌ Quality test '{prompt}': FAILED")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if test_output_quality() else 1)