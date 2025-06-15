# bitnet.cpp
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![version](https://img.shields.io/badge/version-1.0-blue)

[<img src="./assets/header_model_release.png" alt="BitNet Model on Hugging Face" width="800"/>](https://huggingface.co/microsoft/BitNet-b1.58-2B-4T)

**The official inference framework for 1-bit LLMs** - Run powerful language models on your CPU with unprecedented efficiency.

## 🚀 Quick Start

Try it out via this [demo](https://bitnet-demo.azurewebsites.net/), or build and run it on your own [CPU](#build-from-source) or [GPU](https://github.com/microsoft/BitNet/blob/main/gpu/README.md).

```bash
# Quick setup and run
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet
pip install -r requirements.txt
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
python python/benchmarks/run_inference.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf -p "You are a helpful assistant" -cnv
```

## 📖 Overview

bitnet.cpp is the official inference framework for 1-bit LLMs (e.g., BitNet b1.58). It offers a suite of optimized kernels, that support **fast** and **lossless** inference of 1.58-bit models on CPU and GPU (NPU support coming next).

### Key Performance Metrics

| Platform | Speedup | Energy Reduction |
|----------|---------|------------------|
| ARM CPUs | 1.37x - 5.07x | 55.4% - 70.0% |
| x86 CPUs | 2.37x - 6.17x | 71.9% - 82.2% |

bitnet.cpp can run a 100B BitNet b1.58 model on a single CPU, achieving speeds comparable to human reading (5-7 tokens per second). See the [technical report](https://arxiv.org/abs/2410.16144) for details.

### 🎯 Hardware-Specific Optimization

BitNet now includes **kernel tuning** for automatic hardware optimization. Achieve 20-30% additional performance gains:

```bash
# Quick kernel tuning (5 minutes)
python utils/kernel_tuning.py --quick
```

See [docs/kernel_tuning.md](docs/kernel_tuning.md) for details.

<details>
<summary>📊 Performance Benchmarks</summary>

<img src="./assets/m2_performance.jpg" alt="m2_performance" width="800"/>
<img src="./assets/intel_performance.jpg" alt="intel_performance" width="800"/>

>The tested models are dummy setups used in a research context to demonstrate the inference performance of bitnet.cpp.
</details>

## 🎥 Demo

A demo of bitnet.cpp running a BitNet b1.58 3B model on Apple M2:

https://github.com/user-attachments/assets/7f46b736-edec-4828-b809-4be780a3e5b1

## 📰 What's New
- 06/15/2025 [Hardware-Specific Kernel Tuning](docs/kernel_tuning.md) - Achieve 20-30% performance gains ![NEW](https://img.shields.io/badge/NEW-red)
- 05/20/2025 [BitNet Official GPU inference kernel](https://github.com/microsoft/BitNet/blob/main/gpu/README.md)
- 04/14/2025 [BitNet Official 2B Parameter Model on Hugging Face](https://huggingface.co/microsoft/BitNet-b1.58-2B-4T)
- 02/18/2025 [Bitnet.cpp: Efficient Edge Inference for Ternary LLMs](https://arxiv.org/abs/2502.11880)
- 11/08/2024 [BitNet a4.8: 4-bit Activations for 1-bit LLMs](https://arxiv.org/abs/2411.04965)
- 10/21/2024 [1-bit AI Infra: Part 1.1, Fast and Lossless BitNet b1.58 Inference on CPUs](https://arxiv.org/abs/2410.16144)
<details>
<summary>View more updates</summary>

- 10/17/2024 bitnet.cpp 1.0 released.
- 03/21/2024 [The-Era-of-1-bit-LLMs__Training_Tips_Code_FAQ](https://github.com/microsoft/unilm/blob/master/bitnet/The-Era-of-1-bit-LLMs__Training_Tips_Code_FAQ.pdf)
- 02/27/2024 [The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits](https://arxiv.org/abs/2402.17764)
- 10/17/2023 [BitNet: Scaling 1-bit Transformers for Large Language Models](https://arxiv.org/abs/2310.11453)
</details>

## 🤖 Models

### Official Models
<table>
    </tr>
    <tr>
        <th rowspan="2">Model</th>
        <th rowspan="2">Parameters</th>
        <th rowspan="2">CPU</th>
        <th colspan="3">Kernel</th>
    </tr>
    <tr>
        <th>I2_S</th>
        <th>TL1</th>
        <th>TL2</th>
    </tr>
    <tr>
        <td rowspan="2"><a href="https://huggingface.co/microsoft/BitNet-b1.58-2B-4T">BitNet-b1.58-2B-4T</a></td>
        <td rowspan="2">2.4B</td>
        <td>x86</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
    </tr>
    <tr>
        <td>ARM</td>
        <td>&#9989;</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
    </tr>
</table>

### Community Models
> 💡 **Note**: We use existing 1-bit LLMs available on [Hugging Face](https://huggingface.co/) to demonstrate the inference capabilities of bitnet.cpp. We hope the release of bitnet.cpp will inspire the development of 1-bit LLMs in large-scale settings.

<table>
    </tr>
    <tr>
        <th rowspan="2">Model</th>
        <th rowspan="2">Parameters</th>
        <th rowspan="2">CPU</th>
        <th colspan="3">Kernel</th>
    </tr>
    <tr>
        <th>I2_S</th>
        <th>TL1</th>
        <th>TL2</th>
    </tr>
    <tr>
        <td rowspan="2"><a href="https://huggingface.co/1bitLLM/bitnet_b1_58-large">bitnet_b1_58-large</a></td>
        <td rowspan="2">0.7B</td>
        <td>x86</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
    </tr>
    <tr>
        <td>ARM</td>
        <td>&#9989;</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
    </tr>
    <tr>
        <td rowspan="2"><a href="https://huggingface.co/1bitLLM/bitnet_b1_58-3B">bitnet_b1_58-3B</a></td>
        <td rowspan="2">3.3B</td>
        <td>x86</td>
        <td>&#10060;</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
    </tr>
    <tr>
        <td>ARM</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
    </tr>
    <tr>
        <td rowspan="2"><a href="https://huggingface.co/HF1BitLLM/Llama3-8B-1.58-100B-tokens">Llama3-8B-1.58-100B-tokens</a></td>
        <td rowspan="2">8.0B</td>
        <td>x86</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
    </tr>
    <tr>
        <td>ARM</td>
        <td>&#9989;</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
    </tr>
    <tr>
        <td rowspan="2"><a href="https://huggingface.co/collections/tiiuae/falcon3-67605ae03578be86e4e87026">Falcon3 Family</a></td>
        <td rowspan="2">1B-10B</td>
        <td>x86</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
    </tr>
    <tr>
        <td>ARM</td>
        <td>&#9989;</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
    </tr>
    <tr>
        <td rowspan="2"><a href="https://huggingface.co/collections/tiiuae/falcon-edge-series-6804fd13344d6d8a8fa71130">Falcon-E Family</a></td>
        <td rowspan="2">1B-3B</td>
        <td>x86</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
        <td>&#9989;</td>
    </tr>
    <tr>
        <td>ARM</td>
        <td>&#9989;</td>
        <td>&#9989;</td>
        <td>&#10060;</td>
    </tr>
</table>

## 📦 Installation

### System Requirements
- python>=3.9
- cmake>=3.22
- clang>=18
- conda (highly recommended)

<details>
<summary>📋 Platform-specific installation</summary>

**Windows:**
Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) with these components:
- Desktop-development with C++
- C++-CMake Tools for Windows
- Git for Windows
- C++-Clang Compiler for Windows
- MS-Build Support for LLVM-Toolset (clang)

**Linux (Debian/Ubuntu):**
```bash
bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)"
```
</details>

### Build from Source

> [!IMPORTANT]
> Windows users: Always use Developer Command Prompt / PowerShell for VS2022. See [FAQ](#faq) for troubleshooting.

#### 1️⃣ Clone the repository
```bash
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet
```

#### 2️⃣ Set up environment
```bash
# Create conda environment (recommended)
conda create -n bitnet-cpp python=3.9
conda activate bitnet-cpp

# Install dependencies
pip install -r requirements.txt
```

#### 3️⃣ Download model and build
```bash
# Download the official model
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

# Build with optimized kernel
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
```
<details>
<summary>Setup options</summary>

| Option | Description |
|--------|-------------|
| `--hf-repo`, `-hr` | Download model directly from Hugging Face |
| `--model-dir`, `-md` | Local directory containing the model |
| `--quant-type`, `-q` | Quantization type: `i2_s` (recommended) or `tl1` |
| `--use-pretuned`, `-p` | Use pre-optimized kernel parameters |
</details>
## 🔧 Usage

### Basic Inference
```bash
# Run chat mode with the official model
python python/benchmarks/run_inference.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf -p "You are a helpful assistant" -cnv
```

### Quick Chat Interface
```bash
# Use the convenience script for optimized chat
./bitnet-chat.sh
```

### Inference Options

| Option | Description | Default |
|--------|-------------|---------|
| `-m`, `--model` | Path to model file | Required |
| `-p`, `--prompt` | System prompt or direct prompt | Required |
| `-n`, `--n-predict` | Number of tokens to generate | 128 |
| `-t`, `--threads` | Number of CPU threads | Auto |
| `-cnv`, `--conversation` | Enable chat mode | False |
| `-temp`, `--temperature` | Generation randomness (0.0-1.0) | 0.7 |

### Performance Benchmarking

Run end-to-end benchmarks to measure performance:

```bash
# Benchmark with specific parameters
python utils/e2e_benchmark.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf -n 200 -p 512 -t 4
```

**Benchmark Options:**
- `-m`: Model file path (required)
- `-n`: Tokens to generate (default: 128)
- `-p`: Prompt length (default: 512)
- `-t`: Thread count (default: 2)

#### Testing Custom Model Configurations

Generate dummy models for testing different architectures:

```bash
# Generate a 125M parameter test model
python utils/generate-dummy-bitnet-model.py models/bitnet_b1_58-large \
    --outfile models/dummy-bitnet-125m.tl1.gguf \
    --outtype tl1 \
    --model-size 125M

# Benchmark the test model
python utils/e2e_benchmark.py -m models/dummy-bitnet-125m.tl1.gguf -p 512 -n 128
```

### Model Conversion

Convert models from different formats:

```bash
# Convert from safetensors format
huggingface-cli download microsoft/bitnet-b1.58-2B-4T-bf16 --local-dir ./models/bitnet-b1.58-2B-4T-bf16
python ./python/converters/convert-helper-bitnet.py ./models/bitnet-b1.58-2B-4T-bf16
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Setup Guide](SETUP_GUIDE.md) | Detailed installation and configuration |
| [Kernel Tuning](docs/kernel_tuning.md) | Hardware-specific optimization guide |
| [Project Structure](PROJECT_STRUCTURE.md) | Repository organization |
| [Performance Analysis](PERFORMANCE_COMPARISON.md) | Detailed benchmarks and comparisons |
| [BitNet Capabilities](BITNET_CAPABILITIES.md) | Use cases and deployment scenarios |
| [API Documentation](docs/README.md) | Programming interfaces |
| [GPU Support](gpu/README.md) | GPU inference setup |

## 🔬 Implementation Details

### BitNet b1.58 Architecture

This repository provides an optimized implementation of **BitNet b1.58**, specifically targeting the **2B4T model** (2.4B parameters trained on 4 trillion tokens). BitNet b1.58 represents each weight as a ternary value {-1, 0, +1}, achieving extreme quantization while maintaining competitive performance with full-precision models.

### Implementation Method

Our implementation uses several key techniques:

1. **Ternary Weight Encoding**: Weights are packed into 2-bit representations using the I2_S quantization format
   - Each weight uses only 2 bits: `00` (-1), `01` (0), `10` (+1)
   - 128-bit block quantization with per-block scaling factors

2. **Optimized Kernels**: Platform-specific SIMD implementations
   - **TL1 (ARM)**: NEON intrinsics with lookup table (LUT) based computation
   - **TL2 (x86)**: AVX2/AVX-VNNI intrinsics with multiply-accumulate (MAD) operations
   - Tiled matrix multiplication with configurable block sizes (BM, BK, bm)

3. **Hardware-Specific Optimization**: The kernel tuning system (new in this release) automatically finds optimal tiling parameters for your CPU, achieving 20-30% performance gains over generic configurations.

### Model Specifications

The BitNet b1.58 2B4T model features:
- **Architecture**: Transformer-based with BitLinear layers
- **Parameters**: 2.41B (2.4B active)
- **Quantization**: 1.58-bit weights (ternary), 8-bit activations
- **Context Length**: 4,096 tokens
- **Vocabulary**: 128,256 tokens
- **Training Data**: 4 trillion tokens

### Performance Characteristics

On modern CPUs, this implementation achieves:
- **Inference Speed**: 15-25 tokens/second (varies by CPU)
- **Memory Usage**: ~1.1GB (3.91 bits per weight including overhead)
- **Energy Efficiency**: 55-82% reduction compared to FP16 models

## 🙏 Acknowledgements

This project is based on the [llama.cpp](https://github.com/ggerganov/llama.cpp) framework. We thank all the authors for their contributions to the open-source community. 

bitnet.cpp's kernels are built on top of the Lookup Table methodologies pioneered in [T-MAC](https://github.com/microsoft/T-MAC/). For inference of general low-bit LLMs beyond ternary models, we recommend using T-MAC.

## ❓ FAQ

<details>
<summary><b>Q: Build fails with std::chrono errors in log.cpp?</b></summary>

This is a known issue in recent llama.cpp versions. Apply this [fix](https://github.com/tinglou/llama.cpp/commit/4e3db1e3d78cc1bcd22bcb3af54bd2a4628dd323) from the [discussion](https://github.com/abetlen/llama-cpp-python/issues/1942).
</details>

<details>
<summary><b>Q: How to build with clang in conda on Windows?</b></summary>

1. First verify clang installation:
```bash
clang -v
```

2. If clang is not recognized, initialize VS tools:

**Command Prompt:**
```cmd
"C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\VsDevCmd.bat" -startdir=none -arch=x64 -host_arch=x64
```

**PowerShell:**
```powershell
Import-Module "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\Microsoft.VisualStudio.DevShell.dll"
Enter-VsDevShell 3f0e31ad -SkipAutomaticLocation -DevCmdArguments "-arch=x64 -host_arch=x64"
```
</details>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md) before contributing.

## 📬 Contact

For questions and support, please open an issue on our [GitHub repository](https://github.com/microsoft/BitNet/issues).
