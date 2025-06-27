#!/usr/bin/env python3
"""
BitNet Real-time Chat
Optimized for smooth token-by-token display
"""
import subprocess
import os
import sys
import time
import re
import io
from datetime import datetime

class BitNetRealtimeChat:
    def __init__(self, model_path="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"):
        self.model_path = model_path
        self.conversation_history = []
        self.system_prompt = "You are a helpful AI assistant."
        self.temperature = 0.7
        self.max_tokens = 200
        
        # Using 10 threads for optimal performance
        os.environ['OMP_NUM_THREADS'] = '10'
        
    def print_header(self):
        """Print chat header"""
        print("\n" + "="*60)
        print("🤖 BitNet Real-time Chat")
        print("="*60)
        print(f"Model: {os.path.basename(self.model_path)}")
        print(f"Commands: /help /clear /exit")
        print("="*60 + "\n")
        
    def generate_streaming(self, prompt):
        """Generate response with character-by-character streaming"""
        # Build full prompt
        full_prompt = f"{self.system_prompt}\n\n"
        
        # Add conversation history
        for role, msg in self.conversation_history[-6:]:
            full_prompt += f"{role.capitalize()}: {msg}\n\n"
            
        full_prompt += f"User: {prompt}\n\nAssistant:"
        
        # Use run_inference.py but capture output in real-time
        cmd = [
            "python3", "-u", "run_inference.py",  # -u for unbuffered output
            "-m", self.model_path,
            "-p", full_prompt,
            "-n", str(self.max_tokens),
            "-temp", str(self.temperature),
            "-t", "10"  # Using 10 threads for optimal performance
        ]
        
        # Set up for real-time output capture
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered Python output
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            universal_newlines=True,
            bufsize=0,  # Unbuffered
            env=env
        )
        
        # Process output
        response = ""
        in_response = False
        last_word = ""
        word_buffer = ""
        start_time = time.time()
        
        print("🤖 BitNet: ", end='', flush=True)
        
        try:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                    
                # Check if we've hit the assistant marker
                if "Assistant:" in line and not in_response:
                    in_response = True
                    # Extract text after "Assistant:"
                    parts = line.split("Assistant:", 1)
                    if len(parts) > 1:
                        line = parts[1]
                
                if in_response:
                    # Check for technical markers that end response
                    tech_markers = ["build:", "main:", "llama_", "llm_", "warning:", "ggml_"]
                    should_stop = False
                    
                    for marker in tech_markers:
                        if marker in line:
                            # Get text before marker
                            line = line.split(marker)[0]
                            should_stop = True
                            break
                    
                    # Clean and print line
                    clean_line = ''.join(c for c in line if c.isprintable() or c in '\n\t ')
                    
                    # Simulate typing effect - print char by char
                    for char in clean_line:
                        print(char, end='', flush=True)
                        response += char
                        time.sleep(0.01)  # Adjust for typing speed
                    
                    if should_stop:
                        break
                        
        except KeyboardInterrupt:
            process.terminate()
            print("\n⚠️  Generation interrupted!")
            return None
            
        process.wait()
        generation_time = time.time() - start_time
        
        # Extract performance metrics if available
        # (Would need to capture stderr separately for this)
        
        print(f"\n\n📊 [Generated in {generation_time:.1f}s]")
        
        return response.strip()
        
    def run(self):
        """Main chat loop"""
        self.print_header()
        
        while True:
            try:
                # Get input
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith('/'):
                    command = user_input.split()[0].lower()
                    
                    if command == '/exit':
                        print("\n👋 Goodbye!")
                        break
                    elif command == '/clear':
                        self.conversation_history = []
                        self.print_header()
                        print("🗑️  History cleared!")
                    elif command == '/help':
                        print("\nCommands:")
                        print("  /clear - Clear chat history")
                        print("  /exit  - Exit chat")
                        print("\nTips:")
                        print("  - Text appears as it's generated")
                        print("  - Press Ctrl+C to interrupt generation")
                    else:
                        print(f"❌ Unknown command: {command}")
                    continue
                
                # Generate response
                response = self.generate_streaming(user_input)
                
                if response:
                    # Add to history
                    self.conversation_history.append(("user", user_input))
                    self.conversation_history.append(("assistant", response))
                    
                    # Limit history
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                        
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

# Simple launcher script content
LAUNCHER_SCRIPT = '''#!/bin/bash
# BitNet Real-time Chat Launcher

echo "🚀 Starting BitNet Real-time Chat..."
echo ""

# Set thread optimization
export OMP_NUM_THREADS=12
export PYTHONUNBUFFERED=1

# Run the chat
python3 chat_realtime.py
'''

def main():
    """Main entry point"""
    # Check model
    model_path = "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
    if not os.path.exists(model_path):
        print("❌ Model not found!")
        print(f"Expected: {model_path}")
        sys.exit(1)
        
    # Create launcher if it doesn't exist
    launcher_path = "bitnet-realtime.sh"
    if not os.path.exists(launcher_path):
        with open(launcher_path, 'w') as f:
            f.write(LAUNCHER_SCRIPT)
        os.chmod(launcher_path, 0o755)
        print(f"✅ Created launcher: {launcher_path}")
        
    # Run chat
    chat = BitNetRealtimeChat(model_path)
    chat.run()

if __name__ == "__main__":
    main()