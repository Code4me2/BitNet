# BitNet Streaming Chat Interfaces

This directory now contains several chat interfaces with different streaming capabilities:

## Available Chat Modes

### 1. **Standard Chat** (`chat.py`, `chat_advanced.py`)
- Shows full response after generation completes
- More stable and reliable
- Good for testing and basic usage

### 2. **Streaming Chat V1** (`chat_streaming.py`)
- Attempts to show tokens as they're generated
- Reads output character-by-character from llama-cli
- More complex but provides real-time feedback

### 3. **Streaming Chat V2** (`chat_streaming_v2.py`)
- Enhanced version with better buffering
- Uses non-blocking I/O for smoother streaming
- Linux/macOS optimized (limited on Windows)

### 4. **Real-time Chat** (`chat_realtime.py`)
- Simplified streaming approach
- Uses Python's subprocess with line buffering
- Simulates typing effect for natural feel
- Most compatible across platforms

## Quick Start

```bash
# For real-time token display (recommended)
python3 chat_realtime.py

# For advanced streaming (Linux/macOS)
python3 chat_streaming_v2.py

# For standard chat without streaming
./bitnet-chat.sh
```

## Technical Details

### Why Streaming is Challenging

1. **Output Buffering**: The llama-cli binary buffers output, making real-time capture difficult
2. **Process Communication**: Python's subprocess module has limitations for real-time I/O
3. **Text Encoding**: UTF-8 encoding issues with partial token bytes
4. **Platform Differences**: Windows handles process I/O differently than Unix systems

### Our Solutions

1. **Direct Binary Calls**: Bypass run_inference.py wrapper when possible
2. **Non-blocking I/O**: Use fcntl for Unix systems to read without blocking
3. **Character Buffering**: Handle partial UTF-8 sequences gracefully
4. **Simulated Streaming**: Add delays to create typing effect when true streaming isn't possible

## Performance Considerations

- True streaming may slightly reduce overall tokens/second
- Character-by-character display adds visual latency
- Best performance still comes from batch generation

## Troubleshooting

### "No streaming visible"
- Try `chat_realtime.py` which simulates streaming
- Ensure PYTHONUNBUFFERED=1 is set
- Check if output is being buffered by terminal

### "Garbled characters"
- UTF-8 encoding issues - the scripts now handle this
- Try the standard chat interfaces instead

### "Slow typing effect"
- Adjust the sleep delay in the streaming scripts
- Set to 0 for instant display

## Future Improvements

1. **Native Streaming API**: Modify llama.cpp to support true streaming
2. **WebSocket Interface**: Build a web UI with proper streaming support
3. **Async I/O**: Use Python's asyncio for better performance

## Recommendation

For the best experience:
- Use `chat_realtime.py` for a good balance of features and compatibility
- Use `chat_advanced.py` if streaming isn't critical
- Experiment with different interfaces to find what works best for your system