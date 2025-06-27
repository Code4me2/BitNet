# BitNet Project Structure

This document describes the organization of the BitNet project after restructuring for improved maintainability.

## Directory Structure

```
BitNet/
├── 3rdparty/              # External dependencies
│   └── llama.cpp/         # Base framework for LLM inference
│
├── build/                 # Build output (organized by configuration)
│   ├── bin/              # Executable files
│   │   ├── Debug/        # Debug build executables
│   │   └── Release/      # Release build executables
│   └── lib/              # Library files
│       ├── Debug/        # Debug build libraries
│       └── Release/      # Release build libraries
│
├── docs/                  # Documentation (organized by topic)
│   ├── README.md         # Documentation index
│   ├── guides/           # User guides
│   │   ├── chat.md
│   │   ├── streaming_chat.md
│   │   └── threading.md
│   ├── architecture/     # Architecture documentation
│   │   ├── cleanup_summary.md
│   │   └── threading_summary.md
│   ├── optimization/     # Performance optimization docs
│   │   └── optimization_guide.md
│   └── codegen.md       # Code generation documentation
│
├── gpu/                  # GPU-specific implementation
│   ├── bitnet_kernels/   # CUDA kernel implementations
│   └── *.py             # GPU-related Python scripts
│
├── include/              # C++ header files
│   ├── bitnet-lut-kernels.h
│   ├── ggml-bitnet.h
│   └── kernel_config.ini
│
├── models/               # Model files (.gguf format)
│
├── preset_kernels/       # Pre-generated optimized kernels
│
├── python/               # Python scripts (organized by function)
│   ├── chat/            # Chat interface scripts
│   │   ├── chat.py
│   │   ├── chat_advanced.py
│   │   ├── chat_realtime.py
│   │   └── chat_streaming.py
│   ├── benchmarks/      # Benchmarking and inference scripts
│   │   ├── benchmark.py
│   │   ├── benchmark_optimized.py
│   │   ├── run_inference.py
│   │   └── parallel_inference.py
│   └── converters/      # Model conversion utilities (TBD)
│
├── src/                  # C++ source files
│   ├── ggml-bitnet-lut.cpp
│   └── ggml-bitnet-mad.cpp
│
├── tests/                # Test files
│   ├── test_model_loading.py
│   ├── test_optimizations.py
│   ├── test_output_quality.py
│   ├── test_performance.py
│   ├── monitor_threads.py
│   ├── thread_demo.py
│   └── run_tests.sh
│
├── utils/                # Utility scripts
│   ├── codegen_tl1.py   # TL1 kernel code generation
│   ├── codegen_tl2.py   # TL2 kernel code generation
│   ├── convert*.py      # Various model converters
│   └── e2e_benchmark.py # End-to-end benchmarking
│
├── CMakeLists.txt       # Main CMake configuration
├── README.md            # Project overview
├── requirements.txt     # Python dependencies
└── setup_env.py         # Environment setup script
```

## Key Changes from Original Structure

1. **Python Scripts Organization**
   - Chat scripts moved to `python/chat/`
   - Benchmark and inference scripts moved to `python/benchmarks/`
   - Converters will be moved to `python/converters/` (pending)

2. **Test Organization**
   - All test files consolidated in `tests/` directory
   - Includes both Python tests and shell scripts

3. **Documentation Structure**
   - Organized by topic: guides, architecture, optimization
   - Central README.md in docs/ for navigation

4. **Build Output**
   - Separate directories for binaries (`bin/`) and libraries (`lib/`)
   - Configuration-specific subdirectories (Debug/Release)

## Usage Examples

### Running Chat Interface
```bash
# Old way
python chat.py

# New way
python python/chat/chat.py
# or use the provided script
./bitnet-chat.sh
```

### Running Inference
```bash
# Old way
python run_inference.py -m model.gguf -p "prompt"

# New way
python python/benchmarks/run_inference.py -m model.gguf -p "prompt"
```

### Running Tests
```bash
# Old way
python test_performance.py

# New way
python tests/test_performance.py
# or run all tests
cd tests && ./run_tests.sh
```

## Benefits of New Structure

1. **Better Organization** - Related files are grouped together
2. **Easier Navigation** - Clear separation between different components
3. **Scalability** - Easy to add new modules without cluttering root
4. **Build Management** - Organized output directories for different configurations
5. **Documentation** - Topic-based organization makes finding information easier