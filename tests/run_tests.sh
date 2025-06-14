#!/bin/bash
echo "Running BitNet B1.58 2T4B Verification Tests..."
echo "==========================================="

python3 test_model_loading.py
python3 test_performance.py
python3 test_output_quality.py

echo "==========================================="
echo "All tests completed!"