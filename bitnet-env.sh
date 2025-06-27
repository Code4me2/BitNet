#!/bin/bash
#
# BitNet Environment Setup Script
# Source this file to set optimal environment variables for BitNet inference
#
# Usage: source bitnet-env.sh
#

# Detect CPU cores
if [ -z "$BITNET_THREADS" ]; then
    if command -v nproc &> /dev/null; then
        CPU_CORES=$(nproc)
    else
        CPU_CORES=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 12)
    fi
    # Optimal performance found at 10 threads
    BITNET_THREADS=$([ $CPU_CORES -gt 10 ] && echo 10 || echo $CPU_CORES)
fi

# Set thread-related environment variables
export OMP_NUM_THREADS=$BITNET_THREADS
export MKL_NUM_THREADS=$BITNET_THREADS
export OPENBLAS_NUM_THREADS=$BITNET_THREADS
export VECLIB_MAXIMUM_THREADS=$BITNET_THREADS
export NUMEXPR_NUM_THREADS=$BITNET_THREADS

# Set thread affinity for better performance
export OMP_PROC_BIND=true
export OMP_PLACES=cores

# Suppress TensorFlow warnings
export TF_CPP_MIN_LOG_LEVEL=2

# Print configuration
echo "🚀 BitNet environment configured:"
echo "   CPU threads: $BITNET_THREADS"
echo "   Thread affinity: enabled"
echo ""
echo "To make this permanent, add to ~/.bashrc:"
echo "   source $(pwd)/bitnet-env.sh"