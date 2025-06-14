#!/bin/bash
#
# BitNet Directory Cleanup Script
# Safely removes build artifacts and unnecessary files
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to calculate directory/file size
get_size() {
    if [ -e "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        echo "0"
    fi
}

# Function to remove files/directories with confirmation
remove_with_confirm() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        local size=$(get_size "$path")
        echo -e "${YELLOW}  - $description (${size})${NC}"
        if [ "$AUTO_YES" != "true" ]; then
            read -p "    Remove? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$path"
                echo -e "${GREEN}    ✓ Removed${NC}"
                return 0
            else
                echo -e "${BLUE}    ⊗ Skipped${NC}"
                return 1
            fi
        else
            rm -rf "$path"
            echo -e "${GREEN}    ✓ Removed${NC}"
            return 0
        fi
    else
        return 1
    fi
}

# Parse command line arguments
AUTO_YES=false
if [ "$1" == "-y" ] || [ "$1" == "--yes" ]; then
    AUTO_YES=true
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧹 BitNet Directory Cleanup Tool${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if we're in the right directory
if [ ! -f "run_inference.py" ]; then
    echo -e "${RED}❌ Error: This script must be run from the BitNet directory${NC}"
    echo "   Please cd to the BitNet directory and try again."
    exit 1
fi

# Calculate total space before cleanup
echo -e "${BLUE}Calculating current disk usage...${NC}"
BEFORE_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo -e "Current directory size: ${YELLOW}${BEFORE_SIZE}${NC}"
echo

# Start cleanup
echo -e "${BLUE}Files and directories to clean:${NC}"
echo

# Initialize counters
REMOVED_COUNT=0
SKIPPED_COUNT=0

# 1. Archive files
echo -e "${YELLOW}1. Archive files:${NC}"
if remove_with_confirm "cmake.tar.gz" "CMake archive (already extracted)"; then
    ((REMOVED_COUNT++))
else
    ((SKIPPED_COUNT++))
fi
echo

# 2. Build artifacts
echo -e "${YELLOW}2. Build artifacts:${NC}"
if remove_with_confirm "build/" "Build directory with all artifacts"; then
    ((REMOVED_COUNT++))
else
    ((SKIPPED_COUNT++))
fi

# Remove individual object files if build directory was skipped
if [ -d "build/" ]; then
    echo -e "${YELLOW}   Finding and removing .o files...${NC}"
    find . -name "*.o" -type f -exec rm -f {} \; 2>/dev/null
    echo -e "${GREEN}   ✓ Removed all .o files${NC}"
fi

# Remove static libraries
if [ -d "3rdparty/" ]; then
    find 3rdparty/ -name "*.a" -type f -exec rm -f {} \; 2>/dev/null
fi
echo

# 3. Python cache files
echo -e "${YELLOW}3. Python cache files:${NC}"
PYCACHE_COUNT=0
while IFS= read -r -d '' pycache; do
    if remove_with_confirm "$pycache" "Python cache directory"; then
        ((PYCACHE_COUNT++))
    fi
done < <(find . -type d -name "__pycache__" -print0)

# Remove .pyc files
PYC_COUNT=$(find . -name "*.pyc" -type f 2>/dev/null | wc -l)
if [ $PYC_COUNT -gt 0 ]; then
    echo -e "${YELLOW}  - Python bytecode files (.pyc): ${PYC_COUNT} files${NC}"
    if [ "$AUTO_YES" == "true" ] || { read -p "    Remove all? (y/N): " -n 1 -r && echo && [[ $REPLY =~ ^[Yy]$ ]]; }; then
        find . -name "*.pyc" -type f -exec rm -f {} \;
        echo -e "${GREEN}    ✓ Removed${NC}"
        ((REMOVED_COUNT++))
    else
        echo -e "${BLUE}    ⊗ Skipped${NC}"
        ((SKIPPED_COUNT++))
    fi
fi
echo

# 4. Log files
echo -e "${YELLOW}4. Log files:${NC}"
if [ -d "logs/" ]; then
    for logfile in logs/*.log; do
        if [ -f "$logfile" ]; then
            # Keep non-empty log files by default, remove empty ones
            if [ ! -s "$logfile" ]; then
                rm -f "$logfile"
                echo -e "${GREEN}  - Removed empty log: $(basename "$logfile")${NC}"
            else
                if remove_with_confirm "$logfile" "Log file: $(basename "$logfile")"; then
                    ((REMOVED_COUNT++))
                else
                    ((SKIPPED_COUNT++))
                fi
            fi
        fi
    done
fi
echo

# 5. CMake cache files
echo -e "${YELLOW}5. CMake cache files:${NC}"
CMAKE_COUNT=0
for cmake_cache in $(find . -name "CMakeCache.txt" -o -name "cmake_install.cmake" 2>/dev/null); do
    if remove_with_confirm "$cmake_cache" "CMake cache file"; then
        ((CMAKE_COUNT++))
    fi
done
if [ $CMAKE_COUNT -eq 0 ]; then
    echo -e "${BLUE}  No CMake cache files found${NC}"
fi
echo

# 6. Temporary and backup files
echo -e "${YELLOW}6. Temporary and backup files:${NC}"
TEMP_COUNT=0
for pattern in "*~" "*.tmp" "*.bak" ".DS_Store"; do
    while IFS= read -r -d '' tmpfile; do
        if remove_with_confirm "$tmpfile" "Temporary file"; then
            ((TEMP_COUNT++))
        fi
    done < <(find . -name "$pattern" -print0 2>/dev/null)
done
if [ $TEMP_COUNT -eq 0 ]; then
    echo -e "${BLUE}  No temporary files found${NC}"
fi
echo

# 7. Optional: Git directory
if [ -d ".git" ]; then
    echo -e "${YELLOW}7. Version control (optional):${NC}"
    echo -e "${YELLOW}  - .git directory ($(get_size .git))${NC}"
    echo -e "${RED}    ⚠️  Warning: This will remove all git history!${NC}"
    if [ "$AUTO_YES" != "true" ]; then
        read -p "    Remove? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .git
            echo -e "${GREEN}    ✓ Removed${NC}"
            ((REMOVED_COUNT++))
        else
            echo -e "${BLUE}    ⊗ Skipped${NC}"
            ((SKIPPED_COUNT++))
        fi
    else
        echo -e "${BLUE}    ⊗ Skipped (requires manual confirmation)${NC}"
        ((SKIPPED_COUNT++))
    fi
    echo
fi

# Calculate space after cleanup
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
AFTER_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo
echo -e "Directory size before: ${YELLOW}${BEFORE_SIZE}${NC}"
echo -e "Directory size after:  ${GREEN}${AFTER_SIZE}${NC}"
echo
echo -e "Items removed: ${GREEN}${REMOVED_COUNT}${NC}"
echo -e "Items skipped: ${BLUE}${SKIPPED_COUNT}${NC}"
echo

# Reminder about what's preserved
echo -e "${BLUE}Preserved:${NC}"
echo -e "  ✓ Model files (*.gguf)"
echo -e "  ✓ Source code and scripts"
echo -e "  ✓ Configuration files"
echo -e "  ✓ Documentation"
echo -e "  ✓ cmake-local (required - no system cmake)"
echo

# Check if model is still functional
if [ -f "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf" ] && [ -f "run_inference.py" ]; then
    echo -e "${GREEN}✓ BitNet setup appears intact and ready to use${NC}"
else
    echo -e "${RED}⚠️  Warning: Some required files may be missing${NC}"
fi