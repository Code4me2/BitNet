#!/bin/bash
#
# BitNet Cleanup Analysis - Shows what would be cleaned without removing anything
#

echo "🔍 BitNet Directory Cleanup Analysis"
echo "===================================="
echo

# Function to get size with fallback
get_size() {
    if [ -e "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1 || echo "?"
    else
        echo "0"
    fi
}

# Current total size
TOTAL_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "Current directory size: $TOTAL_SIZE"
echo

# Cleanup candidates
echo "📊 Cleanup Candidates:"
echo "---------------------"

# 1. Large files/directories
echo "1. Large items:"
[ -f "cmake.tar.gz" ] && echo "   - cmake.tar.gz: $(get_size cmake.tar.gz)"
[ -d "build/" ] && echo "   - build/: $(get_size build/)"
[ -d "cmake-local/" ] && echo "   - cmake-local/: $(get_size cmake-local/) (KEEP - no system cmake)"
[ -d ".git/" ] && echo "   - .git/: $(get_size .git/) (optional - git history)"

echo
echo "2. Build artifacts:"
OBJ_COUNT=$(find . -name "*.o" 2>/dev/null | wc -l)
OBJ_SIZE=$(find . -name "*.o" 2>/dev/null -exec du -ch {} + | tail -1 | cut -f1)
[ $OBJ_COUNT -gt 0 ] && echo "   - Object files (.o): $OBJ_COUNT files, ${OBJ_SIZE:-0}"

LIB_COUNT=$(find . -name "*.a" 2>/dev/null | wc -l)
LIB_SIZE=$(find . -name "*.a" 2>/dev/null -exec du -ch {} + | tail -1 | cut -f1)
[ $LIB_COUNT -gt 0 ] && echo "   - Static libraries (.a): $LIB_COUNT files, ${LIB_SIZE:-0}"

echo
echo "3. Python cache:"
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
[ $PYCACHE_COUNT -gt 0 ] && echo "   - __pycache__ directories: $PYCACHE_COUNT"

PYC_COUNT=$(find . -name "*.pyc" 2>/dev/null | wc -l)
PYC_SIZE=$(find . -name "*.pyc" 2>/dev/null -exec du -ch {} + | tail -1 | cut -f1)
[ $PYC_COUNT -gt 0 ] && echo "   - Python bytecode (.pyc): $PYC_COUNT files, ${PYC_SIZE:-0}"

echo
echo "4. Log files:"
if [ -d "logs/" ]; then
    for log in logs/*.log; do
        [ -f "$log" ] && echo "   - $(basename "$log"): $(get_size "$log")"
    done
fi

echo
echo "5. Model files (KEEP):"
find models/ -name "*.gguf" -exec echo "   - {} ($(get_size {}))" \; 2>/dev/null

echo
echo "💡 To run cleanup:"
echo "   ./cleanup_bitnet.sh        # Interactive mode"
echo "   ./cleanup_bitnet.sh -y     # Auto-yes mode"
echo