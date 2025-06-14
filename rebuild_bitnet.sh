#!/bin/bash
#
# BitNet Quick Rebuild Script
# Uses local cmake to rebuild after cleanup
#

# Add local cmake to PATH
export PATH="$(pwd)/cmake-local/bin:$PATH"

# Verify cmake is available
if ! cmake --version > /dev/null 2>&1; then
    echo "❌ Error: cmake not found even with local path"
    exit 1
fi

echo "🔨 Rebuilding BitNet..."
echo "Using cmake: $(which cmake)"
echo

# Run setup
python3 setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

if [ $? -eq 0 ]; then
    echo
    echo "✅ Rebuild complete!"
    echo "You can now run: python3 run_inference.py -p 'Your prompt'"
else
    echo
    echo "❌ Rebuild failed. Please check the error messages above."
fi