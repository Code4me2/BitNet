#!/usr/bin/env python3
"""
BitNet Chat with Enhanced Streaming
Uses direct llama-cli interaction for real-time token display
"""
import subprocess
import os
import sys
import select
import fcntl
import termios
import tty
import time
import re
from datetime import datetime
from pathlib import Path

class BitNetStreamingChatV2:
    def __init__(self, model_path="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"):
        self.model_path = model_path
        self.conversation_history = []
        self.system_prompt = "You are a helpful AI assistant."
        self.temperature = 0.7
        self.max_tokens = 200
        
        # Set environment
        # Using 10 threads for optimal performance
        os.environ['OMP_NUM_THREADS'] = '10'
        
        # Determine llama-cli path
        if os.name == 'nt':
            self.llama_cli = "build/bin/Release/llama-cli.exe"
            if not os.path.exists(self.llama_cli):
                self.llama_cli = "build/bin/llama-cli.exe"
        else:
            self.llama_cli = "build/bin/llama-cli"
            
        Path("chat_logs").mkdir(exist_ok=True)
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def print_header(self):
        """Print header"""
        self.clear_screen()
        print("=" * 60)
        print("🤖 BitNet B1.58 2B4T - Streaming Chat")
        print("=" * 60)
        print(f"Model: {os.path.basename(self.model_path)}")
        print(f"Temperature: {self.temperature} | Max Tokens: {self.max_tokens}")
        print("-" * 60)
        print("Commands: /help /clear /temp <n> /tokens <n> /exit")
        print("=" * 60)
        print()
        
    def build_prompt(self, user_input):
        """Build the full prompt with context"""
        # Start with system prompt
        prompt = self.system_prompt + "\n\n"
        
        # Add recent conversation history (last 3 exchanges)
        history_to_include = self.conversation_history[-6:]
        
        for role, message in history_to_include:
            if role == "user":
                prompt += f"User: {message}\n\n"
            else:
                prompt += f"Assistant: {message}\n\n"
                
        # Add current input
        prompt += f"User: {user_input}\n\nAssistant:"
        
        return prompt
        
    def stream_response(self, user_input):
        """Stream response from llama-cli with real-time output"""
        full_prompt = self.build_prompt(user_input)
        
        # Build command
        cmd = [
            self.llama_cli,
            "-m", self.model_path,
            "-p", full_prompt,
            "-n", str(self.max_tokens),
            "--temp", str(self.temperature),
            "-t", "10",  # Using 10 threads for optimal performance
            "--top-k", "40",
            "--top-p", "0.95",
            "--repeat-penalty", "1.1",
            "-ngl", "0",
            "-c", "2048",
            "-b", "1",
            "--no-display-prompt"  # Don't display the prompt again
        ]
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=False  # Get bytes for better control
        )
        
        # Set stdout to non-blocking
        fd = process.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        response_text = ""
        response_started = False
        buffer = b""
        start_time = time.time()
        token_count = 0
        
        print("🤖 BitNet: ", end='', flush=True)
        
        try:
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    break
                    
                # Try to read data
                try:
                    chunk = process.stdout.read(1024)
                    if chunk:
                        buffer += chunk
                        
                        # Try to decode what we have
                        try:
                            text = buffer.decode('utf-8', errors='ignore')
                            buffer = b""  # Clear buffer after successful decode
                            
                            # Process the text
                            if not response_started and "Assistant:" in text:
                                # Find where assistant response starts
                                parts = text.split("Assistant:")
                                if len(parts) > 1:
                                    text = parts[-1]
                                    response_started = True
                            
                            if response_started:
                                # Clean up technical markers
                                for marker in ["llama_", "llm_", "ggml_", "build:", "main:"]:
                                    if marker in text:
                                        text = text.split(marker)[0]
                                        break
                                
                                # Print the text character by character for streaming effect
                                for char in text:
                                    if char.isprintable() or char in '\n\t':
                                        print(char, end='', flush=True)
                                        response_text += char
                                        if char in ' \n\t':
                                            token_count += 1
                                        time.sleep(0.001)  # Small delay for visual effect
                                        
                        except UnicodeDecodeError:
                            # Keep accumulating in buffer
                            pass
                            
                except IOError:
                    # No data available, wait a bit
                    time.sleep(0.01)
                    
        except KeyboardInterrupt:
            process.terminate()
            print("\n\n⚠️  Generation interrupted!")
            return None, 0
            
        # Clean up
        process.wait()
        generation_time = time.time() - start_time
        
        # Get performance info from stderr
        stderr_output = process.stderr.read().decode('utf-8', errors='ignore')
        tokens_per_sec = 0
        match = re.search(r'(\d+\.?\d*)\s*tokens per second', stderr_output)
        if match:
            tokens_per_sec = float(match.group(1))
            
        # Clean response
        response_text = response_text.strip()
        response_text = ''.join(c for c in response_text if c.isprintable() or c in '\n\t')
        
        # Show stats
        if tokens_per_sec > 0:
            print(f"\n\n📊 [{token_count} tokens, {generation_time:.1f}s, {tokens_per_sec:.1f} tok/s]")
        
        return response_text, tokens_per_sec
        
    def run(self):
        """Main chat loop"""
        self.print_header()
        
        while True:
            try:
                # Get user input
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if command == '/exit':
                        print("\n👋 Goodbye!")
                        break
                    elif command == '/clear':
                        self.conversation_history = []
                        self.print_header()
                        print("🗑️  Conversation cleared!")
                    elif command == '/help':
                        print("\nCommands:")
                        print("  /clear    - Clear conversation history")
                        print("  /temp <n> - Set temperature (0.0-1.0)")
                        print("  /tokens <n> - Set max tokens")
                        print("  /exit     - Exit chat")
                    elif command == '/temp':
                        try:
                            self.temperature = float(args)
                            print(f"✅ Temperature set to {self.temperature}")
                        except:
                            print("❌ Invalid temperature")
                    elif command == '/tokens':
                        try:
                            self.max_tokens = int(args)
                            print(f"✅ Max tokens set to {self.max_tokens}")
                        except:
                            print("❌ Invalid token count")
                    else:
                        print(f"❌ Unknown command: {command}")
                    continue
                
                # Generate response
                response, tps = self.stream_response(user_input)
                
                if response:
                    # Add to history
                    self.conversation_history.append(("user", user_input))
                    self.conversation_history.append(("assistant", response))
                    
                    # Keep history manageable
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

def main():
    """Main entry point"""
    # Check requirements
    model_path = "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
    
    if not os.path.exists(model_path):
        print("❌ Model not found!")
        print(f"Expected: {model_path}")
        sys.exit(1)
        
    # Check for llama-cli
    if os.name == 'nt':
        llama_cli = "build/bin/Release/llama-cli.exe"
        if not os.path.exists(llama_cli):
            llama_cli = "build/bin/llama-cli.exe"
    else:
        llama_cli = "build/bin/llama-cli"
        
    if not os.path.exists(llama_cli):
        print("❌ llama-cli not found!")
        print(f"Expected: {llama_cli}")
        sys.exit(1)
        
    # Check if we're on Windows
    if os.name == 'nt':
        print("⚠️  Note: Streaming may be limited on Windows.")
        print("For best experience, use Linux or macOS.\n")
        
    # Run chat
    chat = BitNetStreamingChatV2(model_path)
    chat.run()

if __name__ == "__main__":
    main()