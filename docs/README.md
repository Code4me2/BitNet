# BitNet Documentation

Welcome to the BitNet inference server documentation. This guide will help you get started with BitNet and make the most of its capabilities.

## 📚 Documentation Structure

### Getting Started
- [Installation Guide](./getting-started/installation.md) - Step-by-step installation instructions
- [Setup Guide](./getting-started/setup-guide.md) - Detailed setup with model downloads
- [Docker Setup](./getting-started/docker-status.md) - Docker configuration and current status

### User Guides
- [Chat Interface](./guides/chat.md) - Interactive chat functionality
- [Streaming Chat](./guides/streaming_chat.md) - Real-time streaming responses
- [Threading Guide](./guides/threading-guide.md) - CPU utilization and parallel processing

### Performance
- [BitNet Capabilities](./performance/capabilities.md) - Where BitNet excels
- [Performance Comparison](./performance/comparison.md) - BitNet vs other models
- [Optimization Guide](./performance/optimization.md) - Performance tuning
- [Kernel Tuning](./performance/kernel_tuning.md) - Hardware-specific optimizations

### Architecture
- [Project Structure](./architecture/project-structure.md) - Repository organization
- [Cleanup Summary](./architecture/cleanup_summary.md) - Code organization details

### Development
- [Testing Guide](./development/testing.md) - Testing implementation
- [Code Generation](./development/codegen.md) - Kernel code generation

### Migration
- [BitNet.cpp Migration](./migration/bitnet-cpp-migration.md) - Migration history and guide

## 🚀 Quick Links

- **Quick Start**: See the main [README](../README.md) for quick start instructions
- **API Reference**: Check the setup guide for API endpoint documentation
- **Troubleshooting**: See the installation guide for common issues

## 🔧 Key Features

- **1-bit Quantization**: Extreme efficiency with minimal quality loss
- **Optimized Kernels**: Hardware-specific kernels (I2_S, TL1, TL2)
- **OpenAI-Compatible API**: Drop-in replacement for many applications
- **Parallel Processing**: Efficient multi-prompt handling

## 📊 Performance Highlights

- **Speed**: 1.37x - 6.17x faster than llama.cpp
- **Memory**: ~70% reduction in memory usage
- **Energy**: Significant power consumption reduction
- **Quality**: Comparable to full-precision models for many tasks

## 🤝 Contributing

See the [Contributing Guide](../../CONTRIBUTING.md) for information on how to contribute to the project.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.