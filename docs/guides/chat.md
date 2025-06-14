# BitNet Chat Interface

This directory contains interactive chat interfaces for the BitNet B1.58 2B4T model.

## Quick Start

```bash
# Simple method - use the launcher script
./bitnet-chat.sh

# Or run directly
python3 chat.py

# For advanced features
python3 chat_advanced.py
```

## Available Chat Interfaces

### 1. Basic Chat (`chat.py`)
Simple and straightforward chat interface with essential features:
- Interactive conversation
- System prompt customization
- Conversation history
- Save conversations
- Performance metrics

**Commands:**
- `/help` - Show help
- `/clear` - Clear conversation history
- `/system` - Change system prompt
- `/save` - Save conversation to file
- `/exit` - Exit chat

### 2. Advanced Chat (`chat_advanced.py`)
Feature-rich interface with additional capabilities:
- All basic features plus:
- Adjustable generation parameters (temperature, max_tokens, etc.)
- Export conversations in JSON or Markdown
- Better formatting and line wrapping
- Performance analytics
- Quick parameter adjustments

**Additional Commands:**
- `/settings` - View and modify all settings
- `/export` - Export in json or markdown format
- `/temp <value>` - Quick temperature adjustment
- `/tokens <n>` - Quick max tokens adjustment

### 3. Launcher Script (`bitnet-chat.sh`)
Convenient bash script that:
- Sets optimal thread count automatically
- Checks for required files
- Provides system information
- Launches the basic chat interface

## Performance Tips

1. **Thread Optimization**: The scripts automatically set `OMP_NUM_THREADS=12` for optimal performance on 12-core CPUs.

2. **Temperature Settings**:
   - Low (0.1-0.3): More deterministic, fact-based responses
   - Medium (0.4-0.7): Balanced creativity and coherence
   - High (0.8-1.0): More creative but potentially less coherent

3. **Token Limits**:
   - Short responses: 50-100 tokens
   - Medium responses: 100-200 tokens
   - Long responses: 200-500 tokens

## Example Usage

```bash
# Start a creative writing session
python3 chat_advanced.py
# Then: /temp 0.8
# Then: /tokens 300
# Then: /system You are a creative writing assistant

# Start a coding assistant
python3 chat.py
# Then: /system You are a helpful programming assistant
# Then: How do I implement a binary search in Python?

# Quick chat session
./bitnet-chat.sh
# Just start typing!
```

## Saved Conversations

- Basic chat saves to: `bitnet_chat_YYYYMMDD_HHMMSS.txt`
- Advanced chat saves to: `chat_logs/bitnet_chat_YYYYMMDD_HHMMSS.{json,md}`

## Troubleshooting

1. **Model not found**: Ensure you've run the setup process and the model is in `models/BitNet-b1.58-2B-4T/`

2. **Slow performance**: Check that thread count matches your CPU cores

3. **Out of memory**: Reduce max_tokens or close other applications

4. **Garbled output**: Try lowering temperature or clearing conversation history

## Requirements

- Python 3.7+
- BitNet model file (`ggml-model-i2_s.gguf`)
- Completed BitNet setup (built binaries)
- 12-core CPU (adjustable in settings)

## Performance Expectations

On a 12-core Intel CPU, expect:
- ~16-17 tokens/second generation speed
- <1 second latency for first token
- Smooth interactive experience